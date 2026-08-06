"""
Guitar Tutor Backend - FastAPI Gateway
Main entry point with REST API + WebSocket for real-time voice interaction.

Run with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
import uuid
import json
import base64
import asyncio
import logging
import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from config import TEMP_DIR, HOST, PORT, DEMUCS_PYTHON, WHISPER_PYTHON, MADMOM_PYTHON, PIPER_EXE
from orchestrator import run_pipeline, run_text_only_pipeline, cleanup_temp_files
from middleware.rate_limit import RateLimitMiddleware
from database.engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import get_ws_current_user
from middleware.rate_limit import RateLimitMiddleware
from auth.router import router as auth_router
from routers import sessions, users

# Add ffmpeg to PATH (WinGet install location)
_ffmpeg_dir = r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin"
if os.path.isdir(_ffmpeg_dir) and _ffmpeg_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ["PATH"]

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("guitar-tutor")

# ============================================================
# LIFESPAN (startup / shutdown)
# ============================================================
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup and shutdown logic."""
    # ── Startup ──
    logger.info("=" * 60)
    logger.info("  Guitar Tutor Backend Starting...")
    logger.info("=" * 60)

    checks = {
        "Demucs Python": os.path.isfile(DEMUCS_PYTHON),
        "Whisper Python": os.path.isfile(WHISPER_PYTHON),
        "Madmom Python": os.path.isfile(MADMOM_PYTHON),
        "Piper Binary": os.path.isfile(PIPER_EXE),
    }
    for name, exists in checks.items():
        logger.info(f"  {name}: {'OK' if exists else 'MISSING'}")

    try:
        from services.llm_client import check_llm_health
        lm_ok = await check_llm_health()
        logger.info(f"  LM Studio: {'OK' if lm_ok else 'NOT RUNNING'}")
    except Exception:
        logger.info("  LM Studio: NOT RUNNING")

    logger.info("=" * 60)
    logger.info(f"  API docs: http://localhost:{PORT}/docs")
    logger.info(f"  WebSocket: ws://localhost:{PORT}/ws/session")
    logger.info("=" * 60)

    yield  # ── App is running ──

    # ── Shutdown ──
    cleanup_temp_files()
    logger.info("Guitar Tutor Backend stopped.")


# ============================================================
# APP SETUP
# ============================================================
app = FastAPI(
    title="Guitar Tutor API",
    description="LLM-powered guitar tutor with voice interaction",
    version="1.0.0",
    lifespan=lifespan
)

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

app.include_router(auth_router)
app.include_router(sessions.router)
app.include_router(users.router, prefix="/api/users", tags=["users"])

# ============================================================
# HEALTH CHECK
# ============================================================
@app.get("/health")
async def health_check():
    """Check the status of all services."""
    services = {
        "gateway": True,
        "demucs_python": os.path.isfile(DEMUCS_PYTHON),
        "whisper_python": os.path.isfile(WHISPER_PYTHON),
        "madmom_python": os.path.isfile(MADMOM_PYTHON),
        "piper_binary": os.path.isfile(PIPER_EXE),
        "lm_studio": False
    }
    
    # Check LM Studio
    try:
        from services.llm_client import check_llm_health
        services["lm_studio"] = await check_llm_health()
    except Exception:
        pass
    
    all_healthy = all(services.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services,
        "timestamp": time.time()
    }


# ============================================================
# REST API ENDPOINTS
# ============================================================

@app.post("/api/pipeline")
async def full_pipeline(audio: UploadFile = File(...)):
    """
    Full processing pipeline:
    Upload audio → Separate → Transcribe + Chord detect → LLM → TTS
    
    Returns JSON with all results + audio response.
    """
    # Save uploaded audio to temp
    audio_id = uuid.uuid4().hex[:8]
    input_path = str(TEMP_DIR / f"input_{audio_id}.wav")
    
    try:
        content = await audio.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Received audio: {len(content)} bytes → {input_path}")
        
        # Run the full pipeline
        result = await run_pipeline(input_path)
        
        response = result.to_dict()
        
        # If TTS produced audio, include it as base64
        if result.audio_response_path and os.path.exists(result.audio_response_path):
            with open(result.audio_response_path, "rb") as f:
                response["audio_response_base64"] = base64.b64encode(f.read()).decode("utf-8")
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up input file
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass


