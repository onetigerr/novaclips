## ADDED Requirements

### Requirement: Video Normalization
The system SHALL convert variable input formats into a standardized vertical format for Shorts.

#### Scenario: Vertical Scaling
- **WHEN** processing a video
- **THEN** it is scaled and cropped to exactly 1080x1920 pixels (9:16 aspect ratio)
- **AND** the frame rate is normalized to 30 fps

### Requirement: Metadata Cleaning
The system SHALL remove identifiable metadata to treat content as fresh.

#### Scenario: Strip Tags
- **WHEN** processing a video
- **THEN** global and stream-level metadata (EXIF, creation time, source tags) are removed using ffmpeg
