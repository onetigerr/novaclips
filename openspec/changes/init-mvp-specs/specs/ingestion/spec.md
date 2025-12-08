## ADDED Requirements

### Requirement: Telegram Ingestion
The system SHALL support ingesting video content from specified Telegram channels.

#### Scenario: Ingest from Channel
- **WHEN** the ingest command is run with a target channel
- **THEN** distinct video files are downloaded to the `raw` directory
- **AND** a record is created in the database for each new file

### Requirement: Local Ingestion
The system SHALL support ingesting files from a local watcher directory.

#### Scenario: Ingest from Folder
- **WHEN** the ingest command scans the watch folder
- **THEN** new supported files (mp4, mov) are copied to the `raw` directory
- **AND** marked as `source_type='local'` in the DB

### Requirement: Duplicate Filtering
The system MUST NOT ingest files that have already been recorded in the database.

#### Scenario: Skip existing hash
- **WHEN** a file is being considered for ingestion
- **THEN** its MD5 hash is calculated and checked against `media_items`
- **AND** if present, the file is skipped/ignored
