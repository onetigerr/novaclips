# Change: Implement Auto-Description Generation

## Why
Currently, uploaded videos lack descriptions and titles, which hurts discoverability and user engagement. We need an automated way to generate context-aware descriptions and hashtags. Additionally, files are named with obscure IDs, making manual management difficult.

## What Changes
- **New `prepare` pipeline stage**: Intermediary step between `process` and `upload`.
- **SRT Preservation**: Subtitles are now saved as files, not just burned in.
- **AI Integration**: Uses Groq (Vision + Text) to analyze video content.
- **File Renaming**: Files are renamed to `{id}_{slug}.mp4` for better readability.
- **Status Flow**: `raw` -> `clean` -> `ready` -> `uploaded`.

## Impact
- **Database**: Uses `upload_metadata` JSON field to store generated title/description.
- **Filesystem**: New `.srt` files in `clean/`. Renamed `.mp4` files.
- **Dependencies**: Requires `groq`, `Pillow` (likely already present or to be added).
