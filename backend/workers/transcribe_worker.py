"""
Speech-to-Text Worker - Uses OpenAI Whisper to transcribe audio.
Called via subprocess by the gateway using the whisper-piper venv.

Usage:
    python transcribe_worker.py <audio_file_path> [model_name]
    
Output (JSON to stdout):
    {
        "success": true,
        "text": "transcribed text here",
        "language": "en"
    }
"""

import sys
import os
import json
import glob
import warnings

warnings.filterwarnings("ignore")


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
    if len(sys.argv) < 2:
        output_error("Usage: transcribe_worker.py <audio_file> [model_name]")

    audio_file = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "tiny"

    if not os.path.exists(audio_file):
        output_error(f"Audio file not found: {audio_file}")

    find_ffmpeg()

    try:
        import whisper

        # Load model (cached after first load)
        model = whisper.load_model(model_name)

        # Transcribe with anti-hallucination settings
        # - condition_on_previous_text=False: prevents hallucination cascading
        # - compression_ratio_threshold: filters repetitive hallucinated text
        result = model.transcribe(
            audio_file,
            language="en",
            fp16=False,
            condition_on_previous_text=False,
            compression_ratio_threshold=2.4
        )

        # Filter segments: keep real speech, drop obvious hallucinations
        filtered_segments = []
        for segment in result.get("segments", []):
            no_speech_prob = segment.get("no_speech_prob", 0.0)
            avg_logprob = segment.get("avg_logprob", 0.0)
            seg_text = segment.get("text", "").strip()

            # Skip segments where Whisper is very confident there's NO speech
            if no_speech_prob > 0.7:
                continue
            # Skip segments with extremely low confidence (total garbage)
            if avg_logprob < -1.5:
                continue
            # Skip very short nonsense (single chars, punctuation only)
            if len(seg_text) < 2:
                continue
            
            filtered_segments.append(seg_text)

        text = " ".join(filtered_segments).strip()

        if not text or len(text) < 2:
            print(json.dumps({
                "success": True,
                "text": "",
                "language": "en",
                "no_speech": True
            }))
        else:
            print(json.dumps({
                "success": True,
                "text": text,
                "language": result.get("language", "en"),
                "no_speech": False
            }))

    except ImportError as e:
        output_error(f"Whisper not installed: {e}")
    except Exception as e:
        output_error(f"Transcription failed: {str(e)}")


if __name__ == "__main__":
    main()
