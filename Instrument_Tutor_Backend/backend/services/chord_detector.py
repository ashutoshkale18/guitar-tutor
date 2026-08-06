"""
Chord Detection Service - Calls madmom worker via subprocess.
Uses the madmom-chords env (Python 3.9).
"""

import json
import subprocess
import logging

from config import MADMOM_PYTHON, CHORD_WORKER

logger = logging.getLogger(__name__)


async def detect_chords(audio_path: str) -> dict:
    """
    Detect chords in audio using madmom DeepChroma.
    
    Args:
        audio_path: Path to the audio file (WAV) - should be the
                    'other' stem from Demucs (contains guitar).
        
    Returns:
        dict: {"chords": [...], "unique_chords": [...], "total_segments": N}
        
    Raises:
        RuntimeError: If chord detection fails.
    """
    logger.info(f"Starting chord detection: {audio_path}")
    
    try:
        result = subprocess.run(
            [MADMOM_PYTHON, CHORD_WORKER, audio_path],
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
            raise RuntimeError(f"No JSON output from chord detector. stdout: {result.stdout}, stderr: {result.stderr}")
        
        if not json_output.get("success"):
            raise RuntimeError(f"Chord detection failed: {json_output.get('error', 'Unknown error')}")
        
        logger.info(f"Chord detection complete: {json_output.get('total_segments', 0)} segments, chords: {json_output.get('unique_chords', [])}")
        return json_output
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Chord detection timed out (2 min limit)")
