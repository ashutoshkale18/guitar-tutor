"""
Strum Pattern & Tempo Detection Worker - Uses librosa for rhythm analysis.
Called via subprocess by the gateway using the librosa-analysis venv.

Detects:
  - Onset times (when each strum/pluck happens)
  - Strum direction (upstroke vs downstroke via spectral centroid)
  - Strum strength (onset envelope amplitude)
  - Tempo / BPM
  - Strum pattern string (e.g., "D-U-D-U")
  - Beat positions
  - Tempo stability

Usage:
    python strum_worker.py <audio_file_path>
    
Output (JSON to stdout):
    {
        "success": true,
        "tempo_bpm": 120.0,
        "pattern": "D-U-D-U",
        "total_strums": 6,
        "events": [...],
        "beat_times": [...],
        "tempo_stability": 0.92
    }
"""

import sys
import os
import json
import glob
import warnings
import numpy as np

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


def classify_strum_direction(y, sr, onset_samples, spectral_centroids, centroid_times):
    """
    Classify each strum as upstroke or downstroke.
    
    Method: Spectral centroid analysis around each onset.
    - Downstrokes typically have a brighter/higher initial attack because
      the pick hits thicker (lower-pitched) strings first, producing a rising
      spectral envelope.
    - Upstrokes hit thinner (higher-pitched) strings first, producing a 
      relatively darker/lower initial centroid.
    
    We compare each onset's centroid to the median centroid to classify.
    """
    directions = []
    
    if len(spectral_centroids) == 0 or len(onset_samples) == 0:
        return ["down"] * len(onset_samples)
    
    # Get centroid values at onset positions
    onset_centroids = []
    for onset_sample in onset_samples:
        onset_time = onset_sample / sr
        # Find nearest centroid frame
        idx = np.argmin(np.abs(centroid_times - onset_time))
        onset_centroids.append(spectral_centroids[idx])
    
    if len(onset_centroids) == 0:
        return ["down"] * len(onset_samples)
    
    # Compare to median: above median → downstroke, below → upstroke
    median_centroid = np.median(onset_centroids)
    
    for centroid_val in onset_centroids:
        if centroid_val >= median_centroid:
            directions.append("down")
        else:
            directions.append("up")
    
    return directions


def calculate_tempo_stability(beat_times):
    """
    Calculate how consistent the tempo is (0.0 to 1.0).
    1.0 = perfectly even spacing, 0.0 = completely irregular.
    """
    if len(beat_times) < 3:
        return 0.0
    
    intervals = np.diff(beat_times)
    if len(intervals) == 0:
        return 0.0
    
    mean_interval = np.mean(intervals)
    if mean_interval == 0:
        return 0.0
    
    # Coefficient of variation (lower = more stable)
    cv = np.std(intervals) / mean_interval
    
    # Convert to 0-1 scale (1 = stable)
    stability = max(0.0, 1.0 - cv)
    return round(stability, 3)


def build_pattern_string(directions):
    """Build a compact pattern string like 'D-U-D-U'."""
    abbrev = {"down": "D", "up": "U"}
    return "-".join(abbrev.get(d, "?") for d in directions)


def main():
    if len(sys.argv) < 2:
        output_error("Usage: strum_worker.py <audio_file>")

    audio_file = sys.argv[1]

    if not os.path.exists(audio_file):
        output_error(f"Audio file not found: {audio_file}")

    find_ffmpeg()

    try:
        import librosa
        import soundfile  # Ensures soundfile backend is available

        # ── Step 1: Load audio at original sample rate ─────────
        # Use None for sr to preserve original sample rate for best quality
        y, sr = librosa.load(audio_file, sr=None, mono=True)
        
        duration = float(len(y) / sr)
        
        if duration < 0.5:
            output_error("Audio too short for strum analysis (need at least 0.5s)")

        # ── Step 2: Onset detection (strum events) ────────────
        # Detect onsets using a combination of spectral flux
        onset_env = librosa.onset.onset_strength(
            y=y, sr=sr,
            hop_length=512,
            aggregate=np.median
        )
        
        # Detect onsets WITHOUT backtrack to get accurate peak strengths
        onset_frames_peak = librosa.onset.onset_detect(
            y=y, sr=sr,
            onset_envelope=onset_env,
            hop_length=512,
            backtrack=False,
            units='frames'
        )
        
        # Detect onsets WITH backtrack for accurate timing
        onset_frames = librosa.onset.onset_detect(
            y=y, sr=sr,
            onset_envelope=onset_env,
            hop_length=512,
            backtrack=True,
            units='frames'
        )
        
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=512)
        onset_samples = librosa.frames_to_samples(onset_frames, hop_length=512)
        
        # Get onset strengths from peak frames (normalized 0-1)
        onset_strengths = []
        max_env = float(np.max(onset_env)) if np.max(onset_env) > 0 else 1.0
        for i, frame in enumerate(onset_frames):
            # Use the peak frame for strength if available
            peak_frame = onset_frames_peak[i] if i < len(onset_frames_peak) else frame
            if peak_frame < len(onset_env):
                onset_strengths.append(round(float(onset_env[peak_frame]) / max_env, 3))
            else:
                onset_strengths.append(0.5)

        # ── Step 3: Spectral centroid for strum direction ──────
        spectral_centroids = librosa.feature.spectral_centroid(
            y=y, sr=sr, hop_length=512
        )[0]  # Shape: (n_frames,)
        
        centroid_times = librosa.frames_to_time(
            np.arange(len(spectral_centroids)), sr=sr, hop_length=512
        )
        
        # Classify strum directions
        directions = classify_strum_direction(
            y, sr, onset_samples, spectral_centroids, centroid_times
        )

        # ── Step 4: Tempo / BPM detection ─────────────────────
        tempo_result = librosa.beat.beat_track(
            y=y, sr=sr, hop_length=512
        )
        
        # librosa >= 0.10 returns (tempo_array, beats), older returns (tempo, beats)
        if isinstance(tempo_result[0], np.ndarray):
            tempo_bpm = float(tempo_result[0][0]) if len(tempo_result[0]) > 0 else 0.0
        else:
            tempo_bpm = float(tempo_result[0])
        
        beat_frames = tempo_result[1]
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=512)

        # ── Step 5: Tempo stability ───────────────────────────
        tempo_stability = calculate_tempo_stability(beat_times)

        # ── Step 6: Build strum events ────────────────────────
        events = []
        for i in range(len(onset_times)):
            events.append({
                "time": round(float(onset_times[i]), 3),
                "direction": directions[i] if i < len(directions) else "down",
                "strength": round(onset_strengths[i] if i < len(onset_strengths) else 0.5, 3)
            })

        # ── Step 7: Build pattern string ──────────────────────
        pattern = build_pattern_string(directions)

        # ── Output ────────────────────────────────────────────
        print(json.dumps({
            "success": True,
            "tempo_bpm": round(tempo_bpm, 1),
            "pattern": pattern,
            "total_strums": len(events),
            "events": events,
            "beat_times": [round(float(t), 3) for t in beat_times],
            "tempo_stability": tempo_stability,
            "duration": round(duration, 2)
        }))

    except ImportError as e:
        output_error(f"librosa not installed: {e}")
    except Exception as e:
        output_error(f"Strum detection failed: {str(e)}")


if __name__ == "__main__":
    main()
