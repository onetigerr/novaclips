"""
Verification script for Video Uniquification Pipeline.
"""

import os
import shutil
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from novaclips.core.processing.uniquifier import Uniquifier
from novaclips.config import settings
from novaclips.core.processing.ffmpeg_utils import run_ffmpeg

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verifier")

def generate_dummy_assets():
    """Generate dummy video and music."""
    # Ensure dirs
    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    settings.music_dir.mkdir(parents=True, exist_ok=True)
    
    # Dummy video (vertical, 15s)
    video_path = settings.raw_dir / 'test_video.mp4'
    if not video_path.exists():
        logger.info("Generating dummy video...")
        cmd = [
            'ffmpeg',
            '-f', 'lavfi', '-i', 'testsrc=duration=15:size=1080x1920:rate=30',
            '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=15',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-y', str(video_path)
        ]
        run_ffmpeg(cmd, "Generating dummy video")
        
    # Dummy music logic
    music_file = settings.music_dir / 'test_music.mp3'
    if not any(settings.music_dir.iterdir()):
        logger.info("Generating dummy music...")
        cmd = [
            'ffmpeg',
            '-f', 'lavfi', '-i', 'sine=frequency=440:duration=30',
            '-c:a', 'libmp3lame', '-b:a', '128k',
            '-y', str(music_file)
        ]
        run_ffmpeg(cmd, "Generating dummy music")
        
    return video_path

import argparse

def verify_pipeline(input_file: Path = None):
    if input_file:
        video_path = Path(input_file)
        if not video_path.exists():
            logger.error(f"Input file not found: {video_path}")
            return
    else:
        video_path = generate_dummy_assets()
        
    # Use clean_dir for output
    settings.clean_dir.mkdir(parents=True, exist_ok=True)
    output_path = settings.clean_dir / 'final_output.mp4'
    
    logger.info(f"Using input video: {video_path}")
    logger.info("Initializing Uniquifier...")
    uniquifier = Uniquifier()
    
    logger.info("Running pipeline...")
    success = uniquifier.process(video_path, output_path)
    
    if success:
        logger.info("Pipeline SUCCESS!")
        logger.info(f"Final output: {output_path}")
        logger.info("Params JSON:")
        params = uniquifier.get_last_transform_params()
        print(params)
        
        # Verify debug files
        debug_files = list(settings.debug_dir.glob("*"))
        logger.info(f"Debug files generated in {settings.debug_dir}: {len(debug_files)}")
        for f in sorted(debug_files):
            if f.is_file():
                logger.info(f" - {f.name} ({f.stat().st_size} bytes)")
    else:
        logger.error("Pipeline FAILED.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify uniquification pipeline")
    parser.add_argument("--input", help="Path to input video file (optional)")
    args = parser.parse_args()
    
    try:
        verify_pipeline(args.input)
    finally:
        pass

