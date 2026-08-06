"""
Strum Pattern & Tempo Detection Worker - Uses librosa for rhythm analysis.
Called via subprocess by the gateway using the librosa-analysis venv.

Detects:
  - Onset times (when each strum/pluck happens)
  - Strum direction (upstroke vs downstroke via spectral centroid slope)
  - Strum strength (onset envelope amplitude)
  - Tempo / BPM (onset-interval based, NOT beat_track)
  - Strum pattern string (e.g., "D-U-D-U")
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


def classify_strum_direction_slope(y, sr, onset_times, hop_length=512):
    """
    Classify each strum as upstroke or downstroke using spectral centroid SLOPE.
    
    Theory:
    - Downstrokes: pick hits low strings (E2, A2) first, then sweeps to high strings.
      This produces a RISING spectral centroid in the ~30ms after onset.
    - Upstrokes: pick hits high strings (E4, B3) first, then sweeps to low strings.
      This produces a FALLING spectral centroid after onset.
    
    We measure the slope of the spectral centroid in a 40ms window after each onset.
    """
    import librosa
    
    # Compute spectral centroid at high time resolution
    spectral_centroids = librosa.feature.spectral_centroid(
        y=y, sr=sr, hop_length=hop_length
    )[0]
    
    centroid_times = librosa.frames_to_time(
        np.arange(len(spectral_centroids)), sr=sr, hop_length=hop_length
    )
    
    directions = []
    analysis_window_ms = 40  # Look at centroid slope over 40ms after onset
    
    for onset_time in onset_times:
        # Get centroid values in the window [onset, onset + 40ms]
        window_start = onset_time
        window_end = onset_time + (analysis_window_ms / 1000.0)
        
        mask = (centroid_times >= window_start) & (centroid_times <= window_end)
        window_centroids = spectral_centroids[mask]
        
        if len(window_centroids) < 2:
            # Not enough data points — default to downstroke
            directions.append("down")
            continue
        
        # Calculate slope using linear regression
        x = np.arange(len(window_centroids))
        slope = np.polyfit(x, window_centroids, 1)[0]
        
        # Positive slope = rising centroid = downstroke (low-to-high sweep)
        # Negative slope = falling centroid = upstroke (high-to-low sweep)
        if slope >= 0:
            directions.append("down")
        else:
            directions.append("up")
    
    return directions


def estimate_tempo_from_onsets(onset_times, min_bpm=40, max_bpm=220):
    """
    Estimate BPM from onset inter-onset intervals (IOI).
    More reliable for guitar than librosa.beat.beat_track which is drum-focused.
    
    Method: Find the most common IOI and convert to BPM.
    """
    if len(onset_times) < 3:
        return 0.0
    
    # Calculate inter-onset intervals
    iois = np.diff(onset_times)
    
    # Filter to musically meaningful range
    min_ioi = 60.0 / max_bpm  # ~0.27s at 220 BPM
    max_ioi = 60.0 / min_bpm  # ~1.5s at 40 BPM
    
    valid_iois = iois[(iois >= min_ioi) & (iois <= max_ioi)]
    
    if len(valid_iois) < 2:
        # Fallback: use all intervals
        if len(iois) > 0:
            median_ioi = np.median(iois)
            if median_ioi > 0:
                return round(60.0 / median_ioi, 1)
        return 0.0
    
    # Use histogram to find the most common IOI
    # This is more robust than simple median
    n_bins = min(20, len(valid_iois))
    hist, bin_edges = np.histogram(valid_iois, bins=n_bins)
    peak_bin = np.argmax(hist)
    dominant_ioi = (bin_edges[peak_bin] + bin_edges[peak_bin + 1]) / 2.0
    
    if dominant_ioi > 0:
        bpm = 60.0 / dominant_ioi
        # Clamp to reasonable range
        bpm = max(min_bpm, min(max_bpm, bpm))
        return round(bpm, 1)
    
    return 0.0


def calculate_tempo_stability(onset_times):
    """
    Calculate how consistent the strumming tempo is (0.0 to 1.0).
    Uses inter-onset intervals instead of beat times for guitar accuracy.
    1.0 = perfectly even spacing, 0.0 = completely irregular.
    """
    if len(onset_times) < 3:
        return 0.0
    
    intervals = np.diff(onset_times)
    
    # Remove outlier intervals (> 2x or < 0.5x the median)
    median_int = np.median(intervals)
    if median_int == 0:
        return 0.0
    
    filtered = intervals[
        (intervals >= median_int * 0.4) & 
        (intervals <= median_int * 2.5)
    ]
    
    if len(filtered) < 2:
        return 0.0
    
    mean_interval = np.mean(filtered)
    if mean_interval == 0:
        return 0.0
    
    # Coefficient of variation (lower = more stable)
    cv = np.std(filtered) / mean_interval
    
    # Convert to 0-1 scale (1 = stable)
    # cv of 0 = perfect, cv of 0.5 = very inconsistent
    stability = max(0.0, min(1.0, 1.0 - (cv * 2.0)))
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

        # ── Step 1: Load audio ────────────────────────────────
        y, sr = librosa.load(audio_file, sr=None, mono=True)
        
        duration = float(len(y) / sr)
        
        if duration < 0.5:
            output_error("Audio too short for strum analysis (need at least 0.5s)")

        # ── Step 2: Onset detection with adaptive threshold ───
        # Use spectral flux for onset strength
        onset_env = librosa.onset.onset_strength(
            y=y, sr=sr,
            hop_length=512,
            aggregate=np.median
        )
        
        # Calculate dynamic delta threshold based on audio energy
        rms = librosa.feature.rms(y=y, hop_length=512)[0]
        mean_rms = float(np.mean(rms))
        
        # Gentler dynamic delta — avoid being too aggressive
        # quiet audio (rms < 0.01): delta = 0.03
        # normal audio (rms ~0.05): delta = 0.06
        # loud audio (rms > 0.1): delta = 0.1
        dynamic_delta = max(0.03, min(0.12, mean_rms * 0.8 + 0.02))
        
        # Detect onsets WITHOUT backtrack — these are at the onset peaks
        # (used for strength measurement)
        onset_frames_peak = librosa.onset.onset_detect(
            y=y, sr=sr,
            onset_envelope=onset_env,
            hop_length=512,
            backtrack=False,
            units='frames',
            delta=dynamic_delta
        )
        
        # Detect onsets WITH backtrack for accurate timing
        onset_frames = librosa.onset.onset_detect(
            y=y, sr=sr,
            onset_envelope=onset_env,
            hop_length=512,
            backtrack=True,
            units='frames',
            delta=dynamic_delta
        )
        
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=512)
        
        # ── Step 3: Measure strength from PEAK frames, filter weak ones ──
        max_env = float(np.max(onset_env)) if np.max(onset_env) > 0 else 1.0
        min_strength_threshold = 0.08  # Minimum 8% of peak strength
        
        filtered_indices = []
        onset_strengths = []
        for i in range(len(onset_frames)):
            # Use peak frame for strength (not backtracked frame!)
            peak_frame = onset_frames_peak[i] if i < len(onset_frames_peak) else onset_frames[i]
            if peak_frame < len(onset_env):
                strength = float(onset_env[peak_frame]) / max_env
            else:
                strength = 0.5
            
            if strength >= min_strength_threshold:
                filtered_indices.append(i)
                onset_strengths.append(round(strength, 3))
        
        # Apply filter
        onset_times = onset_times[filtered_indices]
        onset_frames = onset_frames[filtered_indices]

        # ── Step 4: Strum direction via spectral centroid slope ─
        directions = classify_strum_direction_slope(
            y, sr, onset_times, hop_length=512
        )

        # ── Step 5: Tempo / BPM from onset intervals ──────────
        # This is more accurate for guitar than beat_track (drum-optimized)
        tempo_bpm = estimate_tempo_from_onsets(onset_times)
        
        # Also get beat positions from librosa for reference
        tempo_result = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
        if isinstance(tempo_result[0], np.ndarray):
            librosa_bpm = float(tempo_result[0][0]) if len(tempo_result[0]) > 0 else 0.0
        else:
            librosa_bpm = float(tempo_result[0])
        
        beat_frames = tempo_result[1]
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=512)
        
        # If our onset-based BPM is zero, fall back to librosa
        if tempo_bpm == 0.0 and librosa_bpm > 0:
            tempo_bpm = round(librosa_bpm, 1)

        # ── Step 6: Tempo stability from onset intervals ──────
        tempo_stability = calculate_tempo_stability(onset_times)

        # ── Step 7: Build strum events ────────────────────────
        events = []
        for i in range(len(onset_times)):
            events.append({
                "time": round(float(onset_times[i]), 3),
                "direction": directions[i] if i < len(directions) else "down",
                "strength": onset_strengths[i] if i < len(onset_strengths) else 0.5
            })

        # ── Step 8: Build pattern string ──────────────────────
        pattern = build_pattern_string(directions)

        # ── Output ────────────────────────────────────────────
        print(json.dumps({
            "success": True,
            "tempo_bpm": tempo_bpm,
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
