"""
Audio Separation Script using Spleeter
IMPORTANT: Run this from command line, not from an IDE/editor to avoid freezing issues
"""
import os
import sys

def find_ffmpeg():
    """Find ffmpeg executable"""
    ffmpeg_paths = [
        r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe",
        r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe",
    ]
    
    for path in ffmpeg_paths:
        if os.path.exists(path):
            return path
    
    # Search WinGet packages
    winget_base = r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Packages"
    if os.path.exists(winget_base):
        try:
            for item in os.listdir(winget_base):
                if "FFmpeg" in item:
                    pkg = os.path.join(winget_base, item)
                    for sub in os.listdir(pkg):
                        ffmpeg_exe = os.path.join(pkg, sub, "bin", "ffmpeg.exe")
                        if os.path.exists(ffmpeg_exe):
                            return ffmpeg_exe
        except:
            pass
    return None

def main():
    # MUST be at the very top of main() for Windows multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()
    
    # Configure TensorFlow to avoid freezing issues
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TF logging
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'  # Avoid Intel MKL issues
    
    # Import heavy libraries AFTER freeze_support
    import tensorflow as tf
    from spleeter.separator import Separator
    
    # Configure GPU if available (will use CPU if no GPU)
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            # Enable memory growth to prevent GPU memory issues
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"✅ GPU available: {len(gpus)} GPU(s) detected")
        except RuntimeError as e:
            print(f"⚠️ GPU configuration error: {e}")
            print("Falling back to CPU")
    else:
        print("ℹ️ No GPU detected - using CPU (this will be slower)")
    
    # Find FFmpeg
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        print("❌ ERROR: FFmpeg not found!")
        print("Please install FFmpeg using: winget install Gyan.FFmpeg")
        sys.exit(1)
    
    # Add FFmpeg to PATH
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    print(f"✅ Using FFmpeg: {ffmpeg_path}")
    
    # Configuration
    input_file = "Standard_recording_2.mp3"
    output_dir = "output"
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"❌ ERROR: Input file '{input_file}' not found!")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🎵 Starting audio separation...")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_dir}/")
    print(f"   Model: 4stems (vocals, drums, bass, other)\n")
    
    try:
        # Download pretrained model if needed
        print("📥 Downloading Spleeter model (if not already downloaded)...")
        print("   This may take a few minutes on first run...")
        
        from spleeter.utils.configuration import load_configuration
        
        # Initialize separator (will download model on first run)
        separator = Separator(
            'spleeter:4stems',
            multiprocess=False,  # Disable multiprocessing to prevent freezing
            stft_backend='librosa'  # Use librosa backend
        )
        
        print("🔄 Processing audio file (this may take a few minutes)...")
        
        # Perform separation
        separator.separate_to_file(input_file, output_dir)
        
        print(f"\n✅ SUCCESS! Separation complete!")
        print(f"   Stems saved in '{output_dir}' folder")
        print(f"\n   You should see these files:")
        print(f"   - {output_dir}/Standard_recording_2/vocals.wav")
        print(f"   - {output_dir}/Standard_recording_2/drums.wav")
        print(f"   - {output_dir}/Standard_recording_2/bass.wav")
        print(f"   - {output_dir}/Standard_recording_2/other.wav")
        
    except Exception as e:
        print(f"\n❌ ERROR during separation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
