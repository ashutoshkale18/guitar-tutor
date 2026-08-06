"""
Note Detection Worker - Uses madmom RNN to detect individual notes.
Called via subprocess by the gateway using the madmom-chords venv (Python 3.9).

Usage:
    python note_worker.py <audio_file_path>
    
Output (JSON to stdout):
    {
        "success": true,
        "notes": [
            {"onset": 0.5, "midi": 69, "name": "A4", "duration": 0.3, "velocity": 85}
        ],
        "unique_notes": ["A4", "E4"],
        "total_notes": 2
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


# ============================================================
# MIDI ↔ NOTE MAPPING
# ============================================================
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def midi_to_note(midi_num):
    """Convert MIDI number to note name. e.g., 69 → 'A4', 60 → 'C4'."""
    midi_num = int(round(midi_num))
    octave = (midi_num // 12) - 1
    note = NOTE_NAMES[midi_num % 12]
    return f"{note}{octave}"

def midi_to_frequency(midi_num):
    """Convert MIDI number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_num - 69) / 12.0))


# ============================================================
# GUITAR NOTE RANGE FILTER
# ============================================================
# Standard guitar tuning: E2 (MIDI 40) to C6 (MIDI 84)
# Slightly tighter range than before to reduce false positives
GUITAR_MIDI_LOW = 40   # E2 (lowest open string)
GUITAR_MIDI_HIGH = 84  # C6 (high frets, 24th fret on high E)

def is_guitar_range(midi_num):
    """Check if a MIDI note is within typical guitar range."""
    return GUITAR_MIDI_LOW <= midi_num <= GUITAR_MIDI_HIGH


# ============================================================
# POST-PROCESSING: Deduplicate & Clean Notes
# ============================================================
def deduplicate_notes(notes, time_window_ms=80):
    """
    Merge notes that have the same pitch within a short time window.
    This removes ghost notes / double-triggers from the RNN.
    """
    if not notes:
        return notes
    
    cleaned = [notes[0]]
    for note in notes[1:]:
        prev = cleaned[-1]
        time_diff_ms = (note["onset"] - prev["onset"]) * 1000
        
        # If same pitch and within time window, keep the stronger one
        if note["midi"] == prev["midi"] and time_diff_ms < time_window_ms:
            if note["velocity"] > prev["velocity"]:
                cleaned[-1] = note  # Replace with stronger detection
            # else: keep previous (stronger)
        # If different pitch but extremely close (< 20ms), likely the same strum
        # Keep both since guitar produces multiple simultaneous notes in a chord
        else:
            cleaned.append(note)
    
    return cleaned


def merge_nearby_same_notes(notes, time_window_ms=120):
    """
    Second pass: merge same-pitch notes that are close together.
    Guitar strings ring out and can re-trigger the RNN.
    """
    if len(notes) < 2:
        return notes
    
    result = [notes[0]]
    for note in notes[1:]:
        prev = result[-1]
        time_diff_ms = (note["onset"] - prev["onset"]) * 1000
        
        if note["midi"] == prev["midi"] and time_diff_ms < time_window_ms:
            # Extend the duration of the previous note
            new_end = note["onset"] + note["duration"]
            prev_end = prev["onset"] + prev["duration"]
            prev["duration"] = round(max(new_end, prev_end) - prev["onset"], 3)
            prev["velocity"] = max(prev["velocity"], note["velocity"])
        else:
            result.append(note)
    
    return result


# ============================================================
# UTILITY FUNCTIONS
# ============================================================
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


# ============================================================
# MAIN
# ============================================================
def main():
    if len(sys.argv) < 2:
        output_error("Usage: note_worker.py <audio_file>")

    audio_file = sys.argv[1]

    if not os.path.exists(audio_file):
        output_error(f"Audio file not found: {audio_file}")

    find_ffmpeg()
    fix_madmom_compatibility()

    try:
        from madmom.features.notes import RNNPianoNoteProcessor, NotePeakPickingProcessor

        # Step 1: Run RNN note processor
        note_processor = RNNPianoNoteProcessor()
        activations = note_processor(audio_file)

        # Step 2: Peak picking with guitar-optimized parameters
        # Key changes from original:
        #   - threshold: 0.35 → 0.5 (fewer false positives from overtones)
        #   - smooth: 0.09 → 0.12 (more smoothing to reduce ghost triggers)
        #   - pre_avg/post_avg: wider windows for better peak discrimination
        #   - pre_max/post_max: wider to avoid double-triggers
        peak_picker = NotePeakPickingProcessor(
            fps=100,
            threshold=0.5,       # Higher threshold = fewer false positives
            smooth=0.12,         # More smoothing to reduce noise triggers
            pre_avg=0.15,        # Wider pre-average window
            post_avg=0.15,       # Wider post-average window
            pre_max=0.08,        # Wider pre-max to avoid double-triggers
            post_max=0.08,       # Wider post-max
        )

        notes_raw = peak_picker(activations)
        # notes_raw format: [[onset_time, midi_note, duration, velocity], ...]

        # Step 3: Convert to structured output with guitar range filtering
        note_list = []
        for note_event in notes_raw:
            try:
                onset = float(note_event[0])
                midi = int(round(float(note_event[1])))
                duration = float(note_event[2]) if len(note_event) > 2 else 0.0
                velocity = int(round(float(note_event[3]))) if len(note_event) > 3 else 80

                # Filter 1: Must be in guitar range
                if not is_guitar_range(midi):
                    continue

                # Filter 2: Minimum velocity (discard very quiet detections)
                # These are usually overtones, string noise, or pickup hum
                if velocity < 25:
                    continue
                
                # Filter 3: Minimum duration (discard ultra-short ghost notes)
                if duration > 0 and duration < 0.03:
                    continue

                note_name = midi_to_note(midi)
                frequency = round(midi_to_frequency(midi), 1)

                note_list.append({
                    "onset": round(onset, 3),
                    "midi": midi,
                    "name": note_name,
                    "frequency": frequency,
                    "duration": round(duration, 3),
                    "velocity": min(127, max(0, velocity))
                })
            except Exception:
                continue

        # Sort by onset time
        note_list.sort(key=lambda n: n["onset"])

        # Step 4: Post-processing — deduplicate ghost notes
        note_list = deduplicate_notes(note_list, time_window_ms=80)
        note_list = merge_nearby_same_notes(note_list, time_window_ms=120)

        # Extract unique notes (sorted by pitch for readability)
        unique_notes = sorted(
            list(set(n["name"] for n in note_list)),
            key=lambda name: NOTE_NAMES.index(name[:-1]) + int(name[-1]) * 12
            if name[:-1] in NOTE_NAMES else 0
        )

        print(json.dumps({
            "success": True,
            "notes": note_list,
            "unique_notes": unique_notes,
            "total_notes": len(note_list)
        }))

    except ImportError as e:
        output_error(f"madmom not installed or import error: {e}")
    except Exception as e:
        output_error(f"Note detection failed: {str(e)}")


if __name__ == "__main__":
    main()
