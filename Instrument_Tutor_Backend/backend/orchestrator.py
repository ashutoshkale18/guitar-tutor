"""
Pipeline Orchestrator - Coordinates the full audio processing pipeline.

Flow:
  1. Receive raw audio (voice + guitar mixed)
  2. Separate audio into stems (Demucs)
  3. In parallel: Transcribe vocals (Whisper) + Detect chords (madmom) + Detect notes (madmom) + Detect strum/tempo (librosa)
  4. Combine text + chords + notes + strum → Query LLM (LM Studio)
  5. Generate voice response (Piper TTS)
  6. Return results
"""

import os
import asyncio
import logging
import time
import uuid
import wave
import struct
import math
from typing import Callable, Optional

from config import TEMP_DIR
from services.separator import separate_audio
from services.transcriber import transcribe_audio
from services.chord_detector import detect_chords
from services.note_detector import detect_notes
from services.strum_detector import detect_strumming
from services.llm_client import query_llm
from services.tts import synthesize_speech

logger = logging.getLogger(__name__)


class PipelineResult:
    """Container for the full pipeline result."""
    
    def __init__(self):
        self.user_text: str = ""
        self.chords: list[dict] = []
        self.unique_chords: list[str] = []
        self.notes: list[dict] = []
        self.unique_notes: list[str] = []
        self.strumming: dict = {}
        self.llm_response: str = ""
        self.audio_response_path: str = ""
        self.stages_completed: list[str] = []
        self.errors: list[str] = []
        self.total_time: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "user_text": self.user_text,
            "chords": self.chords,
            "unique_chords": self.unique_chords,
            "notes": self.notes,
            "unique_notes": self.unique_notes,
            "strumming": self.strumming,
            "llm_response": self.llm_response,
            "audio_response_path": self.audio_response_path,
            "stages_completed": self.stages_completed,
            "errors": self.errors,
            "total_time_seconds": round(self.total_time, 2)
        }


async def run_pipeline(
    audio_path: str,
    on_status: Optional[Callable] = None
) -> PipelineResult:
    """
    Run the complete audio processing pipeline.
    
    Args:
        audio_path: Path to the raw audio file (WAV) from the user.
        on_status: Optional callback for real-time status updates.
                   Called with (stage: str, message: str).
    
    Returns:
        PipelineResult with all outputs.
    """
    result = PipelineResult()
    start_time = time.time()
    
    async def update_status(stage: str, message: str):
        logger.info(f"[{stage}] {message}")
        if on_status:
            await on_status(stage, message)
    
    # ── Step 1: Separate audio ────────────────────────────────
    await update_status("separating", "Separating audio into voice and instrument stems...")
    
    try:
        stems = await separate_audio(audio_path)
        result.stages_completed.append("separation")
        
        vocals_path = stems.get("vocals")
        # "other" contains guitar, keys, synths - this is what we analyze for chords
        other_path = stems.get("other")
        
        if not vocals_path:
            result.errors.append("No vocals stem produced")
        if not other_path:
            result.errors.append("No instrument stem produced")
            
    except Exception as e:
        error_msg = f"Audio separation failed: {str(e)}"
        result.errors.append(error_msg)
        logger.error(error_msg)
        
        # Fallback: use original audio for both STT and chord detection
        await update_status("separating", "Separation failed - using raw audio as fallback")
        vocals_path = audio_path
        other_path = audio_path
    
    # ── Step 2: Check if instrument stem has enough audio energy ──
    instrument_has_audio = await _check_audio_energy(other_path)
    
    # ── Step 3: Parallel processing (STT + optional Chord/Note/Strum) ──
    if instrument_has_audio:
        await update_status("processing", "Analyzing speech, chords, notes, and strumming in parallel...")
    else:
        await update_status("processing", "Analyzing speech (no instrument audio detected)...")
    
    # Always run transcription
    transcribe_task = asyncio.create_task(
        _safe_transcribe(vocals_path, result)
    )
    
    # Only run instrument analysis if there's actual instrument audio
    instrument_tasks = []
    if instrument_has_audio:
        instrument_tasks.append(asyncio.create_task(
            _safe_detect_chords(other_path, result)
        ))
        instrument_tasks.append(asyncio.create_task(
            _safe_detect_notes(other_path, result)
        ))
        instrument_tasks.append(asyncio.create_task(
            _safe_detect_strumming(other_path, result)
        ))
    else:
        logger.info("Skipping instrument analysis — other stem is too quiet")
    
    await asyncio.gather(transcribe_task, *instrument_tasks)
    
    # ── Step 3: Query LLM ─────────────────────────────────────
    await update_status("thinking", "Generating response from tutor AI...")
    
    try:
        chord_data = result.chords if result.chords else None
        note_data = result.notes if result.notes else None
        strum_data = result.strumming if result.strumming else None
        user_text = result.user_text if result.user_text else ""
        
        llm_response = await query_llm(user_text, chord_data, note_data, strum_data)
        result.llm_response = llm_response
        result.stages_completed.append("llm")
        
    except Exception as e:
        error_msg = f"LLM query failed: {str(e)}"
        result.errors.append(error_msg)
        logger.error(error_msg)
        result.llm_response = "Sorry, I couldn't process your request. Please make sure LM Studio is running."
    
    # ── Step 4: Generate voice response ───────────────────────
    await update_status("speaking", "Generating voice response...")
    
    try:
        audio_response = await synthesize_speech(result.llm_response)
        result.audio_response_path = audio_response
        result.stages_completed.append("tts")
        
    except Exception as e:
        error_msg = f"Voice synthesis failed: {str(e)}"
        result.errors.append(error_msg)
        logger.error(error_msg)
    
    result.total_time = time.time() - start_time
    await update_status("complete", f"Pipeline complete in {result.total_time:.1f}s")
    
    return result


