"""
Note Detection Service - Calls madmom note worker via subprocess.
Uses the madmom-chords venv (Python 3.9).
"""

import json
import subprocess
import logging

from config import MADMOM_PYTHON, NOTE_WORKER

logger = logging.getLogger(__name__)


async def detect_notes(audio_path: str) -> dict:
    """
    Detect individual notes in audio using madmom RNN.
    
    Args:
        audio_path: Path to the audio file (WAV) - should be the
                    'other' stem from Demucs (contains guitar).
        
    Returns:
        dict: {"notes": [...], "unique_notes": [...], "total_notes": N}
        
    Raises:
        RuntimeError: If note detection fails.
    """
    logger.info(f"Starting note detection: {audio_path}")
    
    try:
        result = subprocess.run(
            [MADMOM_PYTHON, NOTE_WORKER, audio_path],
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
            raise RuntimeError(f"No JSON output from note detector. stdout: {result.stdout}, stderr: {result.stderr}")
        
        if not json_output.get("success"):
            raise RuntimeError(f"Note detection failed: {json_output.get('error', 'Unknown error')}")
        
        logger.info(f"Note detection complete: {json_output.get('total_notes', 0)} notes, unique: {json_output.get('unique_notes', [])}")
        return json_output
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Note detection timed out (2 min limit)")
