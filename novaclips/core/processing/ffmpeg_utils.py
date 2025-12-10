"""
FFmpeg utility functions for video processing.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class FFmpegError(Exception):
    """Exception raised when FFmpeg operations fail."""
    pass


def get_video_info(video_path: Path) -> Dict:
    """
    Get video metadata using ffprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary containing video metadata including:
        - width: Video width in pixels
        - height: Video height in pixels
        - fps: Frame rate
        - duration: Duration in seconds
        - codec: Video codec name
        - audio_codec: Audio codec name
        
    Raises:
        FFmpegError: If ffprobe fails or video info cannot be retrieved
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,codec_name,duration',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(video_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        data = json.loads(result.stdout)
        
        # Extract video stream info
        if 'streams' not in data or len(data['streams']) == 0:
            raise FFmpegError(f"No video stream found in {video_path}")
        
        stream = data['streams'][0]
        
        # Parse frame rate (format: "30/1" or "30000/1001")
        fps_str = stream.get('r_frame_rate', '30/1')
        num, den = map(int, fps_str.split('/'))
        fps = num / den if den != 0 else 30.0
        
        # Get duration (try stream first, then format)
        duration = float(stream.get('duration', 0))
        if duration == 0 and 'format' in data:
            duration = float(data['format'].get('duration', 0))
        
        info = {
            'width': int(stream.get('width', 0)),
            'height': int(stream.get('height', 0)),
            'fps': round(fps, 2),
            'duration': round(duration, 2),
            'codec': stream.get('codec_name', 'unknown')
        }
        
        # Get audio codec if available
        cmd_audio = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name',
            '-of', 'json',
            str(video_path)
        ]
        
        result_audio = subprocess.run(cmd_audio, capture_output=True, text=True)
        if result_audio.returncode == 0:
            audio_data = json.loads(result_audio.stdout)
            if 'streams' in audio_data and len(audio_data['streams']) > 0:
                info['audio_codec'] = audio_data['streams'][0].get('codec_name', 'none')
            else:
                info['audio_codec'] = 'none'
        else:
            info['audio_codec'] = 'none'
        
        logger.debug(f"Video info for {video_path.name}: {info}")
        return info
        
    except subprocess.CalledProcessError as e:
        error_msg = f"ffprobe failed: {e.stderr}"
        logger.error(error_msg)
        raise FFmpegError(error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse ffprobe output: {e}"
        logger.error(error_msg)
        raise FFmpegError(error_msg)
    except Exception as e:
        error_msg = f"Failed to get video info: {e}"
        logger.error(error_msg)
        raise FFmpegError(error_msg)


def get_video_resolution(video_path: Path) -> Tuple[int, int]:
    """
    Get video resolution (width, height).
    
    Args:
        video_path: Path to video file
        
    Returns:
        Tuple of (width, height)
        
    Raises:
        FFmpegError: If resolution cannot be determined
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            str(video_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        width, height = map(int, result.stdout.strip().split('x'))
        return width, height
        
    except Exception as e:
        error_msg = f"Failed to get video resolution: {e}"
        logger.error(error_msg)
        raise FFmpegError(error_msg)


def calculate_crop_params(width: int, height: int) -> Optional[Tuple[int, int, int, int]]:
    """
    Calculate crop parameters to achieve 9:16 aspect ratio.
    
    Args:
        width: Current video width
        height: Current video height
        
    Returns:
        Tuple of (crop_width, crop_height, x_offset, y_offset) or None if already 9:16
    """
    target_ratio = 9 / 16  # 0.5625
    current_ratio = width / height
    
    # Allow 1% tolerance
    if abs(current_ratio - target_ratio) < 0.01:
        logger.debug(f"Video already has 9:16 aspect ratio ({width}x{height})")
        return None
    
    if current_ratio > target_ratio:
        # Video is too wide - crop width
        new_width = int(height * target_ratio)
        x_offset = (width - new_width) // 2
        logger.debug(f"Cropping width: {width}x{height} -> {new_width}x{height} (offset: {x_offset}, 0)")
        return (new_width, height, x_offset, 0)
    else:
        # Video is too tall - crop height
        new_height = int(width / target_ratio)
        y_offset = (height - new_height) // 2
        logger.debug(f"Cropping height: {width}x{height} -> {width}x{new_height} (offset: 0, {y_offset})")
        return (width, new_height, 0, y_offset)


def run_ffmpeg(cmd: list, description: str = "FFmpeg operation") -> bool:
    """
    Run an ffmpeg command.
    
    Args:
        cmd: FFmpeg command as list of arguments
        description: Description of the operation for logging
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Running {description}...")
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"{description} completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"{description} failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"{description} failed: {e}")
        return False
