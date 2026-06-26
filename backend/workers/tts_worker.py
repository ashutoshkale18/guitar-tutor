"""
Text-to-Speech Worker - Uses Piper TTS to generate audio from text.
Called via subprocess by the gateway.

Usage:
    python tts_worker.py <output_audio_path> "text to speak"
    
Output (JSON to stdout):
    {
        "success": true,
        "audio_file": "/path/to/output.wav"
    }
"""

import sys
import os
import json
import subprocess


def output_error(message):
    """Output error as JSON and exit."""
    print(json.dumps({"success": False, "error": message}))
    sys.exit(1)


def main():
    if len(sys.argv) < 3:
        output_error("Usage: tts_worker.py <output_audio_path> <text>")

    output_file = sys.argv[1]
    text = sys.argv[2]

    if not text.strip():
        output_error("No text provided")

    # Piper binary path (relative to tutor root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    tutor_root = os.path.dirname(project_dir)

    piper_exe = os.path.join(tutor_root, "whisper-piper", "piper", "piper", "piper.exe")
    piper_model = os.path.join(tutor_root, "whisper-piper", "piper", "piper", "voices", "en_US-amy-low.onnx")

    if not os.path.isfile(piper_exe):
        output_error(f"Piper binary not found: {piper_exe}")

    if not os.path.isfile(piper_model):
        output_error(f"Piper model not found: {piper_model}")

    try:
        cmd = [
            piper_exe,
            "--model", piper_model,
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
            output_error(f"Piper failed (code {process.returncode}): {stderr.decode('utf-8', errors='replace')}")

        if not os.path.exists(output_file):
            output_error("Piper did not produce output file")

        print(json.dumps({
            "success": True,
            "audio_file": output_file
        }))

    except subprocess.TimeoutExpired:
        process.kill()
        output_error("Piper timed out after 60 seconds")
    except Exception as e:
        output_error(f"TTS error: {str(e)}")


if __name__ == "__main__":
    main()
