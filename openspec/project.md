# Project Context

## Purpose
NovaClips is a modular pipeline for collecting, transforming, and publishing short-form videos.
The goal is to automate the flow from Source (Telegram) -> Processing (Uniqueness) -> Publishing (YouTube Shorts).

## Architecture Strategy: MVP vs Production
We strictly follow a two-stage evolution strategy to minimize over-engineering.

### Phase 1: MVP (Current Focus)
- **Goal**: Speed to market, simplicity, minimal abstraction.
- **Architecture**: Monolithic script-based application.
- **Concurrency**: Synchronous Python code (blocking). No `asyncio` complexity unless strictly required by libraries (e.g., Telethon).
- **Database**: SQLite with raw `sqlite3` or simple wrapper. No ORMs (SQLAlchemy). No Migrations (use `CREATE TABLE IF NOT EXISTS` on startup).
- **Interface**: CLI only. No Web API or Admin Panel.
- **Infrastructure**: Local execution, `venv`, single system process. No Docker.
- **Queue/Scheduling**: Main loop with `time.sleep`. No Redis, no external message brokers (Celery).
- **Sources**: Telegram and Local Folder only.
- **Targets**: YouTube Shorts only.
- **Networking**: Direct connection (Local IP). No Proxies for MVP.
- **Auth Persistence**: SQLite blobs/JSON for cookies and sessions.

### Phase 2: Production (Future Roadmap)
- **Goal**: Scalability, robustness, observability, separation of concerns.
- **Architecture**: Modular Monolith or Microservices.
- **Concurrency**: Asynchronous (FastAPI, asyncio).
- **Database**: PostgreSQL + SQLAlchemy (Async) + Alembic migrations.
- **Interface**: REST API (FastAPI) + Optional Web Frontend (React/Vue).
- **Infrastructure**: Docker Compose (App + DB + Redis).
- **Queue**: Redis + Worker (Celery/Arq/Dramatiq).
- **Scalability**: Multiple worker containers, distinct services for Ingest vs Render.

## Tech Stack (MVP)
- **Language**: Python 3.11+
- **Core modules**: `sqlite3`, `logging`, `dataclasses`, `os`, `shutil`.
- **Ingestion**: `Telethon` (Telegram), `yt-dlp`.
- **Processing**: `ffmpeg-python` (or raw `subprocess` calling FFmpeg).
- **Automation**: `Selenium` or `Playwright` (Headless).
- **Config**: `.env` file loaded via `python-dotenv` or `os.getenv`.

## Project Conventions

### Code Style
- **Type Hinting**: Required for all function arguments and returns.
- **Docstrings**: Google style for complex functions/classes.
- **Imports**: standard lib -> third party -> local application.
- **Path Handling**: Use `pathlib.Path` exclusively over `os.path`.

### Architecture Patterns (MVP)
- **Pipeline Style**: Data flows linearly: Ingest -> Raw (Storage) -> Transform -> Clean (Storage) -> Upload.
- **State Management**: Database is the single source of truth. The filesystem reflects the DB state.
- **Error Handling**: "Catch & Log" strategy. If a file fails processing, log the error to `debug.log` and console, update status to `FAILED`, and **continue** to the next item. Do not crash the application.
- **Logging**: Standard `logging` library. Console output + file rotation.

### DevOps & Git
- **Repo Structure**: Flat or minimal package hierarchy.
- **Testing**: Manual End-to-End verification for MVP. No unit test suite required.
- **Deployment**: `git pull` + `pip install -r requirements.txt` + `python main.py`.

## Domain Context
- **Uniqueness**: Platforms (YouTube) fingerprint content. We must strip metadata and slightly alter video/audio (crop, speed, overlay) to avoid "Reused Content" strikes.
- **Safety**: Uploads must mimic human behavior (random delays, persistent cookies) to avoid spam detection.
- **Compliance**: Only ingest content where allowed. Respect copyrights.

## Important Constraints
- **Filesystem**: Use absolute paths or project-relative paths anchored to a configurable ROOT_DIR.
- **Rate Limits**: Respect Telegram and YouTube API/Browser limits. Imposing delays is better than getting banned.
