"""
Video speed adjustment for NovaClips.
Implements random speed variation (±3-7%) to alter fingerprints.
"""

import logging
import random
from pathlib import Path

from novaclips.config import settings
from .processor import VideoProcessor
from .ffmpeg_utils import run_ffmpeg

logger = logging.getLogger(__name__)


class SpeedChanger(VideoProcessor):
    """
    Applies subtle speed modifications to alter timing and audio fingerprints.
    """
    
    def __init__(self):
        super().__init__()
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Change video speed.
        
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

            # Calculate speed factor
            speed_factor = self._calculate_speed_factor()
            
            # Build filter chain
            # Video: setpts=PTS/FACTOR
            # Audio: atempo=FACTOR
            # Note: setpts uses inverse logic (smaller PTS = faster playback)
            # If factor > 1 (faster), PTS should be smaller -> PTS * (1/factor)
            
            video_filter = f"setpts=PTS/{speed_factor}"
            audio_filter = f"atempo={speed_factor}"
            
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-filter:v', video_filter,
                '-filter:a', audio_filter,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                str(output_path)
            ]
            
            description = f"Adjusting speed by factor {speed_factor:.3f}x ({input_path.name})"
            
            success = run_ffmpeg(cmd, description)
            
            if success:
                self.last_params = {'speed_factor': speed_factor}
                self.logger.info(f"Speed adjustment success: {speed_factor:.3f}x")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Speed adjustment failed: {e}", exc_info=True)
            return False

    def get_speed_factor(self) -> float:
        """Public method to get speed factor."""
        return self._calculate_speed_factor()

    def _calculate_speed_factor(self) -> float:
        """
        Calculate random speed factor.
        
        Range: ±3–7% (defined in config)
        
        Returns:
            Speed factor (e.g., 0.95 or 1.05)
        """
        min_pct = settings.processing.get('SPEED_MIN_PERCENT', 3)
        max_pct = settings.processing.get('SPEED_MAX_PERCENT', 7)
        
        # Determine direction: +1 (faster) or -1 (slower)
        direction = 1 if random.random() > 0.5 else -1
        
        # Calculate percentage
        percent = random.uniform(min_pct, max_pct)
        
        # Calculate factor
        # If faster: 1.0 + 0.05 = 1.05
        # If slower: 1.0 - 0.05 = 0.95
        factor = 1.0 + (direction * (percent / 100.0))
        
        return round(factor, 4)
