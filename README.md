# 🎸 LLM Guitar Tutor

An AI-powered guitar tutor that listens to your playing in real-time, analyzes chords, notes, strumming patterns, and tempo, then provides intelligent feedback using a local LLM.

## Architecture

```
[Microphone Audio] → [Demucs Separation]
                           ↓
                  ┌────────┴────────┐
                  │                 │
             [Vocals]          [Guitar Stem]
                  │                 │
             [Whisper]     ┌───────┼───────┐
                  │        │       │       │
                  │    [Chords] [Notes] [Strum]
                  │    (madmom) (madmom) (librosa)
                  │        │       │       │
                  └────────┴───────┴───────┘
                              │
                     [LLM Tutor Response]
                              │
                        [Piper TTS]
```

Each ML component runs in its own **isolated Python virtual environment** to avoid dependency conflicts.

## Components

| Component | Directory | Python | Purpose |
|-----------|-----------|--------|---------|
| **Backend Gateway** | `backend/` | 3.13 | FastAPI server, orchestration, WebSocket API |
| **Audio Separator** | `demucs-separator/` | 3.9 | Splits audio into vocals + instruments (Demucs) |
| **Speech-to-Text** | `whisper-piper/` | 3.13 | Transcribes speech (Whisper) + TTS (Piper) |
| **Chord Detection** | `madmom-chords/` | 3.9 | Detects chords using DeepChroma (madmom) |
| **Note Detection** | `backend/workers/` | 3.9 | Detects individual notes via RNN (madmom) |
| **Strum/Tempo** | `librosa-analysis/` | 3.13 | Onset detection, strum patterns, BPM (librosa) |
| **React Frontend** | `Main/llm-tutor-landing/` | — | React + Vite UI |
| **Vanilla Frontend** | `Main/guitar-tutor-ui/` | — | Lightweight HTML/JS UI |

## Prerequisites

