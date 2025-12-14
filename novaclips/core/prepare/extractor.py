import logging
import subprocess
from pathlib import Path
from typing import List
from novaclips.core.processing.ffmpeg_utils import get_video_info

logger = logging.getLogger(__name__)

class FrameExtractor:
    """Extracts keyframes from video for analysis."""

    def extract_frames(self, video_path: Path, output_dir: Path, num_frames: int = 4) -> List[Path]:
        """
        Extracts N frames at evenly spaced intervals (avoiding start/end).
        Returns list of paths to extracted images.
        """
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        info = get_video_info(video_path)
        duration = info.get('duration', 0)
        
        if duration <= 0:
            logger.error(f"Invalid duration for {video_path}")
            return []

        # Points: 15%, 35%, 60%, 85% (roughly covering the narrative)
        # If num_frames is 4, we use these hardcoded ratios for best results.
        if num_frames == 4:
            ratios = [0.15, 0.35, 0.60, 0.85]
        else:
            # Fallback for dynamic N
            # range from 0.1 to 0.9
            step = 0.8 / (num_frames + 1)
            ratios = [0.1 + step * (i + 1) for i in range(num_frames)]

        extracted_paths = []
        
        for i, ratio in enumerate(ratios):
            timestamp = duration * ratio
            out_file = output_dir / f"frame_{i}.jpg"
            
            # Extract frame using ffmpeg
            # -ss before -i is faster (input seeking)
            cmd = [
                "ffmpeg",
                "-ss", str(timestamp),
                "-i", str(video_path),
                "-frames:v", "1",
                "-q:v", "2", # High quality jpeg
                "-y",
                str(out_file)
            ]
            
            try:
                subprocess.run(
                    cmd, 
                    check=True, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
                if out_file.exists():
                    extracted_paths.append(out_file)
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to extract frame at {timestamp}s: {e}")

        return extracted_paths