async def run_text_only_pipeline(
    text: str,
    on_status: Optional[Callable] = None
) -> PipelineResult:
    """
    Run a text-only pipeline (no audio processing).
    Useful for text-based questions to the tutor.
    
    Args:
        text: User's text question.
        on_status: Optional callback for status updates.
    
    Returns:
        PipelineResult with LLM response.
    """
    result = PipelineResult()
    start_time = time.time()
    
    result.user_text = text
    
    try:
        llm_response = await query_llm(text, None)
        result.llm_response = llm_response
        result.stages_completed.append("llm")
    except Exception as e:
        result.errors.append(str(e))
        result.llm_response = "Sorry, I couldn't process your request."
    
    try:
        audio_path = await synthesize_speech(result.llm_response)
        result.audio_response_path = audio_path
        result.stages_completed.append("tts")
    except Exception as e:
        result.errors.append(f"TTS failed: {str(e)}")
    
    result.total_time = time.time() - start_time
    return result


async def _check_audio_energy(audio_path: str, threshold_db: float = -40.0) -> bool:
    """
    Check if an audio file has enough energy to contain meaningful audio.
    Returns False if the RMS energy is below the threshold (near silence).
    
    Args:
        audio_path: Path to WAV file.
        threshold_db: RMS threshold in dB. Default -40dB (very quiet).
    
    Returns:
        True if audio has meaningful content, False if near-silent.
    """
    try:
        if not audio_path or not os.path.exists(audio_path):
            return False
        
        with wave.open(audio_path, 'rb') as wf:
            n_frames = wf.getnframes()
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            
            if n_frames == 0:
                return False
            
            # Read all frames
            raw_data = wf.readframes(n_frames)
            
            # Convert to samples based on sample width
            if sampwidth == 2:  # 16-bit
                fmt = f'<{n_frames * n_channels}h'
                samples = struct.unpack(fmt, raw_data)
                max_val = 32768.0
            elif sampwidth == 4:  # 32-bit
                fmt = f'<{n_frames * n_channels}i'
                samples = struct.unpack(fmt, raw_data)
                max_val = 2147483648.0
            else:
                # Fallback: assume there's audio
                return True
            
            # Calculate RMS energy (normalized 0-1)
            sum_sq = sum(s * s for s in samples)
            rms = math.sqrt(sum_sq / len(samples)) / max_val
            
            if rms == 0:
                return False
            
            rms_db = 20 * math.log10(rms)
            logger.info(f"Audio energy check: {audio_path} → RMS = {rms_db:.1f} dB (threshold: {threshold_db} dB)")
            
            return rms_db > threshold_db
            
    except Exception as e:
        logger.warning(f"Energy check failed, assuming audio present: {e}")
        return True  # If we can't check, assume there's audio


async def _safe_transcribe(audio_path: str, result: PipelineResult):
    """Transcribe audio with error handling."""
    try:
        transcription = await transcribe_audio(audio_path)
        result.user_text = transcription.get("text", "")
        result.stages_completed.append("transcription")
        
        if transcription.get("no_speech"):
            logger.info("No speech detected in vocals")
            
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        result.errors.append(error_msg)
        logger.error(error_msg)


async def _safe_detect_chords(audio_path: str, result: PipelineResult):
    """Detect chords with error handling."""
    try:
        chord_result = await detect_chords(audio_path)
        result.chords = chord_result.get("chords", [])
        result.unique_chords = chord_result.get("unique_chords", [])
        result.stages_completed.append("chord_detection")
        
    except Exception as e:
        error_msg = f"Chord detection failed: {str(e)}"
        result.errors.append(error_msg)
        logger.error(error_msg)


async def _safe_detect_notes(audio_path: str, result: PipelineResult):
    """Detect individual notes with error handling."""
    try:
        note_result = await detect_notes(audio_path)
        result.notes = note_result.get("notes", [])
        result.unique_notes = note_result.get("unique_notes", [])
        result.stages_completed.append("note_detection")
        
    except Exception as e:
        error_msg = f"Note detection failed: {str(e)}"
        result.errors.append(error_msg)
        logger.error(error_msg)


async def _safe_detect_strumming(audio_path: str, result: PipelineResult):
    """Detect strum patterns and tempo with error handling."""
    try:
        strum_result = await detect_strumming(audio_path)
        result.strumming = {
            "tempo_bpm": strum_result.get("tempo_bpm", 0),
            "pattern": strum_result.get("pattern", ""),
            "total_strums": strum_result.get("total_strums", 0),
            "events": strum_result.get("events", []),
            "beat_times": strum_result.get("beat_times", []),
            "tempo_stability": strum_result.get("tempo_stability", 0),
        }
        result.stages_completed.append("strum_detection")
        
    except Exception as e:
        error_msg = f"Strum detection failed: {str(e)}"
        result.errors.append(error_msg)
        logger.error(error_msg)


def cleanup_temp_files():
    """Clean up old temp files."""
    import glob as glob_mod
    
    for pattern in ["*.wav", "stems/"]:
        for filepath in glob_mod.glob(str(TEMP_DIR / pattern)):
            try:
                if os.path.isfile(filepath):
                    # Only remove files older than 10 minutes
                    if time.time() - os.path.getmtime(filepath) > 600:
                        os.remove(filepath)
            except OSError:
                pass
