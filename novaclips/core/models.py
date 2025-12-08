from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(kw_only=True)
class MediaItem:
    id: Optional[int] = None
    source_type: str
    source_id: Optional[str] = None
    original_filename: str
    status: str = "raw"
    content_hash: Optional[str] = None
    duration_seconds: Optional[int] = None
    
    # Paths (stored as strings relative to root)
    raw_path: Optional[str] = None
    clean_path: Optional[str] = None
    ready_path: Optional[str] = None
    
    # Upload info
    upload_channel: Optional[str] = None
    upload_url: Optional[str] = None
    upload_metadata: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    uploaded_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: dict):
        """Factory method to create instance from sqlite3.Row"""
        row_data = dict(row)
        # Filter out keys that are not in the dataclass fields
        # This prevents crashes if DB has extra columns (forward compatibility)
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in row_data.items() if k in valid_keys}
        return cls(**filtered_data)
