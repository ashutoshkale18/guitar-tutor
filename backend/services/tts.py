"""
Text-to-Speech Service - Calls Piper TTS binary via subprocess.
"""

import json
import subprocess
import logging
import uuid

from config import PIPER_EXE, PIPER_MODEL, TEMP_DIR, STATIC_DIR

logger = logging.getLogger(__name__)


async def synthesize_speech(text: str) -> str:
    """
    Convert text to speech using Piper TTS.
    
    Args:
        text: The text to convert to speech.
        
    Returns:
        Path to the generated WAV audio file.
        
    Raises:
        RuntimeError: If TTS fails.
    """
    # Generate unique output filename
    output_file = str(STATIC_DIR / f"tts_{uuid.uuid4().hex[:8]}.wav")
    
    logger.info(f"Generating speech: '{text[:50]}...'")
    
    try:
        cmd = [
            PIPER_EXE,
            "--model", PIPER_MODEL,
            "--output_file", output_file
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(
            input=text.encode("utf-8"),
            timeout=60
        )
        
        if process.returncode != 0:
            raise RuntimeError(f"Piper failed (code {process.returncode}): {stderr.decode('utf-8', errors='replace')}")
        
        import os
        if not os.path.exists(output_file):
            raise RuntimeError("Piper did not produce output file")
        
        logger.info(f"Speech generated: {output_file}")
        return output_file
        
    except subprocess.TimeoutExpired:
        process.kill()
        raise RuntimeError("TTS timed out (60s limit)")
    except Exception as e:
        if "Piper failed" in str(e) or "TTS timed out" in str(e):
            raise
        raise RuntimeError(f"TTS error: {str(e)}")
