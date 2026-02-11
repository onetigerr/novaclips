#!/usr/bin/env python3
"""
Script to normalize volume across multiple audio chunks and merge them
into a single file using FFmpeg's dynaudnorm filter.
"""

import os
import sys
import glob
import subprocess
from pathlib import Path

# Configuration
AUDIO_DIR = Path("data/audio/LLMs-explained")
OUTPUT_FILENAME = "Algenib_full_normalized.wav"
INPUT_PATTERN = "Algenib_part_*.wav"

# FFmpeg speechnorm filter settings (optimized for speech)
# e: Expansion factor (default 12.5). Higher = more aggressive suppression of silence/noise.
# r: Raise amount (default 0.001). Lower = less noise boost.
# l: Link channels (default 1).
DYNAUDNORM_FILTER = "speechnorm=e=50.0:r=0.0005:l=1"


def main():
    project_root = Path(__file__).resolve().parent.parent
    audio_path = project_root / AUDIO_DIR
    output_path = audio_path / OUTPUT_FILENAME
    
    print(f"Searching for files in: {audio_path}")
    
    # 1. Find all matching files
    files = sorted(audio_path.glob(INPUT_PATTERN), key=lambda x: int(x.stem.split('_')[-1]))
    
    if not files:
        print(f"Error: No files found matching {INPUT_PATTERN}")
        sys.exit(1)
        
    print(f"Found {len(files)} files:")
    for f in files:
        print(f"  - {f.name}")
        
    # 2. Create input list for ffmpeg
    list_file_path = audio_path / "ffmpeg_list.txt"
    with open(list_file_path, "w") as f:
        for audio_file in files:
            # ffmpeg requires safe filenames or absolute paths
            f.write(f"file '{audio_file.absolute()}'\n")
            
    print(f"\nCreated file list: {list_file_path}")
    
    # 3. Construct FFmpeg command
    # -f concat: Use concat demuxer
    # -safe 0: Allow unsafe file paths (absolute paths)
    # -i list.txt: Input list
    # -af ...: Audio filter graph
    cmd = [
        "ffmpeg",
        "-y",               # Overwrite output
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file_path),
        "-af", DYNAUDNORM_FILTER,
        str(output_path)
    ]
    
    print("\nRunning FFmpeg command:")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✓ Successfully created normalized audio: {output_path}")
        
        # Cleanup
        os.remove(list_file_path)
        print("  Cleaned up temporary list file.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ FFmpeg failed with error code {e.returncode}")
        print("Ensure ffmpeg is installed and in your PATH.")
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ FFmpeg executable not found. Please install ffmpeg.")
        sys.exit(1)


if __name__ == "__main__":
    main()
