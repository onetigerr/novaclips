import logging
from typing import Optional, List
from novaclips.core.db import DatabaseManager
from novaclips.core.models import MediaItem

logger = logging.getLogger(__name__)

class MediaDAO:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def add_item(self, item: MediaItem) -> int:
        """Insert a new media item and return its ID."""
        query = """
            INSERT INTO media_items (
                source_type, source_id, original_filename, 
                status, content_hash, raw_path
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            item.source_type, item.source_id, item.original_filename,
            item.status, item.content_hash, item.raw_path
        )
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            item.id = cursor.lastrowid
            return item.id

    def get_by_hash(self, content_hash: str) -> Optional[MediaItem]:
        """Find an item by its content hash (duplicate check)."""
        query = "SELECT * FROM media_items WHERE content_hash = ?"
        row = self.db.fetch_one(query, (content_hash,))
        if row:
            return MediaItem.from_row(row)
        return None

    def get_pending_raw(self) -> List[MediaItem]:
        """Get items ready for processing (status='raw')."""
        return self._get_by_status('raw')

    def get_pending_upload(self) -> List[MediaItem]:
        """Get items ready for upload (status='ready')."""
        return self._get_by_status('ready')

    def _get_by_status(self, status: str) -> List[MediaItem]:
        query = "SELECT * FROM media_items WHERE status = ?"
        rows = self.db.fetch_all(query, (status,))
        return [MediaItem.from_row(row) for row in rows]

    def update_status(self, item_id: int, new_status: str, **kwargs):
        """
        Update status and optionally other fields (passed as kwargs matching column names).
        Example: update_status(1, 'clean', clean_path='/tmp/foo.mp4', processed_at=datetime.now())
        """
        set_parts = ["status = ?"]
        values = [new_status]
        
        for key, value in kwargs.items():
            set_parts.append(f"{key} = ?")
            values.append(value)
            
        values.append(item_id) # For WHERE clause
        
        query = f"UPDATE media_items SET {', '.join(set_parts)} WHERE id = ?"
        
        self.db.execute_query(query, tuple(values))
