"""
Strum Pattern & Tempo Detection Service - Calls librosa worker via subprocess.
Uses the librosa-analysis venv.
"""

import json
import subprocess
import logging

from config import LIBROSA_PYTHON, STRUM_WORKER

logger = logging.getLogger(__name__)


async def detect_strumming(audio_path: str) -> dict:
    """
    Detect strumming patterns and tempo in audio using librosa.
    
    Args:
        audio_path: Path to the audio file (WAV) - should be the
                    'other' stem from Demucs (contains guitar).
        
    Returns:
        dict: {"tempo_bpm": 120.0, "pattern": "D-U-D-U", "events": [...], ...}
        
    Raises:
        RuntimeError: If strum detection fails.
    """
    logger.info(f"Starting strum detection: {audio_path}")
    
    try:
        result = subprocess.run(
            [LIBROSA_PYTHON, STRUM_WORKER, audio_path],
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
            raise RuntimeError(f"No JSON output from strum detector. stdout: {result.stdout}, stderr: {result.stderr}")
        
        if not json_output.get("success"):
            raise RuntimeError(f"Strum detection failed: {json_output.get('error', 'Unknown error')}")
        
        logger.info(f"Strum detection complete: {json_output.get('total_strums', 0)} strums, tempo: {json_output.get('tempo_bpm', 0)} BPM, pattern: {json_output.get('pattern', '?')}")
        return json_output
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Strum detection timed out (2 min limit)")
