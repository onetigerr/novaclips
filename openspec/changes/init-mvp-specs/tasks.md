## 1. Foundation & Media Management
- [ ] 1.1 Initialize project structure (dirs: `data/storage/{raw,clean,ready}`, `data/db`)
- [ ] 1.2 Implement Database Manager (SQLite connection, `schema.sql` application)
- [ ] 1.3 Create `MediaItem` dataclass and DAO (Data Access Object) methods (add, update, get_by_hash)

## 2. CLI Framework
- [ ] 2.1 Scaffold `main.py` with `click` or `argparse`
- [ ] 2.2 Implement basic command registration (`ingest`, `process`, `upload`)

## 3. Ingestion
- [ ] 3.1 Implement `LocalIngest` strategies (scan folder, hash check, copy to raw)
- [ ] 3.2 Implement `TelegramIngest` using Telethon (auth flow, fetch history, download media)

## 4. Processing
- [ ] 4.1 Implement `VideoProcessor` base class
- [ ] 4.2 Add `ffmpeg-python` normalization logic (scale 1080x1920, 30fps)
- [ ] 4.3 Add metadata stripping logic
- [ ] 4.4 Connect processing step to CLI (`novaclips process`)

## 5. Upload
- [ ] 5.1 Implement `AdsPowerClient` (Wrapper for Local API: `/api/v1/user/start`)
- [ ] 5.2 Implement `BrowserManager` (Connect Playwright to `ws` endpoint)
- [ ] 5.3 Implement `YouTubeUploader` (Navigation, File selection, Form filling)
- [ ] 5.4 Connect upload step to CLI (`novaclips upload`)

## 6. Verification
- [ ] 6.1 Run full E2E test: Ingest -> Process -> Upload (Manual verification)
