## ADDED Requirements

### Requirement: Asset Lifecycle Tracking
The system SHALL track the state of every media item from Ingest to Upload.

#### Scenario: State Progression
- **WHEN** a file successfully completes a processing step (e.g., Raw -> Clean)
- **THEN** its `status` field in the database is updated (e.g., to 'clean')
- **AND** the corresponding path field (e.g., `clean_path`) is populated

### Requirement: Storage Organization
The system MUST organize files into a strict directory hierarchy based on their state.

#### Scenario: File Placement
- **WHEN** a file is ingested, processed, or finalized
- **THEN** it is placed in `data/storage/raw`, `data/storage/clean`, or `data/storage/ready` respectively
