# NovaClips

NovaClips is a modular pipeline for **collecting, transforming and publishing short-form videos** across multiple channels.

It focuses on:
- automated ingestion from external sources,
- batch video processing (crop/resize/overlays),
- scheduled uploads to platforms,
- basic analytics and monitoring.

> ⚠️ **Important:** You are responsible for complying with copyright law and each platform’s Terms of Service.  
> Only ingest and republish content you own, have rights to, or is clearly allowed by the source.

---

## Features

- 🔄 **Ingestion layer** – pluggable “grabbers” (Telegram, local folders, etc.).
- 🗃 **Media library** – central DB for tracking clips, statuses and usage.
- 🎛 **Video transform pipeline** – FFmpeg-based crop/scale/overlays/audio.
- 🧱 **Template-based renders** – consistent visual style for all clips.
- 📺 **Channel manager** – track multiple publishing channels/accounts.
- 🌐 **Optional proxy/identity layer** – separate network profiles per account.
- ⬆️ **Uploader** – (semi-)automated publishing with titles/descriptions/links.
- 📊 **Analytics hooks** – store basic performance metrics (views, clicks).
- 🧩 **Orchestrator** – simple job queues: ingest → process → publish.

NovaClips is meant as a **backend service/tooling**, not as a GUI app.

---

## High-Level Architecture

