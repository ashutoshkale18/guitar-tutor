"""
Chord Detection Worker - Uses madmom DeepChroma to detect guitar chords.
Called via subprocess by the gateway using the madmom-chords venv (Python 3.9).

Usage:
    python chord_worker.py <audio_file_path>
    
Output (JSON to stdout):
    {
        "success": true,
        "chords": [
            {"start": 0.0, "end": 1.2, "chord": "Am"},
            {"start": 1.2, "end": 2.5, "chord": "G"}
        ],
        "unique_chords": ["Am", "G"],
        "total_segments": 2
    }
"""

import sys
import os
import json
import glob
import warnings
import numpy as np

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


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


def fix_madmom_compatibility():
    """Fix NumPy and collections compatibility issues with madmom."""
    # Fix numpy deprecated aliases
    numpy_aliases = {
        'float': np.float64,
        'int': np.int_,
        'complex': np.complex128,
        'bool': np.bool_,
        'str': np.str_,
        'object': np.object_,
    }
    for alias, actual_type in numpy_aliases.items():
        if not hasattr(np, alias):
            setattr(np, alias, actual_type)

    # Fix collections compatibility for Python 3.10+
    if sys.version_info >= (3, 10):
        try:
            import collections
            import collections.abc
            abc_attributes = [
                'Iterable', 'Iterator', 'Mapping', 'MutableMapping',
                'MutableSequence', 'Sequence', 'Set', 'MutableSet'
            ]
            for attr in abc_attributes:
                if not hasattr(collections, attr) and hasattr(collections.abc, attr):
                    setattr(collections, attr, getattr(collections.abc, attr))
        except (ImportError, AttributeError):
            pass


def output_error(message):
    """Output error as JSON and exit."""
    print(json.dumps({"success": False, "error": message}))
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        output_error("Usage: chord_worker.py <audio_file>")

    audio_file = sys.argv[1]

    if not os.path.exists(audio_file):
        output_error(f"Audio file not found: {audio_file}")

    find_ffmpeg()
    fix_madmom_compatibility()

    try:
        from madmom.audio.chroma import DeepChromaProcessor
        from madmom.features.chords import DeepChromaChordRecognitionProcessor

        # Step 1: Extract chroma features
        chroma_processor = DeepChromaProcessor()
        chroma_features = chroma_processor(audio_file)

        # Step 2: Decode chords from chroma
        chord_decoder = DeepChromaChordRecognitionProcessor()
        chords = chord_decoder(chroma_features)

        # Convert to list of dicts
        chord_list = []
        for item in chords:
            try:
                if hasattr(item, '__getitem__'):
                    start = float(item[0]) if len(item) > 0 else 0.0
                    end = float(item[1]) if len(item) > 1 else 0.0
                    label = str(item[2]) if len(item) > 2 else 'N'
                    chord_list.append({"start": start, "end": end, "chord": label})
                else:
                    chord_list.append({
                        "start": float(item.start),
                        "end": float(item.end),
                        "chord": str(item.label)
                    })
            except Exception:
                continue

        unique_chords = list(set(c["chord"] for c in chord_list))

        print(json.dumps({
            "success": True,
            "chords": chord_list,
            "unique_chords": sorted(unique_chords),
            "total_segments": len(chord_list)
        }))

    except ImportError as e:
        output_error(f"madmom not installed: {e}")
    except Exception as e:
        output_error(f"Chord detection failed: {str(e)}")


if __name__ == "__main__":
    main()
