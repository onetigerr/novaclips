"""
Audio mixing for NovaClips.
Implements background music mixing.
"""

import logging
import random
from pathlib import Path
from typing import List

from novaclips.config import settings
from .processor import VideoProcessor
from .ffmpeg_utils import run_ffmpeg

logger = logging.getLogger(__name__)


class AudioMixer(VideoProcessor):
    """
    Mixes background music with original audio.
    Selects random track, loops it, and mixes at reduced volume.
    """
    
    def __init__(self):
        super().__init__()
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Mix background music.
        
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

            # Get music files
            music_files = self._get_music_files()
            if not music_files:
                self.logger.error(f"No music files found in {settings.music_dir}")
                return False
                
            # Select random track
            music_track = random.choice(music_files)
            self.logger.info(f"Selected music track: {music_track.name}")
            
            # Calculate volume
            volume_db = self._get_random_volume()
            # FFmpeg volume filter uses linear scale or dB.
            # "volume=-10dB" works.
            
            # Build command
            # -stream_loop -1 on input 1 (music) enables infinite looping
            # amix=inputs=2:duration=first ends when video ends
            
            # Filter complex:
            # [1:a]volume=VideoVolume[m];[0:a][m]amix=inputs=2:duration=first[a]
            # Since volume is string like "-10dB"
            
            filter_complex = f"[1:a]volume={volume_db}dB[m];[0:a][m]amix=inputs=2:duration=first[a]"
            
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-stream_loop', '-1',
                '-i', str(music_track),
                '-filter_complex', filter_complex,
                '-map', '0:v',   # Use video from input 0
                '-map', '[a]',   # Use mixed audio
                '-c:v', 'copy',  # Copy video stream (no re-encode needed if just changing audio)
                                 # WAIT: copy sometimes fails if timestamps bad. But here usually safe.
                                 # Let's stick to copy for speed, unless issues arise.
                '-c:a', 'aac',   # Encode audio
                '-b:a', '128k',
                '-y',
                str(output_path)
            ]
            
            description = f"Mixing audio with {music_track.name} at {volume_db}dB"
            
            success = run_ffmpeg(cmd, description)
            
            if success:
                # Also save the mixed audio track separately for debug
                try:
                    debug_audio_path = output_path.with_suffix('.aac')
                    # Extract audio from the output video we just created
                    # -vn = no video, -acodec copy
                    audio_cmd = [
                        'ffmpeg',
                        '-i', str(output_path),
                        '-vn',
                        '-c:a', 'copy',
                        '-y',
                        str(debug_audio_path)
                    ]
                    run_ffmpeg(audio_cmd, f"Extracting mixed audio to {debug_audio_path.name}")
                except Exception as ex:
                    self.logger.warning(f"Failed to save debug audio track: {ex}")

                self.last_params = {
                    'music_track': music_track.name,
                    'volume_db': volume_db
                }
                self.logger.info(f"Audio mix success: {music_track.name} ({volume_db}dB)")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Audio mixing failed: {e}", exc_info=True)
            return False

    def get_mixing_params(self) -> tuple[Path, float]:
        """
        Get info for mixing: (music_path, volume_db).
        Returns (None, 0) if no music found.
        """
        music_files = self._get_music_files()
        if not music_files:
            return None, 0
            
        track = random.choice(music_files)
        volume = self._get_random_volume()
        return track, volume

    def _get_music_files(self) -> List[Path]:
        """Get list of valid music files."""
        music_dir = settings.music_dir
        if not music_dir.exists():
            return []
            
        valid_exts = {'.mp3', '.wav', '.m4a', '.aac', '.flac'}
        return [
            f for f in music_dir.iterdir() 
            if f.is_file() and f.suffix.lower() in valid_exts
        ]

    def _get_random_volume(self) -> float:
        """Get random volume in dB."""
        min_db = settings.processing.get('AUDIO_VOLUME_MIN_DB', -12)
        max_db = settings.processing.get('AUDIO_VOLUME_MAX_DB', -8)
        
        return round(random.uniform(min_db, max_db), 1)
