"""
Audio Separation Worker - Uses Demucs to split audio into stems.
Called via subprocess by the gateway using the demucs-separator venv.

Usage:
    python separate_worker.py <input_audio_path> <output_dir>
    
Output (JSON to stdout):
    {
        "success": true,
        "vocals": "/path/to/vocals.wav",
        "other": "/path/to/other.wav",
        "drums": "/path/to/drums.wav",
        "bass": "/path/to/bass.wav"
    }
"""

import sys
import os
import json
import subprocess
import glob


def find_ffmpeg():
    """Find and add ffmpeg to PATH."""
    search_paths = [
        r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Links",
        r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg*\bin",
        r"C:\ProgramData\chocolatey\bin",
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
    ]
    for search_path in search_paths:
        matching = glob.glob(search_path) if '*' in search_path else [search_path]
        for path in matching:
            ffmpeg_exe = os.path.join(path, 'ffmpeg.exe')
            if os.path.isfile(ffmpeg_exe):
                if path not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
                return True
    return False


def output_error(message):
    """Output error as JSON and exit."""
    print(json.dumps({"success": False, "error": message}))
    sys.exit(1)


def main():
    import multiprocessing
    multiprocessing.freeze_support()

    if len(sys.argv) < 3:
        output_error("Usage: separate_worker.py <input_audio> <output_dir>")

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_file):
        output_error(f"Input file not found: {input_file}")

    find_ffmpeg()

    # Suppress TF warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

    os.makedirs(output_dir, exist_ok=True)

    # Run demucs via subprocess (same approach as separate_studio.py)
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        device = "cpu"

    cmd = [
        sys.executable, "-m", "demucs",
        "--device", device,
        "-n", "htdemucs",
        "-o", output_dir,
        input_file
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 min max
        )

        if result.returncode != 0:
            output_error(f"Demucs failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        output_error("Demucs timed out after 5 minutes")
    except Exception as e:
        output_error(f"Demucs error: {str(e)}")

    # Find output files
    # Demucs outputs to: <output_dir>/htdemucs/<input_filename_without_ext>/
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    stems_dir = os.path.join(output_dir, "htdemucs", input_name)

    if not os.path.isdir(stems_dir):
        output_error(f"Demucs output directory not found: {stems_dir}")

    stems = {}
    for stem_name in ["vocals", "other", "drums", "bass"]:
        stem_path = os.path.join(stems_dir, f"{stem_name}.wav")
        if os.path.isfile(stem_path):
            stems[stem_name] = stem_path

    if not stems:
        output_error("No stem files found in Demucs output")

    result = {"success": True}
    result.update(stems)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
