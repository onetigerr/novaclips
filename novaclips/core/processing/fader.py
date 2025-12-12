"""
Video fade-in and fade-out effect for NovaClips.
Implements random fade duration at start and end.
"""

import logging
import random
from pathlib import Path

from novaclips.config import settings
from .processor import VideoProcessor
from .ffmpeg_utils import get_video_info, run_ffmpeg

logger = logging.getLogger(__name__)


class Fader(VideoProcessor):
    """
    Applies fade-in and fade-out effects to alter visual signature.
    Duration is randomized: 
    - < 10s: 0.2s fade
    - >= 10s: 0.2s-0.5s fade
    """
    
    def __init__(self):
        super().__init__()
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Apply fade-in/out effect.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            
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

            # Get video duration
            video_info = get_video_info(input_path)
            duration = video_info.get('duration', 0)
            
            if duration <= 0:
                self.logger.error("Invalid video duration for fade")
                return False

            # Calculate fade duration
            fade_duration = self._calculate_fade_duration(duration)
            
            # Start time for fade out
            # We want to fade out at the very end.
            start_fade_out = duration - fade_duration
            
            # Filters:
            # fade=t=in:st=0:d=FAST_DURATION
            # fade=t=out:st=START_FADE_OUT:d=FAST_DURATION
            
            # Chaining filters
            # [0:v]fade=t=in...[v1];[v1]fade=t=out...[v2]
            # Simplest is comma separated if single chain
            
            filters = (
                f"fade=t=in:st=0:d={fade_duration},"
                f"fade=t=out:st={start_fade_out}:d={fade_duration}"
            )
            
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-vf', filters,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'copy', # Copy audio
                '-y',
                str(output_path)
            ]
            
            description = f"Applying fade in/out ({fade_duration}s) to {input_path.name}"
            
            success = run_ffmpeg(cmd, description)
            
            if success:
                self.last_params = {
                    'fade_duration': fade_duration,
                    'fade_in_start': 0,
                    'fade_out_start': start_fade_out
                }
                self.logger.info(f"Fade success: {fade_duration}s in/out")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Fade effect failed: {e}", exc_info=True)
            return False

    def get_fade_duration(self, duration: float) -> float:
        """Public method to calculate fade duration."""
        return self._calculate_fade_duration(duration)

    def _calculate_fade_duration(self, duration: float) -> float:
        """
        Calculate fade duration.
        """
        if duration < 10:
            return 0.2
        else:
            return round(random.uniform(0.2, 0.5), 2)
