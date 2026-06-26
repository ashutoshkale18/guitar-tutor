"""
Audio Separator Service - Calls Demucs worker via subprocess.
Uses the demucs-separator env (Python 3.9).
"""

import json
import subprocess
import logging

from config import DEMUCS_PYTHON, SEPARATE_WORKER, TEMP_DIR

logger = logging.getLogger(__name__)


async def separate_audio(input_audio_path: str) -> dict:
    """
    Separate audio into stems using Demucs.
    
    Args:
        input_audio_path: Path to the input audio file (WAV).
        
    Returns:
        dict with stem file paths: {"vocals": "...", "other": "...", "drums": "...", "bass": "..."}
        
    Raises:
        RuntimeError: If separation fails.
    """
    output_dir = str(TEMP_DIR / "stems")
    
    logger.info(f"Starting audio separation: {input_audio_path}")
    
    try:
        result = subprocess.run(
            [DEMUCS_PYTHON, SEPARATE_WORKER, input_audio_path, output_dir],
            capture_output=True,
            text=True,
            timeout=300,
            env=None  # Use the worker's own env
        )
        
        # Parse JSON output from stdout (skip any non-JSON lines)
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
            raise RuntimeError(f"No JSON output from separator. stdout: {result.stdout}, stderr: {result.stderr}")
        
        if not json_output.get("success"):
            raise RuntimeError(f"Separation failed: {json_output.get('error', 'Unknown error')}")
        
        logger.info(f"Separation complete. Stems: {list(json_output.keys())}")
        return json_output
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Audio separation timed out (5 min limit)")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse separator output: {e}")
