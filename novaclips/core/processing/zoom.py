"""
Video zoom effect for NovaClips.
Implements linear zoom-in from center.
"""

import logging
from pathlib import Path

from novaclips.config import settings
from .processor import VideoProcessor
from .ffmpeg_utils import get_video_info, run_ffmpeg

logger = logging.getLogger(__name__)


class Zoomer(VideoProcessor):
    """
    Applies subtle zoom-in effects to create visual differentiation.
    Zoom amount is interpolated based on video duration.
    """
    
    def __init__(self):
        super().__init__()
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Apply zoom-in effect.
        
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
                self.logger.error("Invalid video duration for zoom")
                return False

            # Calculate zoom percentage
            zoom_pct = self._calculate_zoom_percentage(duration)
            
            # Build filter
            # z='1+(on/(30*DURATION))*PCT'
            # x='iw/2-(iw/zoom/2)'
            # y='ih/2-(ih/zoom/2)'
            # d=DURATION*30
            # s=1080x1920 (Ensure output resolution is maintained)
            
            fps = 30  # Assumed from normalization
            total_frames = int(duration * fps) + 100 # Add buffer
            
            # Expression: 1 + (on / (duration * 30)) * zoom_pct
            # Note: 'on' starts at 0.
            # We use 'time' -> 'time' is in seconds.
            # z = 1 + (time / duration) * zoom_pct
            
            zoom_expr = f"1+(time/{duration})*{zoom_pct}"
            
            filters = (
                f"zoompan="
                f"z='{zoom_expr}':"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"d={total_frames}:"
                f"s=1080x1920:"
                f"fps={fps}"
            )
            
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-vf', filters,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'copy', # Copy audio as zoom doesn't affect it
                '-y',
                str(output_path)
            ]
            
            description = f"Applying zoom-in (Max {zoom_pct*100:.1f}%) to {input_path.name}"
            
            success = run_ffmpeg(cmd, description)
            
            if success:
                self.last_params = {
                    'zoom_percentage': zoom_pct,
                    'duration': duration
                }
                self.logger.info(f"Zoom success: {zoom_pct*100:.2f}% over {duration}s")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Zoom effect failed: {e}", exc_info=True)
            return False

    def _calculate_zoom_percentage(self, duration: float) -> float:
        """
        Calculate zoom percentage based on duration using linear interpolation.
        
        Points:
        - 10s: 4% (0.04)
        - 20s: 5% (0.05)
        - 40s: 6% (0.06)
        - 80s: 7% (0.07)
        """
        # Define points (seconds, factor)
        points = [
            (10, settings.processing.get('ZOOM_FACTOR_10S', 0.04)),
            (20, settings.processing.get('ZOOM_FACTOR_20S', 0.05)),
            (40, settings.processing.get('ZOOM_FACTOR_40S', 0.06)),
            (80, settings.processing.get('ZOOM_FACTOR_80S', 0.07))
        ]
        
        # Sort just in case
        points.sort(key=lambda x: x[0])
        
        # Handle edges
        if duration <= points[0][0]:
            return points[0][1]
        if duration >= points[-1][0]:
            return points[-1][1]
            
        # Linear interpolation
        for i in range(len(points) - 1):
            t1, v1 = points[i]
            t2, v2 = points[i+1]
            
            if t1 <= duration < t2:
                # Interpolate
                # v = v1 + (v2 - v1) * (duration - t1) / (t2 - t1)
                
                ratio = (duration - t1) / (t2 - t1)
                value = v1 + (v2 - v1) * ratio
                return round(value, 4)
                
        return points[-1][1] # Should be covered by edges check but for safety