```text
            +----------------------+
            |  External Sources    |
            |  (Telegram, local)   |
            +----------+-----------+
                       |
                       v
            +----------------------+
            |   Ingestion Module   |
            +----------+-----------+
                       |
                       v
            +----------------------+
            |   Media Library DB   |
            |  (items + statuses)  |
            +----------+-----------+
                       |
             RAW   →  CLEAN  →  READY
                       |
                       v
            +----------------------+
            |  Transform/Render    |
            |  (FFmpeg templates)  |
            +----------+-----------+
                       |
                       v
            +----------------------+      +-------------------+
            |   Upload Queue       | ---> | Channel Manager   |
            +----------+-----------+      +-------------------+
                       |
                       v
            +----------------------+
            |     Uploader         |
            | (via browser/API)    |
            +----------+-----------+
                       |
                       v
            +----------------------+
            |   Analytics/Logs     |
            +----------------------+
````

---

## Modules Overview

### 1. Ingestion

**Goal:** pull fresh media from configured sources into a local storage.

Possible adapters:

* `TelegramIngest` (e.g. with Telethon / Pyrogram)

  * fetch recent messages with media from given channels
  * filter by date, type, duration
* `LocalFolderIngest`

  * scan local folder(s) for new files
* `GenericHTTPIngest`

  * download from allowed HTTP sources (where ToS permits)

Output:

* Files in `storage/raw/`
* Row in DB table `media_items` with status `RAW`

---

### 2. Media Library (DB)

Minimal schema example:

* `media_items`

  * `id` (PK)
  * `source` (enum/string)
  * `source_ref` (message ID, URL, etc.)
  * `path_raw`
  * `path_clean`
  * `path_ready`
  * `duration_sec`
  * `status` (`RAW` | `CLEAN` | `READY` | `POSTED` | `FAILED`)
  * `created_at`, `updated_at`
  * `hash` (optional, for dedupe)

Backend options:

* SQLite (default, simple dev)
* PostgreSQL (recommended for production)

---

### 3. Transform / Unique / Clean

**Goal:** turn raw media into "clean" clips suitable for short-form platforms while avoiding content fingerprinting.

The MVP uniquification process applies 6 transformation techniques to ensure videos are not flagged as duplicate content:

#### 1. Aspect Ratio Conversion to 9:16

* Only vertical videos are processed (horizontal videos are rejected)
* Convert vertical source videos to exact 1080×1920 format
* **Center-crop** to 9:16 aspect ratio

#### 2. Speed Variation

* Apply subtle speed modifications: ±3–7% (e.g., 0.95x or 1.05x)
* Changes timing and audio fingerprints without affecting viewer perception

#### 3. Audio Mixing

* Extract original audio
* Add royalty-free background music track (looped)
* Reduce background music volume by -8 to -12 dB relative to speech
* Apply audio ducking to keep speech intelligible

#### 4. Auto Zoom and Pan Effects

* Apply slow zoom-in/zoom-out throughout the video or in segments
* OR apply subtle pan movements (up/down shifts)
* Effects are subtle enough not to disturb viewing experience

#### 5. Auto-Generated Subtitles

* Separate video and audio streams
* Process audio separately (apply music mixing and ducking)
* Transcribe processed audio using ASR (Whisper or equivalent)
* Burn subtitles permanently into the final video (hard-coded)
* Consistent subtitle styling across all videos

#### 6. Edge Trimming

* Trim 0.5–1 second from beginning and/or end
* Optionally add short fade-in/fade-out effects
* Modifies total duration and timecodes

**Additional Operations:**

* Normalize frame rate to 30 fps
* Strip all metadata (EXIF, creation time, source tags)
* Normalize audio volume

Output:

* File in `storage/clean/`
* Update `media_items.status = 'CLEAN'`


---

### 4. Final Render

**Goal:** apply final template and prepare per-platform versions.

* combine one or more `CLEAN` clips into a final short
* apply final FFmpeg filterchain (e.g. LUTs, sharpness)
* export to `storage/ready/` in target codec/container

Output:

* File in `storage/ready/`
* `media_items.status = 'READY'`
* optional `variant` (A/B versions)

---

### 5. Channel Manager

**Goal:** manage multiple channels/accounts in one place.

Example table `channels`:

* `id`
* `platform` (e.g. `youtube`, `tiktok`)
* `label` (human-friendly name)
* `credentials_ref` (path to cookies/session or token)
* `proxy_ref` (optional)
* `status` (`ACTIVE`, `LIMITED`, `BANNED`)
* `created_at`, `last_check_at`

Responsibilities:

* track which channel is available for uploads
* map ready videos to channels
* log published video IDs per channel

---

### 6. Proxy / Identity Layer (Optional)

**Goal:** separate network/browser identity per account, if needed.

* `proxies` table: `id`, `host`, `port`, `auth`, `label`
* mapping: `channel.proxy_ref → proxy settings`
* optionally integrate with:

  * Selenium/Playwright custom profiles
  * different user-agent strings
  * isolated browser profiles

NovaClips does not include any “anti-detection” tooling by default, only configuration hooks.

---

### 7. Uploader

**Goal:** publish `READY` videos with metadata.

Implementation options:

* **Browser automation** (Selenium / Playwright):

  * open Studio / upload page
  * select file from `storage/ready/`
  * fill title, description, tags
  * set visibility (public/unlisted/scheduled)
* **Official APIs**, where allowed and appropriate:

  * note: some platforms limit or disallow automated uploads

Uploader should:

* update `media_items.status = 'POSTED'`
* store external `video_id` in a separate table `published_items`
* log failures / retries

---

### 8. CTA / Link Builder

**Goal:** generate titles/descriptions/comments with links.

* simple template system:

  * `{BASE_TITLE}`, `{SHORT_TAGS}`, `{MAIN_LINK}`, `{HASHTAGS}`, etc.
* environment- or config-driven:

  * main website URL
  * Telegram / Discord invite
  * tracking parameters (UTM)

Output:

* strings for:

  * title
  * description
  * optional pinned comment

---

### 9. Analytics

**Goal:** keep track of basic performance metrics.

Tables:

* `published_items`

  * `id`
  * `media_item_id`
  * `channel_id`
  * `platform_video_id`
  * `published_at`
* `stats_items`

  * `published_item_id`
  * `views`
  * `likes`
  * `comments`
  * `collected_at`

Data collection:

* via platform APIs where possible
* or via lightweight HTML scraping (respecting ToS)

---

### 10. Orchestrator

**Goal:** tie everything together via jobs and schedules.

Responsibilities:

* schedule ingestion (e.g. every 10–30 minutes)
* schedule transform/render jobs for new raw items
* feed `READY` items into upload queue
* trigger analytics collector once/twice per day
* send logs/alerts on failures

Implementation options:

* simple `cron` + CLI scripts
* Python task queue (e.g. RQ / Celery)
* or a minimal in-process scheduler

---

## Tech Stack (Suggested)

* **Language:** Python 3.11+
* **Ingestion:** Telethon / Pyrogram (for Telegram), `requests`, `yt-dlp`
* **Video:** FFmpeg (CLI, called from Python)
* **Automation:** Selenium or Playwright for uploader
* **DB:** SQLite (dev), PostgreSQL (prod)
* **Config:** `.env` + `config.yaml` or similar
* **Orchestration:** `cron`, or a simple queue runner

---

## Quickstart (Conceptual)

1. **Install prerequisites**

   * Python 3.11+, FFmpeg, virtualenv.
2. **Clone project & install deps**

   * `pip install -r requirements.txt`
3. **Configure `.env` / `config.yaml`**

   * DB connection
   * Telegram API keys (if using Telegram)
   * base output directories
4. **Run initial DB migrations/init script.**
5. **Run ingestion script** (to pull some media).
6. **Run transform/render script** (to produce `READY` videos).
7. **Run uploader** (manual or automated) and verify one full cycle.
