"""
Auto-generated subtitles for NovaClips.
Uses faster-whisper to generate and burn subtitles.
"""

import logging
import math
from pathlib import Path
from typing import List

from faster_whisper import WhisperModel

from novaclips.config import settings
from .processor import VideoProcessor
from .ffmpeg_utils import run_ffmpeg

logger = logging.getLogger(__name__)


class Subtitler(VideoProcessor):
    """
    Generates and burns subtitles into video.
    """
    
    def __init__(self):
        super().__init__()
        # Use medium model for accurate Russian subtitle recognition
        # Quality is critical: "избранником" vs "испранником", "равновесие" vs "ромовесие"
        # Tradeoff: ~160s processing vs ~6s for small, but accuracy is worth it
        
        # Read from config if available, otherwise use defaults
        whisper_config = getattr(settings, 'whisper', {})
        
        self.model_size = whisper_config.get('MODEL_SIZE', 'medium')
        self.device = whisper_config.get('DEVICE', 'cpu')
        self.compute_type = whisper_config.get('COMPUTE_TYPE', 'int8')
        self.language = whisper_config.get('LANGUAGE', None)
        self.cpu_threads = whisper_config.get('CPU_THREADS', 0)  # 0 = auto-detect
        self.beam_size = whisper_config.get('BEAM_SIZE', 5)
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Generate and burn subtitles.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            
        Returns:
            True if successful, False otherwise
        """
        srt_path = None
        try:
            # Validate input
            if not self.validate_input(input_path):
                return False
            
            # Ensure output directory exists
            if not self.ensure_output_dir(output_path):
                return False
                
            # Define intermediate SRT path
            # output_path is like .../debug/06_subtitles.mp4
            # We want .../debug/06_subtitles.srt
            srt_path = output_path.with_suffix('.srt')
            
            # 1. Transcribe
            self.logger.info("Starting transcription...")
            # Extract audio for whisper? faster-whisper can read from video file directly via ffmpeg
            
            if not self._generate_srt(input_path, srt_path):
                return False
                
            # 2. Burn subtitles
            self.logger.info("Burning subtitles...")
            if not self._burn_subtitles(input_path, srt_path, output_path):
                return False
                
            self.last_params = {
                'engine': 'faster-whisper',
                'model_size': self.model_size,
                'generated_srt': str(srt_path)
            }
            
            # Keep SRT for debugging as requested
            self.logger.info(f"Saved debug subtitles to: {srt_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Subtitle processing failed: {e}", exc_info=True)
            return False

    def generate_srt(self, video_path: Path, srt_path: Path) -> List[tuple[float, float]]:
        """Public method to generate SRT. Returns list of (start, end) segments."""
        return self._generate_srt(video_path, srt_path)

    def _generate_srt(self, video_path: Path, srt_path: Path) -> List[tuple[float, float]]:
        """Generate SRT file using faster-whisper."""
        try:
            model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=self.cpu_threads if hasattr(self, 'cpu_threads') else 0
            )
            
            segments, info = model.transcribe(
                str(video_path),
                beam_size=self.beam_size if hasattr(self, 'beam_size') else 5,
                language=self.language if hasattr(self, 'language') else None,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                condition_on_previous_text=False
            )
            self.logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")

            # Consume generator to list so we can use it for both writing and returning
            segment_list = list(segments)
            has_segments = len(segment_list) > 0
            
            self.logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")

            with open(srt_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(segment_list, start=1):
                    # Format timestamp: HH:MM:SS,mmm
                    start = self._format_timestamp(segment.start)
                    end = self._format_timestamp(segment.end)
                    text = segment.text.strip()
                    
                    f.write(f"{i}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{text}\n\n")
            
            if not has_segments:
                self.logger.info("No speech detected (VAD filtered everything). Removed empty SRT.")
                srt_path.unlink(missing_ok=True)
                return []
                
            self.logger.info(f"SRT generated: {srt_path}")
            
            # Return simple list of (start, end) tuples
            return [(s.start, s.end) for s in segment_list]
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return []

    def _burn_subtitles(self, input_path: Path, srt_path: Path, output_path: Path) -> bool:
        """Burn SRT into video with FFmpeg."""
        try:
            # Build style string
            # Alignment: 2 (Bottom Center)
            s_conf = settings.subtitles
            font = s_conf.get('FONT', 'Arial')
            size = s_conf.get('SIZE', 24)
            color = s_conf.get('COLOR', 'white') # &HFFFFFF
            # FFmpeg standard colors or hex. 
            # Note: subtitles filter uses libass. 
            # Use ForceStyle.
            # Convert color names if needed, but simple names work often.
            
            # Simple ForceStyle
            style = (
                f"FontName={font},"
                f"FontSize={size},"
                f"PrimaryColour=&H00FFFFFF," # White in BGR (AABBGGRR) -> &H00FFFFFF (Solid White)
                f"OutlineColour=&H00000000," # Black
                f"BorderStyle=1," # Outline
                f"Outline={s_conf.get('OUTLINE_WIDTH', 2)},"
                f"Alignment=2" # Bottom Center
            )
            
            # Escape path for filter
            # Windows needs escaping, standard posix easy
            # Using absolute path for SRT is safest in ffmpeg filter
            # Filter syntax: subtitles=filename:force_style='...'
            # Path needs to be escaped: \: for colons, \\ for backslashes
            
            escaped_srt = str(srt_path).replace(":", "\\:").replace("'", "\\'")
            
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-vf', f"subtitles='{escaped_srt}':force_style='{style}'",
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-c:a', 'copy',
                '-y',
                str(output_path)
            ]
            
            description = "Burning subtitles"
            return run_ffmpeg(cmd, description)
            
        except Exception as e:
            self.logger.error(f"Burning subtitles failed: {e}")
            return False

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS,mmm format."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        mils = int((seconds - int(seconds)) * 1000)
        
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{mils:03d}"
