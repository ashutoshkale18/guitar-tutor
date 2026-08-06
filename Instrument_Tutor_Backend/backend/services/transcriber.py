"""
Speech-to-Text Service - Calls Whisper worker via subprocess.
Uses the whisper-piper venv (Python 3.13).
"""

import json
import subprocess
import logging

from config import WHISPER_PYTHON, TRANSCRIBE_WORKER, WHISPER_MODEL_NAME

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio to text using Whisper.
    
    Args:
        audio_path: Path to the audio file (WAV).
        
    Returns:
        dict: {"text": "...", "language": "en", "no_speech": False}
        
    Raises:
        RuntimeError: If transcription fails.
    """
    logger.info(f"Starting transcription: {audio_path}")
    
    try:
        result = subprocess.run(
            [WHISPER_PYTHON, TRANSCRIBE_WORKER, audio_path, WHISPER_MODEL_NAME],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse JSON output
        stdout_lines = result.stdout.strip().split('\n')
        json_output = None
        for line in reversed(stdout_lines):
            line = line.strip()
            if line.startswith('{'):
                try:
                    json_output = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        
        if json_output is None:
            raise RuntimeError(f"No JSON output from transcriber. stdout: {result.stdout}, stderr: {result.stderr}")
        
        if not json_output.get("success"):
            raise RuntimeError(f"Transcription failed: {json_output.get('error', 'Unknown error')}")
        
        logger.info(f"Transcription complete: '{json_output.get('text', '')[:50]}...'")
        return json_output
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Transcription timed out (2 min limit)")