- **Python 3.9** (for madmom/demucs — [download](https://www.python.org/downloads/release/python-3913/))
- **Python 3.13** (for backend/whisper/librosa — [download](https://www.python.org/downloads/))
- **Node.js 18+** ([download](https://nodejs.org/))
- **FFmpeg** ([download](https://ffmpeg.org/download.html) or `winget install Gyan.FFmpeg`)
- **LM Studio** ([download](https://lmstudio.ai/)) — for the local LLM
- **GPU recommended** — Demucs runs much faster with CUDA (RTX 4050+)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/guitar-tutor.git
cd guitar-tutor
```

### 2. Set Up Backend (FastAPI Gateway)

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate        # Windows
pip install -r requirements.txt
deactivate
cd ..
```

### 3. Set Up Demucs (Audio Separation)

> ⚠️ Requires Python 3.9

```bash
cd demucs-separator
py -3.9 -m venv venv
.\venv\Scripts\activate

# Install PyTorch with CUDA (for GPU acceleration)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

pip install -r requirements.txt
deactivate
cd ..
```

### 4. Set Up Whisper + Piper (Speech-to-Text + TTS)

```bash
cd whisper-piper
python -m venv venv
.\venv\Scripts\activate
pip install openai-whisper
deactivate
cd ..
```

**Piper TTS** (pre-built binary):
1. Download Piper from [GitHub Releases](https://github.com/rhasspy/piper/releases)
2. Extract to `whisper-piper/piper/piper/`
3. Download a voice model (e.g., `en_US-amy-low.onnx`) to `whisper-piper/piper/piper/voices/`

### 5. Set Up Madmom (Chord + Note Detection)

> ⚠️ Requires Python 3.9 with specific NumPy version

```bash
cd madmom-chords
py -3.9 -m venv venv
.\venv\Scripts\activate
pip install numpy==1.19.5 cython
pip install madmom
deactivate
cd ..
```

### 6. Set Up Librosa (Strum/Tempo Analysis)

```bash
cd librosa-analysis
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..
```

### 7. Set Up React Frontend

```bash
cd Main/llm-tutor-landing
npm install
cd ../..
```

### 8. Configure Paths

Edit `backend/config.py` and update the Python interpreter paths if your venv locations differ:

```python
DEMUCS_PYTHON = str(TUTOR_ROOT / "demucs-separator" / "venv" / "python.exe")
WHISPER_PYTHON = str(TUTOR_ROOT / "whisper-piper" / "venv" / "Scripts" / "python.exe")
MADMOM_PYTHON = str(TUTOR_ROOT / "madmom-chords" / "venv" / "python.exe")
LIBROSA_PYTHON = str(TUTOR_ROOT / "librosa-analysis" / "venv" / "Scripts" / "python.exe")
```

Also ensure FFmpeg is installed and accessible. The workers auto-search common paths, but you can add yours to `FFMPEG_SEARCH_PATHS` in `config.py`.

## Running

### Step 1: Start LM Studio

1. Open LM Studio
2. Load any chat model (e.g., Llama 3, Mistral, Phi-3)
3. Start the local server on **port 1234** (default)

### Step 2: Start Backend

```bash
cd backend
.\venv\Scripts\activate
python main.py
```

The backend runs on `http://localhost:8000`. You should see:
```
Guitar Tutor Backend Starting...
  Demucs Python: OK
  Whisper Python: OK
  Madmom Python: OK
  Piper Binary: OK
  LM Studio: OK
  API docs: http://localhost:8000/docs
  WebSocket: ws://localhost:8000/ws/session
```

### Step 3: Start Frontend

```bash
cd Main/llm-tutor-landing
npm run dev
```

Open `http://localhost:5173` in your browser.

### Step 4: Use the Tutor

1. Click the **microphone button** to start recording
2. Play guitar and/or ask a question
3. Click again to stop recording
4. Wait for the analysis pipeline to complete (~30-60s)
5. See chords, notes, strum patterns, and AI feedback!

You can also type text questions directly without recording.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `ws://localhost:8000/ws/session` | WebSocket | Main real-time session |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger API docs |

### WebSocket Message Types

**Client → Server:**
- Binary WAV data (audio recording)
- `{"type": "stop_recording"}` — end audio stream
- `{"type": "text_input", "text": "..."}` — text question

**Server → Client:**
- `{"type": "status", "stage": "...", "message": "..."}` — pipeline progress
- `{"type": "transcription", "text": "..."}` — speech-to-text result
- `{"type": "chords", "data": [...], "unique_chords": [...]}` — detected chords
- `{"type": "notes", "data": [...], "unique_notes": [...]}` — detected notes
- `{"type": "strumming", "data": {...}}` — strum pattern & tempo
- `{"type": "response", "text": "..."}` — LLM tutor response
- `{"type": "audio", "data": "base64..."}` — TTS audio response
- `{"type": "complete", "total_time": N}` — pipeline finished

## Project Structure

```
tutor/
├── backend/                    # FastAPI gateway & orchestrator
│   ├── main.py                 # WebSocket server & API
│   ├── orchestrator.py         # Pipeline coordinator
│   ├── config.py               # All paths & settings
│   ├── services/               # Service wrappers (subprocess calls)
│   │   ├── separator.py        # Demucs wrapper
│   │   ├── transcriber.py      # Whisper wrapper
│   │   ├── chord_detector.py   # madmom chord wrapper
│   │   ├── note_detector.py    # madmom note wrapper
│   │   ├── strum_detector.py   # librosa strum wrapper
│   │   ├── llm_client.py       # LM Studio client
│   │   └── tts.py              # Piper TTS wrapper
│   └── workers/                # Standalone scripts (run in venvs)
│       ├── separate_worker.py
│       ├── transcribe_worker.py
│       ├── chord_worker.py
│       ├── note_worker.py
│       ├── strum_worker.py
│       └── tts_worker.py
├── demucs-separator/           # Audio separation venv
├── whisper-piper/              # STT + TTS venv
├── madmom-chords/              # Chord detection venv
├── librosa-analysis/           # Strum/tempo analysis venv
└── Main/                       # Frontend apps
    ├── llm-tutor-landing/      # React + Vite UI
    └── guitar-tutor-ui/        # Vanilla HTML/JS UI
```

## Troubleshooting

### "Madmom import error" or NumPy issues
Madmom requires Python 3.9 and NumPy ≤ 1.19.5. Make sure the madmom venv uses `py -3.9`.

### "LM Studio is not running"
Start LM Studio, load a model, and start the server on port 1234.

### No FFmpeg found
Install FFmpeg: `winget install Gyan.FFmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html).

### Demucs is slow
Demucs runs on CPU by default (~30s). With CUDA GPU it takes ~5s. Install PyTorch with CUDA support.

### Transcription is garbage / hallucinating
This happens when Whisper processes non-speech audio. The pipeline includes an energy threshold check that skips instrument analysis on silent stems, and Whisper filtering to reject hallucinated text.

## License

MIT
