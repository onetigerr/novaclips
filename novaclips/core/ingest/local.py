import hashlib
import shutil
import logging
from pathlib import Path
from typing import List, Optional
from novaclips.core.ingest.base import IngestStrategy
from novaclips.core.dao import MediaDAO
from novaclips.core.models import MediaItem

logger = logging.getLogger(__name__)

class LocalIngest(IngestStrategy):
    def __init__(self, dao: MediaDAO, source_dir: Path):
        self.dao = dao
        self.source_dir = source_dir
        # Move to config
        from novaclips.config import settings
        self.raw_dir = settings.raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def scan(self) -> List[Path]:
        """Scans source directory for video files."""
        if not self.source_dir.exists():
            logger.warning(f"Source directory {self.source_dir} does not exist.")
            return []

        video_extensions = {'.mp4', '.mov', '.avi', '.mkv'}
        found_files = []
        
        for file_path in self.source_dir.glob('*'):
            if file_path.suffix.lower() in video_extensions:
                found_files.append(file_path)
                
        return found_files

    def calculate_hash(self, file_path: Path) -> str:
        """Calculates SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to avoid memory issues with large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def process_file(self, file_path: Path) -> Optional[int]:
        """
        Ingests a single file: check hash -> copy -> save to DB.
        Returns ID of new item or None if duplicate/failed.
        """
        try:
            file_hash = self.calculate_hash(file_path)
            
            # Check for duplicate
            if self.dao.get_by_hash(file_hash):
                logger.info(f"Skipping duplicate: {file_path.name}")
                return None

            # Copy to raw
            target_path = self.download(file_path)
            
            # Create DB entry
            item = MediaItem(
                source_type="local",
                original_filename=file_path.name,
                status="raw",
                content_hash=file_hash,
                raw_path=str(target_path)
            )
            item_id = self.dao.add_item(item)
            logger.info(f"Ingested {file_path.name} as ID {item_id}")
            return item_id

        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")
            return None

    def download(self, item: Path) -> Path:
        """Copies file to raw directory."""
        # Use simple timestamp prefix to avoid name collisions in raw
        # In a real app we might use UUID or ID
        import time
        timestamp = int(time.time())
        target_filename = f"{timestamp}_{item.name}"
        target_path = self.raw_dir / target_filename
        
        shutil.copy2(item, target_path)
        return target_path
