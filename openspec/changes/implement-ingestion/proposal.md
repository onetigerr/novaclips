# Change: Implement Ingestion Strategies

## Why
The project requires a way to import media from various sources to begin the processing pipeline. Currently, there is no mechanism to ingest videos.

## What Changes
- Adds `IngestStrategy` abstract base class.
- Adds `LocalIngest` for importing files from a local directory.
- Adds `TelegramIngest` for ensuring authentication and downloading media from Telegram channels.
- Defines storage locations for raw media.

## Impact
- **New Capability**: `ingest`
- **Affected Code**: `novaclips/core/ingest/`
- **Dependencies**: Adds `Telethon` to requirements.