@app.post("/api/separate")
async def separate_endpoint(audio: UploadFile = File(...)):
    """Upload audio → get separated stems."""
    audio_id = uuid.uuid4().hex[:8]
    input_path = str(TEMP_DIR / f"sep_{audio_id}.wav")
    
    try:
        content = await audio.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        from services.separator import separate_audio
        result = await separate_audio(input_path)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transcribe")
async def transcribe_endpoint(audio: UploadFile = File(...)):
    """Upload audio → get transcribed text."""
    audio_id = uuid.uuid4().hex[:8]
    input_path = str(TEMP_DIR / f"stt_{audio_id}.wav")
    
    try:
        content = await audio.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        from services.transcriber import transcribe_audio
        result = await transcribe_audio(input_path)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass


@app.post("/api/chords")
async def chords_endpoint(audio: UploadFile = File(...)):
    """Upload audio → get detected chords."""
    audio_id = uuid.uuid4().hex[:8]
    input_path = str(TEMP_DIR / f"chord_{audio_id}.wav")
    
    try:
        content = await audio.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        from services.chord_detector import detect_chords
        result = await detect_chords(input_path)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass


@app.post("/api/ask")
async def ask_endpoint(body: dict):
    """Send a text question to the LLM tutor."""
    text = body.get("text", "")
    chords = body.get("chords", None)
    
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        from services.llm_client import query_llm
        response = await query_llm(text, chords)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts")
