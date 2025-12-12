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
    transform_params TEXT,           -- JSON dump of applied uniquification params
    
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
│   ├── ready/      # Finalized with overlays/CTA, ready for upload
│   └── debug/      # Intermediate files (step-by-step debug output)
├── logs/
│   └── app.log
├── sessions/       # Browser cookies and telegram sessions
└── music/          # Royalty-free music tracks for mixing
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

### 5. MVP Uniquification Strategy
To avoid content fingerprinting and "Reused Content" strikes, the MVP implements 6 transformation techniques. 
**Order of operations:**
1. Validation (Min 800x450)
2. Normalization (1080x1920, 30fps)
3. Smart Trimming
4. Speed Adjustment
5. Zoom Effect
6. Audio Mixing
7. Subtitles

#### 5.1 Validation & Normalization
- **Rule**: Reject videos smaller than 800px height OR 450px width
- **Action**: Scale/Crop to 1080x1920 (9:16), 30fps

#### 5.2 Smart Trimming
- **Logic**:
    - Duration < 10s: Trim 0.5s from start
    - Duration >= 10s: Trim 0.5-1.0s (random) from start AND 0.5-1.0s (random) from end

#### 5.3 Speed Variation
- **Range**: ±3–7% (random)
- **Implementation**: `setpts` (video) + `atempo` (audio)

#### 5.4 Auto Zoom Effects
- **Effect**: Linear Zoom-In from center (0% -> X%)
- **Amount**: Linear interpolation based on original duration
#### 4. Random Fade (Replaces Zoom)
- **Goal**: Alter visual signature at boundaries.
- **Tech**: FFmpeg `fade` filter.
- **Param**: 
    - In: `fade=t=in:st=0:d=DURATION`
    - Out: `fade=t=out:st=END_TIME:d=DURATION`
- **Logic**:
    - Duration: Random 0.2-0.5s.
- **Note**: Zoom effect is currently deferred due to performance and debugging needs.

### 5. Audio Mixing
- **Goal**: Alter audio fingerprint.
- **Tech**: FFmpeg `amix`.
- **Logic**:
    - Loop background track.
    - Mix at -8dB to -12dB.
    - Random track selection.

### 6. Auto-Subtitles
- **Goal**: Add visual text layer.
- **Tech**: `faster-whisper` -> SRT -> FFmpeg `subtitles` filter.
- **Logic**:
    - Transcribe on CPU.
    - Burn-in styles from config.
    - Save SRT for debug.ned in `config.yaml` (font, size, color)

#### Implementation Notes
- **Debug Mode**: Save intermediate files to `data/storage/debug/` after each step for inspection.
- **Production Mode**: Combine into a unified FFmpeg filter graph where possible, but distinct steps are acceptable for MVP stability.
- **Logging**: Save all random parameters (speed factor, trim amounts, chosen music track) to `media_items.transform_params` JSON column.

## Open Questions
- **Proxy Management**: For MVP Phase 0, we might skip complex proxy binding in DB and use environment variables, but the schema should eventually support it.

