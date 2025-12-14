## ADDED Requirements

### Requirement: Content Preparation
The system SHALL analyze processed videos to generate metadata before upload.

#### Scenario: Description Generation
- **WHEN** the `prepare` command is run on a `clean` item
- **THEN** 4 keyframes are extracted (15%, 35%, 60%, 85%) and stitched into a collage
- **AND** the collage and subtitles (if available) are sent to an AI model
- **AND** a description with hashtags is generated and stored in `upload_metadata`
- **AND** the item status is updated to `ready`

#### Scenario: File Renaming
- **WHEN** an item is prepared
- **THEN** the file is renamed to `{id}_{slug}.mp4` where slug is derived from the generated title/description
- **AND** the database record is updated with the new path

### Requirement: Metadata Injection
The system SHALL use pre-generated metadata during upload.

#### Scenario: Description Population
- **WHEN** uploading a video
- **THEN** the description field in YouTube Studio is populated with the content from `upload_metadata`
