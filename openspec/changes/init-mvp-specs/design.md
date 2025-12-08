## Context
The system needs a lightweight state tracking mechanism and a consistent filesystem organization for the media pipeline. As per the MVP definition, we will use SQLite and local directories.

## Decisions

### 1. Database Schema (`novaclips.db`)
We will use a single main table `media_items` to track the lifecycle of each video.

```sql
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
    upload_metadata TEXT             -- JSON dump of title, tags, description
);

CREATE INDEX IF NOT EXISTS idx_content_hash ON media_items(content_hash);
CREATE INDEX IF NOT EXISTS idx_status ON media_items(status);
```

### 2. File System Structure
We will enforce a strict directory structure relative to the project root (or a configured data root).

```
data/
├── db/
│   └── novaclips.db
├── storage/
│   ├── raw/        # Ingested files (original)
│   ├── clean/      # Normalized (9:16, no metadata)
│   └── ready/      # Finalized with overlays/CTA, ready for upload
├── logs/
│   └── app.log
└── sessions/       # Browser cookies and telegram sessions
```

### 3. CLI Command Structure
Using `argparse` or `click`.

- `novaclips ingest [source]`
- `novaclips process [step]` 
- `novaclips upload`
- `novaclips list` (show DB status)

### 4. Browser & Proxy Infrastructure
- **Browser**: AdsPower (Anti-detect browser).
- **Automation**: Playwright (connecting via CDP/WebSocket to AdsPower).
- **Proxy**: Managed inside AdsPower profiles. The app does not handle proxy chains directly, it just requests the profile launch.

## Open Questions
- **Proxy Management**: For MVP Phase 0, we might skip complex proxy binding in DB and use environment variables, but the schema should eventually support it.
