import logging
import shutil
from pathlib import Path
from novaclips.core.dao import MediaDAO

logger = logging.getLogger(__name__)

class FileRenamer:
    """Handles renaming of files and DB updates."""
    
    def __init__(self, dao: MediaDAO):
        self.dao = dao

    def rename_item(self, item_id: int, current_path: Path, new_slug: str) -> Path:
        """
        Renames file to {id}_{slug}.mp4
        Updates DB record.
        Returns new path.
        """
        try:
            # Construct new filename
            # Keep extension
            ext = current_path.suffix
            new_filename = f"{item_id}_{new_slug}{ext}"
            new_path = current_path.parent / new_filename
            
            if new_path == current_path:
                return current_path
                
            # Rename file
            current_path.rename(new_path)
            
            # Check for sidecar files (like .srt)
            # if we have {old}.srt, rename to {new}.srt
            old_srt = current_path.with_suffix('.srt')
            if old_srt.exists():
                new_srt = new_path.with_suffix('.srt')
                old_srt.rename(new_srt)

            logger.info(f"Renamed {current_path.name} -> {new_path.name}")
            return new_path
            
        except Exception as e:
            logger.error(f"Failed to rename file: {e}")
            return current_path
