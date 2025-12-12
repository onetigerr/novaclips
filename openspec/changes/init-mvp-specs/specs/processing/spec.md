## ADDED Requirements

### Requirement: Video Validation
The system SHALL validate input video parameters before processing.

#### Scenario: Minimum Resolution Check
- **WHEN** validating a source video
- **THEN** it must have a vertical resolution of at least 800 pixels
- **AND** a horizontal resolution of at least 450 pixels
- **OTHERWISE** the video is rejected

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

### Requirement: Speed Variation
The system SHALL apply subtle speed modifications to alter timing and audio fingerprints.

#### Scenario: Random Speed Adjustment
- **WHEN** processing a video for uniquification
- **THEN** playback speed is adjusted by a random value between ±3% and ±7% (e.g., 0.93x-0.97x or 1.03x-1.07x)
- **AND** the speed change is applied to both video and audio streams

### Requirement: Audio Mixing
The system SHALL modify the audio track to change acoustic fingerprints using background music.

#### Scenario: Background Music Addition
- **WHEN** processing a video for uniquification
- **THEN** a random royalty-free background music track is selected from `data/music`
- **AND** if no music files exist, the process fails with an ERROR
- **AND** the music is mixed at a fixed volume (randomly between -8dB and -12dB relative to original audio)
- **AND** if the video is longer than the music, the music loop is hard-repeated (no crossfade)

### Requirement: Auto Zoom Effects
The system SHALL apply subtle dynamic zoom effects.

#### Scenario: Center Zoom-In
- **WHEN** processing a video for uniquification
- **THEN** a linear zoom-in effect is applied from the center of the frame
- **AND** the zoom amount depends on video duration (Linear interpolation: 10s=4%, 20s=5%, 40s=6%, 80s=7%)
- **AND** the initial zoom starts at 0% (1.0x scale)

### 6. Auto Zoom and Pan [DEFERRED]
**Requirement:** Apply a slow, subtle zoom (e.g., 5-10% over the duration of the clip).
**Status:** Deferred for debugging.

### 7. Fade In/Out [NEW]
**Requirement:** Add a fade-in and fade-out effect to the video.
**Parameters:**
- Duration: 0.2 - 0.5 seconds (randomized based on video length).
- Placement: Start and end of the video.
**Scenario:**
- Video length < 10s: Fade 0.2s.
- Video length >= 10s: Random fade 0.3-0.5s.

### 8. Auto-Generated Subtitles
**Requirement:** Transcribe audio using `faster-whisper` and burn subtitles into the video.
**Scenario:**
- Style defined in configuration (font, size, color).
- Burned into the video stream for permanent retention.

### 9. Edge Trimming
**Requirement:** Trim 0.5-1.0 second from the start and end of the video.
**Scenario:**
- Video < 10s: Trim 0.5s from start only.
- Video >= 10s: Trim 0.5-1.0s from start and end.
