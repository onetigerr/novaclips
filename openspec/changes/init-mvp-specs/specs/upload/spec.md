## ADDED Requirements

### Requirement: Playwright Upload
The system SHALL upload videos to YouTube using a standard Playwright browser instance.

#### Scenario: Upload Execution
- **WHEN** the upload task processes an item
- **THEN** it launches a Playwright browser context pointing to a local `user_data_dir`
- **AND** performs the upload via the automated browser interface

### Requirement: Session Persistence (Local)
The system SHALL rely on Playwright's persistent context to maintain login sessions.

#### Scenario: Profile Reuse
- **WHEN** the browser is launched with `user_data_dir`
- **THEN** cookies and authentication state are loaded from the filesystem
- **AND** the user does not need to re-login if a valid session exists

