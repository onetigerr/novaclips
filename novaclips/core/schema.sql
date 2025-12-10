CREATE TABLE IF NOT EXISTS media_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Source Info
    source_type TEXT NOT NULL,       -- 'telegram', 'local', 'tiktok'
    source_id TEXT,                  -- specific channel ID or unique source identifier
    original_filename TEXT NOT NULL, -- basename of the file
    
    -- Processing Info
    content_hash TEXT,               -- MD5 or similar to detect duplicates
    duration_seconds INTEGER,
    
    -- Lifecycle
    status TEXT NOT NULL DEFAULT 'raw', -- raw, clean, ready, uploaded, failed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    uploaded_at DATETIME,
    
    -- Paths (Relative to ROOT_DIR)
    raw_path TEXT,
    clean_path TEXT,
    ready_path TEXT,
    
    -- Upload Info
    upload_channel TEXT,             -- Which channel it was uploaded to
    upload_url TEXT,                 -- YouTube URL
    upload_metadata TEXT,            -- JSON dump of title, tags, description
    
    -- Error tracking
    processing_error TEXT            -- Error message if processing failed
);

CREATE INDEX IF NOT EXISTS idx_content_hash ON media_items(content_hash);
CREATE INDEX IF NOT EXISTS idx_status ON media_items(status);
