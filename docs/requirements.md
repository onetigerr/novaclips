# NovaClips Requirements (OpenSpec Draft)

## 1. Input Layer (Sources)

### Requirement: Telegram Source
The system SHALL support extracting media from Telegram channels.
#### Scenario: Parse specific channel
- **WHEN** user configures a Telegram channel source
- **THEN** the system extracts video files and metadata (date, caption)
- **AND** saves them to the `raw` storage area

### Requirement: TikTok Source
The system SHALL support downloading videos from TikTok without watermarks.
#### Scenario: Download by URL
- **WHEN** user provides a TikTok URL
- **THEN** the system downloads the video file without the TikTok watermark
- **AND** saves it to the `raw` storage area

### Requirement: Local Source
The system SHALL support monitoring a local folder for new files.
#### Scenario: Watch folder
- **WHEN** a new file is placed in the designated watch folder
- **THEN** the system automatically detects and ingests the file

---

## 2. Media Management

### Requirement: Duplicate Prevention
The system MUST prevent processing or uploading the same file twice.
#### Scenario: Hash check
- **WHEN** a new file is ingested
- **THEN** its MD5 hash is calculated and compared against the database
- **AND** if a match is found, the file is marked as duplicate and skipped

### Requirement: Asset Lifecycle
The system SHALL track the status of each media asset.
#### Scenario: Status transition
- **WHEN** a file is successfully processed from `raw` to `clean`
- **THEN** the database record is updated to reflect the new status

---

## 3. Processing (Uniqueness)

### Requirement: Video Normalization
The system SHALL convert all input videos to a standard format for Shorts.
#### Scenario: Resize and Crop
- **WHEN** a horizontal or non-standard video is processed
- **THEN** it is cropped and scaled to 1080x1920 (9:16)
- **AND** encoded as H.264/MP4

### Requirement: Anti-Metadata
The system SHALL remove original metadata to prevent fingerprinting.
#### Scenario: Strip metadata
- **WHEN** a video is processed
- **THEN** all EXIF and source metadata tags are removed from the output file

---

## 4. Channels & Accounts

### Requirement: Account Management
The system SHALL manage credentials for multiple YouTube accounts (approx. 5 for MVP).
#### Scenario: Channel Rotation
- **WHEN** an upload task is triggered
- **THEN** the system selects an active, non-limited account from the database

### Requirement: Session Persistence
The system SHALL persist session data to avoid frequent re-logins.
#### Scenario: Save Cookies
- **WHEN** a login session is established
- **THEN** cookies and tokens are saved to SQLite for future reuse

---

## 5. Uploading (YouTube Shorts)

### Requirement: Automated Upload
The system SHALL upload videos to YouTube Shorts via browser automation (CLI-triggered).
#### Scenario: Upload flow
- **WHEN** the upload command is run
- **THEN** the system launches a headless browser instance
- **AND** uploads the video with the specified title and description

### Requirement: Upload Limits
The system MUST respect daily upload limits per channel.
#### Scenario: Limit reached
- **WHEN** a channel reaches its configured daily limit
- **THEN** the system skips that channel and attempts to use the next available one

---

## 6. Infrastructure & CLI

### Requirement: CLI Interface
The system SHALL provide a Command Line Interface for all operations.
#### Scenario: Manual trigger
- **WHEN** user runs `novaclips process`
- **THEN** the batch processing pipeline is executed

### Requirement: Proxy Support
The system SHALL route network requests through assigned proxies per channel.
#### Scenario: IP Isolation
- **WHEN** performing actions for Channel A
- **THEN** all traffic uses the proxy server assigned to Channel A
