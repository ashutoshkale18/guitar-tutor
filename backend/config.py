"""
Configuration for the Guitar Tutor Backend.
All paths to external venvs, binaries, and services.
"""

import os
from pathlib import Path

# ============================================================
# BASE PATHS
# ============================================================
# Root of the tutor project
TUTOR_ROOT = Path(__file__).parent.parent.resolve()

# This project's root
PROJECT_ROOT = Path(__file__).parent.resolve()

# Temp directory for audio files (inside this project)
TEMP_DIR = PROJECT_ROOT / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# ============================================================
# EXTERNAL PYTHON INTERPRETERS (existing venvs)
# ============================================================
# Demucs audio separator (Python 3.9)
DEMUCS_PYTHON = str(TUTOR_ROOT / "demucs-separator" / "venv" / "python.exe")

# Whisper speech-to-text (Python 3.13)
WHISPER_PYTHON = str(TUTOR_ROOT / "whisper-piper" / "venv" / "Scripts" / "python.exe")

# Madmom chord + note detection (Python 3.9)
MADMOM_PYTHON = str(TUTOR_ROOT / "madmom-chords" / "venv" / "python.exe")

# Librosa strum/tempo analysis (Python 3.13)
LIBROSA_PYTHON = str(TUTOR_ROOT / "librosa-analysis" / "venv" / "Scripts" / "python.exe")

# ============================================================
# PIPER TTS BINARY
# ============================================================
PIPER_EXE = str(TUTOR_ROOT / "whisper-piper" / "piper" / "piper" / "piper.exe")
PIPER_MODEL = str(TUTOR_ROOT / "whisper-piper" / "piper" / "piper" / "voices" / "en_US-amy-low.onnx")

# ============================================================
# WORKER SCRIPTS (in this project)
# ============================================================
WORKERS_DIR = PROJECT_ROOT / "workers"
SEPARATE_WORKER = str(WORKERS_DIR / "separate_worker.py")
TRANSCRIBE_WORKER = str(WORKERS_DIR / "transcribe_worker.py")
CHORD_WORKER = str(WORKERS_DIR / "chord_worker.py")
NOTE_WORKER = str(WORKERS_DIR / "note_worker.py")
STRUM_WORKER = str(WORKERS_DIR / "strum_worker.py")
TTS_WORKER = str(WORKERS_DIR / "tts_worker.py")

# ============================================================
# LM STUDIO (local LLM)
# ============================================================
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_TIMEOUT = 30  # seconds

# ============================================================
# WHISPER CONFIG
# ============================================================
WHISPER_MODEL_NAME = "tiny"  # tiny | base | small | medium | large

# ============================================================
# DEMUCS CONFIG
# ============================================================
DEMUCS_MODEL = "htdemucs"  # htdemucs is best quality

# ============================================================
# AUDIO CONFIG
# ============================================================
AUDIO_SAMPLE_RATE = 16000  # Hz
AUDIO_CHANNELS = 1  # Mono

# ============================================================
# FFMPEG (needed by whisper and demucs)
# ============================================================
FFMPEG_SEARCH_PATHS = [
    r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Links",
    r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg*\bin",
    r"C:\ProgramData\chocolatey\bin",
    r"C:\ffmpeg\bin",
    r"C:\Program Files\ffmpeg\bin",
]

# ============================================================
# GATEWAY SERVER
# ============================================================
HOST = "0.0.0.0"
PORT = 8000

# ============================================================
# LLM SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """You are an expert guitar tutor AI assistant.
You help students learn guitar by analyzing their playing and answering questions.

When chord data is provided, analyze the chord progression and provide feedback on:
- Whether the chords are played correctly
- Suggestions for improvement
- Music theory context (key, progression type)
- Practice tips

When note data is provided, analyze which individual notes were detected:
- Whether notes are clean and in tune
- If notes belong to the detected chord
- Finger positioning suggestions

When strumming data is provided, analyze the rhythm:
- Whether the strum pattern is consistent (e.g., D-U-D-U)
- Tempo stability and BPM feedback
- Rhythm improvement tips

Keep responses concise (2-4 sentences max) and encouraging. Use simple language.
If the student asks a question, answer it directly.
If only playing data is provided (no question), give brief feedback on their playing."""
