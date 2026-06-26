"""
Audio Separation using Demucs with RTX 4050 GPU
Much more stable than Spleeter - no freezing!
"""
import os
import sys
import subprocess

def main():
    import multiprocessing
    multiprocessing.freeze_support()
    
    print("=" * 60)
    print("AUDIO SEPARATION WITH DEMUCS (GPU Accelerated)")
    print("=" * 60)
    print()
    
    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU Detected: {gpu_name}")
            print(f"   CUDA Version: {torch.version.cuda}")
            device = "cuda"
        else:
            print("⚠️  No GPU detected - will use CPU (slower)")
            device = "cpu"
    except Exception as e:
        print(f"⚠️  GPU check failed: {e}")
        device = "cpu"
    
    print()
    
    # Configuration
    input_file = "Standard_recording_2.mp3"
    output_dir = "output"
    
    # Validate input
    if not os.path.exists(input_file):
        print(f"❌ ERROR: Input file '{input_file}' not found!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎵 Input File: {input_file}")
    print(f"📁 Output Folder: {output_dir}/")
    print(f"🔧 Device: {device.upper()}")
    print(f"🎯 Model: htdemucs (4 stems: drums, bass, other, vocals)")
    print()
    print("🔄 Starting separation... (This may take a few minutes)")
    print("   Please wait and DO NOT close this window!")
    print()
    
    # Run Demucs
    cmd = [
        sys.executable, "-m", "demucs",
        "--device", device,
        "-n", "htdemucs",  # Use htdemucs model (best quality)
        "-o", output_dir,
        input_file
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! Audio separation complete!")
        print("=" * 60)
        print()
        print(f"📂 Output location: {output_dir}/htdemucs/Standard_recording_2/")
        print()
        print("   Separated tracks:")
        print("   ├── drums.wav")
        print("   ├── bass.wav")
        print("   ├── other.wav")
        print("   └── vocals.wav")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("❌ ERROR: Separation failed!")
        print(f"   Error code: {e.returncode}")
    except Exception as e:
        print()
        print(f"❌ ERROR: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
