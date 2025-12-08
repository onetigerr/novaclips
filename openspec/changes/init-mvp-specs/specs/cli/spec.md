## ADDED Requirements

### Requirement: Command Line Interface
The system SHALL be controllable exclusively via CLI commands.

#### Scenario: Ingest Command
- **WHEN** user runs `novaclips ingest --source telegram`
- **THEN** new media is fetched from configured channels

#### Scenario: Process Command
- **WHEN** user runs `novaclips process`
- **THEN** pending `raw` items are converted to `clean` and then `ready`

#### Scenario: Upload Command
- **WHEN** user runs `novaclips upload`
- **THEN** `ready` items are uploaded to the target platform
