"""
Video trimmer for NovaClips.
Implements smart trimming logic:
- Duration < 10s: Trim start only
- Duration >= 10s: Trim start and end
"""

import logging
import random
from pathlib import Path

from .processor import VideoProcessor
from .ffmpeg_utils import get_video_info, run_ffmpeg

logger = logging.getLogger(__name__)


class Trimmer(VideoProcessor):
    """
    Trims video edges to alter duration and timing metadata.
    Randomized trim amounts to ensure uniqueness.
    """
    
    def __init__(self):
        super().__init__()
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Trim video start/end.
        
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
            
            # Get video info for duration
            video_info = get_video_info(input_path)
            duration = video_info.get('duration', 0)
            
            if duration <= 0:
                self.logger.error("Invalid video duration")
                return False

            # Calculate trim parameters
            start_trim, end_trim = self._calculate_trim_amounts(duration)
            
            # Calculate new duration
            new_duration = duration - start_trim - end_trim
            if new_duration <= 0:
                self.logger.error(f"Trim amounts ({start_trim}+{end_trim}) exceed video duration ({duration})")
                return False
            
            # Build trim command
            # ffmpeg -ss [start] -i [input] -t [duration] -c copy [output]
            # using -c copy might be problematic if keyframes are not aligned perfectly.
            # But re-encoding is safer for precision. 
            # Given we are modifying the video stream anyway later (speed, zoom), re-encoding here is fine
            # or we can use stream copy if precision isn't critical.
            # However, for 0.5s precision, stream copy is often inaccurate.
            # Let's re-encode to be safe and accurate, or use fast re-encode.
            # Actually, `normalizer` already encoded to H.264.
            # If we want frame-accurate cut, we must re-encode (at least around cut points).
            # Simple re-encode is best for MVP reliability.
            
            # Wait, if we use -ss before -i, it seeks fast but might not be frame accurate for copy.
            # If we use -ss after -i, it's frame accurate but slow.
            # For short videos (<60s), decoding is fast enough.
            # Let's use filter complex "trim" or simply -ss and -t with re-encoding.
            
            cmd = [
                'ffmpeg',
                '-ss', str(start_trim),
                '-i', str(input_path),
                '-t', str(new_duration),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                str(output_path)
            ]
            
            description = (
                f"Trimming {input_path.name} "
                f"(Duration: {duration}s -> {new_duration:.2f}s, "
                f"Trim: Start={start_trim}s, End={end_trim}s)"
            )
            
            success = run_ffmpeg(cmd, description)
            
            if success:
                # Adjust SRT file timestamps if it exists
                # Subtitles were generated on the full video, now need to shift times
                self._adjust_srt_timestamps(output_path, start_trim)
                
                self.last_params = {
                    'start_trim': start_trim,
                    'end_trim': end_trim,
                    'original_duration': duration,
                    'new_duration': new_duration
                }
                self.logger.info(f"Trim success: -{start_trim}s start, -{end_trim}s end")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Trimming failed: {e}", exc_info=True)
            return False

    def get_trim_amounts(self, duration: float) -> tuple[float, float]:
        """Public method to calculate trim amounts."""
        return self._calculate_trim_amounts(duration)

    def _calculate_trim_amounts(self, duration: float) -> tuple[float, float]:
        """
        Calculate start and end trim amounts based on duration.
        
        Rules:
        - Duration < 10s: Trim 0.5s from start only
        - Duration >= 10s: Trim 0.5-1.0s from start AND 0.5-1.0s from end
        
        Returns:
            Tuple (start_trim, end_trim)
        """
        # Round to 2 decimals for cleaner logs/cmds
        if duration < 10:
            return 0.5, 0.0
        else:
            start_trim = round(random.uniform(0.5, 1.0), 2)
            end_trim = round(random.uniform(0.5, 1.0), 2)
            return start_trim, end_trim

    def _adjust_srt_timestamps(self, video_path: Path, start_trim: float) -> None:
        """
        Adjust SRT file timestamps after trimming video start.
        
        Since subtitles were generated on full video, all timestamps need
        to be shifted backward by start_trim amount.
        
        Args:
            video_path: Path to trimmed video file
            start_trim: Amount trimmed from start (in seconds)
        """
        # Find SRT file with same name as video
        srt_path = video_path.with_suffix('.srt')
        
        if not srt_path.exists():
            self.logger.debug(f"No SRT file found at {srt_path}, skipping adjustment")
            return
        
        try:
            self.logger.info(f"Adjusting SRT timestamps by -{start_trim}s")
            
            with open(srt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            adjusted_lines = []
            
            for line in lines:
                # Timeline format: 00:00:01,500 --> 00:00:03,200
                if '-->' in line:
                    parts = line.split('-->')
                    if len(parts) == 2:
                        start_time = self._parse_srt_timestamp(parts[0].strip())
                        end_time = self._parse_srt_timestamp(parts[1].strip())
                        
                        # Subtract start_trim from both timestamps
                        new_start = max(0, start_time - start_trim)
                        new_end = max(0, end_time - start_trim)
                        
                        # Format back to SRT timestamp
                        adjusted_line = f"{self._format_srt_timestamp(new_start)} --> {self._format_srt_timestamp(new_end)}\n"
                        adjusted_lines.append(adjusted_line)
                    else:
                        adjusted_lines.append(line)
                else:
                    adjusted_lines.append(line)
            
            # Write adjusted SRT
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.writelines(adjusted_lines)
            
            self.logger.info(f"SRT timestamps adjusted successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to adjust SRT timestamps: {e}", exc_info=True)
    
    def _parse_srt_timestamp(self, timestamp: str) -> float:
        """Parse SRT timestamp (HH:MM:SS,mmm) to seconds."""
        # Remove any whitespace
        timestamp = timestamp.strip()
        
        # Split by comma to separate seconds and milliseconds
        parts = timestamp.split(',')
        if len(parts) != 2:
            return 0.0
        
        time_part = parts[0]  # HH:MM:SS
        ms_part = parts[1]    # mmm
        
        # Split time part
        time_components = time_part.split(':')
        if len(time_components) != 3:
            return 0.0
        
        hours = int(time_components[0])
        minutes = int(time_components[1])
        seconds = int(time_components[2])
        milliseconds = int(ms_part)
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
        return total_seconds
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

