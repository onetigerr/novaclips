## ADDED Requirements

### Requirement: AdsPower & Playwright Upload
The system SHALL upload videos to YouTube using an AdsPower browser profile controlled by Playwright.

#### Scenario: Upload Execution
- **WHEN** the upload task processes an item
- **THEN** it calls AdsPower Local API to start the specific profile
- **AND** connects Playwright not to a local binary, but to the returned WebSocket Debug URL
- **AND** performs the upload via the existing profile session

### Requirement: Session Persistence (AdsPower)
The system SHALL rely on AdsPower's built-in session management.

#### Scenario: Profile Reuse
- **WHEN** the browser is launched via AdsPower
- **THEN** cookies and cache are automatically managed by the AdsPower profile (no manual cookie saving required)
