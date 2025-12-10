## ADDED Requirements

### Requirement: Ingest Strategy Interface
The system SHALL provide a uniform interface for all ingestion strategies to scan for and download media.

#### Scenario: Interface contract
- **WHEN** a concrete strategy is implemented
- **THEN** it must implement `scan()` and `download()` methods

### Requirement: Local File Ingestion
The system SHALL support ingesting video files from a local directory, ensuring no duplicates are imported based on file hash.

#### Scenario: Ingest new file
- **WHEN** `LocalIngest` scans a directory with a new video file
- **THEN** it copies the file to the raw storage folder
- **AND** records the file hash in the database

#### Scenario: Skip duplicate file
- **WHEN** `LocalIngest` scans a file with a hash already in the DB
- **THEN** it skips the file without copying

### Requirement: Telegram Channel Ingestion
The system SHALL support ingesting media from Telegram channels using a user account.

#### Scenario: Authenticate User
- **WHEN** `TelegramIngest` is initialized
- **THEN** it verifies session validity or prompts/handles login flow

#### Scenario: Fetch Channel History
- **WHEN** `scan()` is called with a channel source
- **THEN** it retrieves message history up to a limit
- **AND** filters for video media

#### Scenario: Download Telegram Media
- **WHEN** `download()` is called for a Telegram message
- **THEN** it downloads the video file to raw storage
- **AND** respects rate limits
