"""
Video normalization for NovaClips.

Normalizes videos to 1080x1920 (9:16), 30fps, H.264/AAC/MP4.
Filters out horizontal videos and corrects aspect ratios.
"""

import logging
from pathlib import Path
from typing import Optional

from .processor import VideoProcessor
from .ffmpeg_utils import (
    FFmpegError,
    get_video_info,
    get_video_resolution,
    calculate_crop_params,
    run_ffmpeg
)
from novaclips.config import settings

logger = logging.getLogger(__name__)


class Normalizer(VideoProcessor):
    """
    Normalizes videos to standard format for YouTube Shorts.
    
    - Rejects horizontal videos (width > height)
    - Corrects aspect ratio to 9:16 by cropping
    - Scales to 1080x1920
    - Normalizes to 30fps
    - Converts to H.264/AAC/MP4
    - Removes all metadata
    """
    
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    TARGET_FPS = 30
    
    def __init__(self):
        super().__init__()
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Normalize a video file.
        
        Args:
            input_path: Path to input video
            output_path: Path for output video
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate input
            if not self.validate_input(input_path):
                return False
            
            # Ensure output directory exists
            if not self.ensure_output_dir(output_path):
                return False
            
            # Get video info
            self.logger.info(f"Analyzing video: {input_path.name}")
            try:
                video_info = get_video_info(input_path)
            except FFmpegError as e:
                self.logger.error(f"Failed to get video info: {e}")
                return False
            
            width = video_info['width']
            height = video_info['height']
            
            # Check dimensions and orientation
            if not self._validate_dimensions(width, height):
                return False
            
            # Build FFmpeg filter chain
            filters = self.get_filter_chain(width, height)
            
            # Run FFmpeg normalization
            return self._run_normalization(input_path, output_path, filters)
            
        except Exception as e:
            self.logger.error(f"Normalization failed: {e}", exc_info=True)
            return False
    
    def _validate_dimensions(self, width: int, height: int) -> bool:
        """
        Validate video dimensions and orientation.
        Rejects horizontal videos and those below minimum resolution.
        
        Args:
            width: Video width
            height: Video height
            
        Returns:
            True if valid, False otherwise
        """
        # 1. Check orientation
        if width > height:
            self.logger.warning(
                f"Rejecting horizontal video: {width}x{height}. "
                "Only vertical videos are supported."
            )
            return False
            
        # 2. Check minimum resolution
        min_h = settings.processing.get('MIN_RESOLUTION_HEIGHT', 800)
        min_w = settings.processing.get('MIN_RESOLUTION_WIDTH', 450)
        
        if height < min_h:
            self.logger.warning(
                f"Rejecting video with low height: {height}px < {min_h}px"
            )
            return False
            
        if width < min_w:
            self.logger.warning(
                f"Rejecting video with low width: {width}px < {min_w}px"
            )
            return False
        
        self.logger.info(f"Video dimensions valid: {width}x{height} (Vertical, >{min_w}x{min_h}) ✓")
        return True
    
    def get_filter_chain(self, width: int, height: int) -> str:
        """
        Public method to get normalization filters.
        """
        return self._build_filter_chain(width, height)

    def _build_filter_chain(self, width: int, height: int) -> str:
        """
        Build FFmpeg filter chain for normalization.
        
        Args:
            width: Current video width
            height: Current video height
            
        Returns:
            FFmpeg filter string
        """
        filters = []
        
        # Step 1: Crop to 9:16 if needed
        crop_params = calculate_crop_params(width, height)
        if crop_params:
            crop_w, crop_h, x_offset, y_offset = crop_params
            filters.append(f"crop={crop_w}:{crop_h}:{x_offset}:{y_offset}")
            self.logger.info(f"Will crop to {crop_w}x{crop_h} (offset: {x_offset}, {y_offset})")
        
        # Step 2: Scale to target resolution
        filters.append(f"scale={self.TARGET_WIDTH}:{self.TARGET_HEIGHT}")
        self.logger.info(f"Will scale to {self.TARGET_WIDTH}x{self.TARGET_HEIGHT}")
        
        # Step 3: Normalize FPS
        filters.append(f"fps={self.TARGET_FPS}")
        self.logger.info(f"Will normalize FPS to {self.TARGET_FPS}")
        
        return ','.join(filters)
    
    def _run_normalization(
        self,
        input_path: Path,
        output_path: Path,
        filters: str
    ) -> bool:
        """
        Run FFmpeg normalization command.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            filters: FFmpeg filter string
            
        Returns:
            True if successful, False otherwise
        """
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-vf', filters,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-map_metadata', '-1',  # Remove all metadata
            '-movflags', '+faststart',
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        description = f"Normalizing {input_path.name}"
        return run_ffmpeg(cmd, description)
