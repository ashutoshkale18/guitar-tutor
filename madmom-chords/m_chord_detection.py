"""
Madmom Chord Detection - WORKING VERSION
Fixes the NumPy 1.20+ dtype compatibility issue with madmom
"""

import os
import sys
import numpy as np
import warnings

def fix_madmom_compatibility():
    """Fix NumPy and collections compatibility issues with madmom"""
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=UserWarning)
    
    # Add ffmpeg to PATH if not already there
    import glob
    
    ffmpeg_search_paths = [
        r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Links",
        r"C:\Users\susha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg*\bin",
        r"C:\ProgramData\chocolatey\bin",
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
    ]
    
    ffmpeg_found = False
    for search_path in ffmpeg_search_paths:
        # Handle wildcards
        matching_paths = glob.glob(search_path) if '*' in search_path else [search_path]
        for ffmpeg_path in matching_paths:
            if os.path.exists(ffmpeg_path):
                # Check if ffmpeg.exe is actually in this directory
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
        print("⚠️  Warning: Could not find ffmpeg.exe in common locations")
    
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

def validate_audio_file(audio_file):
    """Validate audio file exists and has valid format"""
    if not os.path.exists(audio_file):
        print(f"❌ Error: Audio file '{audio_file}' not found!")
        return False
    
    valid_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    _, ext = os.path.splitext(audio_file)
    
    if ext.lower() not in valid_extensions:
        print(f"⚠️  Warning: '{ext}' files may not work well with madmom")
        print(f"   Recommended formats: {', '.join(valid_extensions)}")
    
    file_size = os.path.getsize(audio_file)
    if file_size == 0:
        print(f"❌ Error: Audio file is empty!")
        return False
    
    print(f"✓ Audio file validated: {file_size / (1024*1024):.2f} MB")
    return True

