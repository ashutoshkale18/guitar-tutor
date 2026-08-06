# cmake is installed
# microsoft visualStudio.2022.BuildTools installed
# Ninja-build.Ninja installed
# msys2.msys2 installed
# -e --id GnuWin32.Make
# mingw-w64 installed
# BrechtSanders.WinLibs.POSIX.UCRT installed
# learn about the winget

import sys, os, subprocess, json, tempfile, requests, sounddevice as sd, numpy as np, scipy.io.wavfile as wav

# Fix Unicode output on Windows (emoji/special chars)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import whisper
import glob

# Add ffmpeg to PATH
ffmpeg_search_paths = [
    r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Links",
    r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg*\bin",
    r"C:\ProgramData\chocolatey\bin",
    r"C:\ffmpeg\bin",
    r"C:\Program Files\ffmpeg\bin",
]

ffmpeg_found = False
for search_path in ffmpeg_search_paths:
    matching_paths = glob.glob(search_path) if '*' in search_path else [search_path]
    for ffmpeg_path in matching_paths:
        if os.path.exists(ffmpeg_path):
            ffmpeg_exe = os.path.join(ffmpeg_path, 'ffmpeg.exe')
            if os.path.isfile(ffmpeg_exe):
                if ffmpeg_path not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']
                    print(f"✓ Added ffmpeg to PATH: {ffmpeg_path}")
                ffmpeg_found = True
                break
    if ffmpeg_found:
        break

if not ffmpeg_found:
    print("⚠️ Warning: Could not find ffmpeg.exe")

# ==== CONFIG ====
WHISPER_MODEL_NAME = "tiny"  # Using tiny model for faster loading
PIPER_CMD = ["./piper/piper/piper.exe", "--model", "./piper/piper/voices/en_US-amy-low.onnx"]
LM_API = "http://localhost:1234/v1/chat/completions"
RECORD_SECS = 5
AUDIO_FILE = os.path.join(tempfile.gettempdir(), "tutor_voice_input.wav")
# ================

# Load Whisper model once at startup
print("🔄 Loading Whisper model...")
whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
print("✅ Whisper model loaded!")

def record_audio():
    print(f"🎙️ Speak now for {RECORD_SECS} seconds...")
    
    # Get microphone info
    try:
        default_input = sd.query_devices(kind='input')
        print(f"   Using: {default_input['name']}")
        print(f"   Max input channels: {default_input['max_input_channels']}")
    except Exception as e:
        print(f"   Warning: Could not get device info - {e}")
    
    fs = 16000
    
    # Record with explicit device selection
    try:
        audio = sd.rec(
            int(RECORD_SECS * fs), 
            samplerate=fs, 
            channels=1, 
            dtype="float32",
            blocking=True  # Wait for recording to complete
        )
    except Exception as e:
        print(f"❌ Recording error: {e}")
        print("\nTrying to list available input devices...")
        devices = sd.query_devices()
        print("\nAvailable INPUT devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']}")
        raise
    
    # Check if audio was actually recorded
    max_amplitude = np.max(np.abs(audio))
    mean_amplitude = np.mean(np.abs(audio))
    
    print(f"\n📊 Audio Stats:")
    print(f"   Max amplitude: {max_amplitude:.4f}")
    print(f"   Mean amplitude: {mean_amplitude:.4f}")
    
    if max_amplitude < 0.001:
        print("\n⚠️ WARNING: Very low/no audio detected!")
        print("   Possible issues:")
        print("   1. Microphone is muted in Windows")
        print("   2. Browser/app is using the microphone exclusively")
        print("   3. Microphone permissions not granted to Python")
        print("   4. Wrong microphone selected")
        print("\n   Try closing all browser tabs and other apps using the mic.")
    elif max_amplitude < 0.05:
        print("   ⚠️ Audio level is low - boosting gain...")
        # Boost audio by 3x if too quiet
        audio = audio * 3.0
        audio = np.clip(audio, -1.0, 1.0)  # Prevent clipping
    else:
        print("   ✅ Audio level looks good!")
        # Boost audio by 2x for better Whisper detection
        audio = audio * 2.0
        audio = np.clip(audio, -1.0, 1.0)
    
    # Convert to 16-bit PCM for Whisper (reuse single file)
    audio_int16 = (audio * 32767).astype(np.int16)
    wav.write(AUDIO_FILE, fs, audio_int16)
    
    print(f"   💾 Saved to: {AUDIO_FILE}")
    return AUDIO_FILE

def transcribe(file_path):
    print("📝 Transcribing...")
    try:
        # Verify file exists
        if not os.path.exists(file_path):
            print(f"   ❌ File not found: {file_path}")
            return "[File not found]"
        
        # Use Python whisper library with fp32 for CPU and without ffmpeg
        result = whisper_model.transcribe(file_path, language="en", fp16=False)
        text = result["text"].strip()
        
        if not text or len(text) < 2:
            print(f"   ⚠️ No speech detected")
            return "[No speech detected]"
        
        return text
        
    except Exception as e:
        import traceback
        print(f"   ❌ Transcription error: {e}")
        print(f"   Full error: {traceback.format_exc()}")
        return "[Transcription failed]"

def query_lmstudio(prompt):
    payload = {
        "model": "local-llm",
        "messages": [
            {"role": "system", "content": "You are a helpful local AI assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(LM_API, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "⚠️ Error: LM Studio is not running. Please start LM Studio server on port 1234."
    except requests.exceptions.Timeout:
        return "⚠️ Error: LM Studio request timed out."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def speak(text):
    print(f"🔊 Speaking: {text}")
    try:
        p = subprocess.Popen(PIPER_CMD, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.communicate(input=text.encode("utf-8"), timeout=30)
        p.wait()  # Ensure process completes
        if p.returncode != 0:
            print(f"   ⚠️ Piper returned error code: {p.returncode}")
    except subprocess.TimeoutExpired:
        print("   ⚠️ Piper timed out")
        p.kill()
        p.wait()
    except Exception as e:
        print(f"   ⚠️ Speaking error: {e}")

print("\nStarting voice assistant... (say 'exit', 'quit', or 'stop' to end)\n")
print("=" * 60)

while True:
    audio_file = record_audio()
    user_text = transcribe(audio_file)
    
    # Clean up audio file after transcription
    try:
        if os.path.exists(audio_file):
            os.remove(audio_file)
    except OSError:
        pass
    
    print(f"🗣️ You said: {user_text}")
    
    # Check for exit commands
    if user_text.lower().strip() in ["exit", "quit", "stop"]:
        print("👋 Goodbye!")
        break
    
    # Skip LLM query for no speech detected
    if "[No speech detected]" in user_text or "[Transcription failed]" in user_text:
        print("=" * 60)
        continue
    
    reply = query_lmstudio(user_text)
    print(f"🤖 LM Studio: {reply}\n")
    speak(reply)
    print("=" * 60)