async def tts_endpoint(body: dict):
    """Convert text to speech, return audio file."""
    text = body.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        from services.tts import synthesize_speech
        audio_path = await synthesize_speech(text)
        return FileResponse(
            audio_path,
            media_type="audio/wav",
            filename="response.wav"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# WEBSOCKET ENDPOINT (for Gemini-style voice UI)
# ============================================================

@app.websocket("/ws/session")
async def websocket_session(
    ws: WebSocket, 
    token: str = Query(None), 
    session_id: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time voice interaction.
    """
    try:
        user = await get_ws_current_user(token, db)
        user_id = user.id
    except Exception as e:
        await ws.accept()
        await ws.send_json({"type": "error", "message": "Authentication failed"})
        await ws.close()
        return

    await ws.accept()
    logger.info(f"WebSocket session started for user {user_id}, session {session_id}")
    
    audio_chunks: list[bytes] = []
    is_recording = False
    
    try:
        while True:
            message = await ws.receive()
            
            if "text" in message:
                # JSON command
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type", "")
                    
                    if msg_type == "start_recording":
                        audio_chunks = []
                        is_recording = True
                        await ws.send_json({"type": "status", "stage": "recording", "message": "Recording started"})
                        
                    elif msg_type == "stop_recording":
                        is_recording = False
                        await ws.send_json({"type": "status", "stage": "processing", "message": "Processing audio..."})
                        
                        if audio_chunks:
                            # Combine audio chunks and process
                            audio_data = b"".join(audio_chunks)
                            audio_chunks = []
                            await _process_audio_ws(ws, audio_data, user_id, session_id, db)
                        else:
                            await ws.send_json({"type": "error", "message": "No audio data received"})
                    
                    elif msg_type == "text_input":
                        text = data.get("text", "")
                        if text:
                            await _process_text_ws(ws, text, user_id, session_id, db)
                        else:
                            await ws.send_json({"type": "error", "message": "No text provided"})
                    
                except json.JSONDecodeError:
                    await ws.send_json({"type": "error", "message": "Invalid JSON"})
                    
            elif "bytes" in message:
                # Binary audio data
                if is_recording:
                    audio_chunks.append(message["bytes"])
                    
    except WebSocketDisconnect:
        logger.info("WebSocket session ended")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


async def _process_audio_ws(ws: WebSocket, audio_data: bytes, user_id: str, session_id: str, db: AsyncSession):
    """Process audio through the full pipeline and send results via WebSocket."""
    audio_id = uuid.uuid4().hex[:8]
    wav_path = str(TEMP_DIR / f"ws_{audio_id}.wav")
    temp_files = [wav_path]
    
    try:
        # Detect audio format from header bytes
        is_wav = audio_data[:4] == b"RIFF"
        is_webm = audio_data[:4] == b"\x1a\x45\xdf\xa3"
        
        logger.info(f"Received audio: {len(audio_data)} bytes, format={'WAV' if is_wav else 'WebM' if is_webm else 'unknown'}")
        
        if is_wav:
            # Already a proper WAV file — save directly, no conversion needed
            with open(wav_path, "wb") as f:
                f.write(audio_data)
            logger.info(f"Saved WAV directly: {wav_path} ({len(audio_data)} bytes)")
        elif is_webm:
            # WebM/Opus from MediaRecorder — needs ffmpeg conversion
            webm_path = str(TEMP_DIR / f"ws_{audio_id}.webm")
            temp_files.append(webm_path)
            with open(webm_path, "wb") as f:
                f.write(audio_data)
            
            import subprocess as sp
            conv = sp.run(
                ["ffmpeg", "-y", "-i", webm_path, "-ar", "16000", "-ac", "1", "-f", "wav", wav_path],
                capture_output=True, text=True, timeout=30
            )
            if conv.returncode != 0:
                logger.error(f"ffmpeg failed: {conv.stderr[-300:]}")
                raise RuntimeError(f"Audio conversion failed: {conv.stderr[-200:]}")
        else:
            # Unknown format — try saving as-is and hope ffmpeg can handle it
            raw_path = str(TEMP_DIR / f"ws_{audio_id}.raw")
            temp_files.append(raw_path)
            with open(raw_path, "wb") as f:
                f.write(audio_data)
            
            import subprocess as sp
            conv = sp.run(
                ["ffmpeg", "-y", "-i", raw_path, "-ar", "16000", "-ac", "1", "-f", "wav", wav_path],
                capture_output=True, text=True, timeout=30
            )
            if conv.returncode != 0:
                raise RuntimeError(f"Unsupported audio format (header: {audio_data[:8].hex()})")
        
        if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 100:
            raise RuntimeError("Audio file is too small or empty")
        
        input_path = wav_path
        
        # Define status callback for real-time updates
        async def on_status(stage: str, message: str):
            try:
                await ws.send_json({"type": "status", "stage": stage, "message": message})
            except Exception:
                pass
        
        # Run pipeline
        result = await run_pipeline(
            audio_path=input_path, 
            user_id=user_id, 
            session_id=session_id, 
            db=db, 
            on_status=on_status
        )
        
        # Send transcription
        if result.user_text:
            await ws.send_json({"type": "transcription", "text": result.user_text})
        
        # Send chord data
        if result.chords:
            await ws.send_json({
                "type": "chords",
                "data": result.chords,
                "unique_chords": result.unique_chords
            })
        
        # Send note data
        if result.notes:
            await ws.send_json({
                "type": "notes",
                "data": result.notes,
                "unique_notes": result.unique_notes
            })
        
        # Send strumming data
        if result.strumming:
            await ws.send_json({
                "type": "strumming",
                "data": result.strumming
            })
        
        # Send LLM response text
        if result.llm_response:
            await ws.send_json({"type": "response", "text": result.llm_response})
        
        # Send audio response as base64
        if result.audio_response_path and os.path.exists(result.audio_response_path):
            with open(result.audio_response_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
            await ws.send_json({"type": "audio", "format": "wav", "data": audio_b64})
        
        # Send errors if any
        if result.errors:
            await ws.send_json({"type": "errors", "messages": result.errors})
        
        # Final complete status
        await ws.send_json({
            "type": "complete",
            "total_time": result.total_time,
            "stages_completed": result.stages_completed
        })
        
    except Exception as e:
        await ws.send_json({"type": "error", "message": str(e)})
    finally:
        for path in temp_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


async def _process_text_ws(ws: WebSocket, text: str, user_id: str, session_id: str, db: AsyncSession):
    """Process text-only input through LLM + TTS and send via WebSocket."""
    try:
        result = await run_text_only_pipeline(
            text=text, 
            user_id=user_id, 
            session_id=session_id, 
            db=db
        )
        
        await ws.send_json({"type": "transcription", "text": text})
        
        if result.llm_response:
            await ws.send_json({"type": "response", "text": result.llm_response})
        
        if result.audio_response_path and os.path.exists(result.audio_response_path):
            with open(result.audio_response_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
            await ws.send_json({"type": "audio", "format": "wav", "data": audio_b64})
        
        await ws.send_json({
            "type": "complete",
            "total_time": result.total_time,
            "stages_completed": result.stages_completed
        })
        
    except Exception as e:
        await ws.send_json({"type": "error", "message": str(e)})





# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