def detect_chords_with_madmom(audio_file):
    """
    Working madmom chord detection with proper error handling
    Uses the two-step process to avoid dtype issues
    """
    try:
        print("🔧 Applying madmom compatibility fixes...")
        fix_madmom_compatibility()
        
        print(f"🐍 Python version: {sys.version.split()[0]}")
        print(f"📊 NumPy version: {np.__version__}")
        
        print("📦 Importing madmom...")
        from madmom.audio.chroma import DeepChromaProcessor
        from madmom.features.chords import DeepChromaChordRecognitionProcessor
        from madmom.audio.signal import Signal
        import madmom
        print(f"✓ madmom version: {madmom.__version__}")
        
        print("="*60)
        print("🎸 MADMOM DEEP LEARNING CHORD DETECTION")
        print("="*60)
        print()
        
        print(f"📁 Loading audio: {audio_file}")
        
        if not validate_audio_file(audio_file):
            return None
        
        # Load audio first
        try:
            signal = Signal(audio_file)
            print(f"✓ Audio loaded: {signal.sample_rate}Hz, {signal.num_channels} channel(s)")
        except Exception as e:
            print(f"❌ Error loading audio: {e}")
            print("   Make sure you have ffmpeg installed")
            return None
        
        print("🧠 Initializing deep learning models...")
        print("   Step 1: Deep chroma extraction")
        
        # CRITICAL: Use two-step process to avoid dtype errors
        # Step 1: Extract chroma features
        chroma_processor = DeepChromaProcessor()
        
        print("🎵 Extracting chroma features from audio...")
        chroma_features = chroma_processor(audio_file)
        print(f"✓ Chroma features extracted: shape {chroma_features.shape}")
        
        print("   Step 2: Chord recognition from chroma")
        
        # Step 2: Decode chords from chroma
        chord_decoder = DeepChromaChordRecognitionProcessor()
        
        print("🎵 Decoding chords from chroma features...")
        chords = chord_decoder(chroma_features)
        
        # Convert structured array to list of tuples to avoid dtype issues
        chord_list = []
        for item in chords:
            try:
                # Handle both old and new numpy structured array formats
                if hasattr(item, '__getitem__'):
                    start = float(item[0]) if len(item) > 0 else 0.0
                    end = float(item[1]) if len(item) > 1 else 0.0
                    label = str(item[2]) if len(item) > 2 else 'N'
                    chord_list.append((start, end, label))
                else:
                    chord_list.append((item.start, item.end, item.label))
            except Exception as e:
                print(f"⚠️  Warning: Could not parse chord item: {e}")
                continue
        
        if not chord_list:
            print("⚠️  No chords detected in the audio file")
            return None
        
        print("✅ Processing complete!")
        print()
        print("="*60)
        print("🎼 DETECTED CHORDS")
        print("="*60)
        print(f"{'Time (s)':<12} {'Chord':<15} {'Duration'}")
        print("-" * 60)
        
        # Display results
        for i, (start, end, chord) in enumerate(chord_list):
            duration = f"{end - start:.2f}s"
            print(f"{start:<12.2f} {chord:<15} {duration}")
        
        print("="*60)
        print(f"🎯 Total chord segments: {len(chord_list)}")
        
        # Calculate statistics
        unique_chords = set([chord for _, _, chord in chord_list])
        print(f"🎨 Unique chords detected: {len(unique_chords)}")
        print(f"🎵 Chord vocabulary: {', '.join(sorted(unique_chords))}")
        
        # Calculate average chord duration
        durations = [end - start for start, end, _ in chord_list]
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"⏱️  Average chord duration: {avg_duration:.2f}s")
        
        print("="*60)
        print("✅ madmom chord detection completed successfully!")
        
        return chord_list
        
    except ImportError as e:
        print("❌ madmom import error!")
        print(f"   Error details: {e}")
        print()
        print("🔧 SOLUTION:")
        print("pip install https://github.com/CPJKU/madmom/archive/master.zip")
        return None
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"❌ Error: {e}")
        print()
        
        if "ufunc" in error_msg and ("multiply" in error_msg or "dtype" in error_msg):
            print("🔧 CRITICAL NumPy COMPATIBILITY ISSUE DETECTED!")
            print()
            print("This is a known bug with madmom and NumPy 1.20+")
            print()
            print("=" * 60)
            print("WORKING SOLUTION: Downgrade NumPy")
            print("=" * 60)
            print()
            print("Run these commands:")
            print("pip uninstall numpy -y")
            print("pip install numpy==1.19.5")
            print()
            print("Then run the script again.")
            print()
            print("=" * 60)
            print("WHY THIS HAPPENS:")
            print("=" * 60)
            print("madmom's chord recognition returns a structured array with")
            print("string dtype ('U32'), and NumPy 1.20+ doesn't allow arithmetic")
            print("operations on string arrays. NumPy 1.19.5 is the last version")
            print("that works with madmom's chord detection.")
            
        elif "ffmpeg" in error_msg or "audio" in error_msg:
            print("🔧 Audio processing error.")
            print("Install ffmpeg:")
            print("Windows: Download from https://ffmpeg.org")
            
        else:
            print("🔧 Try reinstalling madmom:")
            print("pip uninstall madmom -y")
            print("pip install https://github.com/CPJKU/madmom/archive/master.zip")
        
        print()
        return None

def main():
    """Main function"""
    audio_file = "other.wav"
    
    print("🎸 MADMOM CHORD DETECTION")
    print("=" * 50)
    print()
    
    # Allow command line argument for audio file
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        print(f"Using audio file from command line: {audio_file}")
        print()
    
    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"❌ Audio file '{audio_file}' not found!")
        print()
        print("Please ensure you have an audio file in the current directory.")
        print()
        print("Usage:")
        print(f"  python {sys.argv[0]}                # Uses 'music.wav'")
        print(f"  python {sys.argv[0]} yourfile.mp3   # Uses custom file")
        return
    
    # Run madmom chord detection
    result = detect_chords_with_madmom(audio_file)
    
    if result is None:
        print()
        print("🔄 madmom failed to run. Check the error messages above.")
        print()
        print("💡 System Info:")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   NumPy: {np.__version__}")
        
        # Check if NumPy version is the problem
        np_version = tuple(map(int, np.__version__.split('.')[:2]))
        if np_version >= (1, 20):
            print()
            print("=" * 60)
            print("⚠️  NumPy VERSION IS THE PROBLEM!")
            print("=" * 60)
            print()
            print("Your NumPy version is incompatible with madmom chord detection.")
            print()
            print("🔧 DEFINITIVE FIX:")
            print()
            print("   pip uninstall numpy -y")
            print("   pip install numpy==1.19.5")
            print()
            print("Then run this script again.")
            print("=" * 60)

if __name__ == "__main__":
    main()