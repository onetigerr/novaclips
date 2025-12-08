# Change: Initialize MVP Specifications

## Why
The project currently has requirements scattered across `docs/` files. To ensure a structured development process aligned with OpenSpec, these requirements must be formalized into specific Capabilities with clear Scenarios. This establishes the "Definition of Done" for the MVP.

## What Changes
- Formalize **Ingestion** capability (Telegram, Local).
- Formalize **Media Management** capability (SQLite Schema, Lifecycle).
- Formalize **Processing** capability (Uniqueness, Normalization).
- Formalize **Upload** capability (YouTube Shorts via Selenium).
- Formalize **CLI** capability (Commands structure).
- Define the `media_items` database schema.
- Define the standard project directory structure for media (`raw`, `clean`, `etc`).

## Impact
- **New Specs**: `ingestion`, `media-management`, `processing`, `upload`, `cli`.
- **Codebase**: This proposal sets the blueprint for the entire initial codebase implementation.
