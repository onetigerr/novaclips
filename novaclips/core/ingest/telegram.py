import logging
import asyncio
import os
import hashlib
from pathlib import Path
from typing import List, Optional
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

from novaclips.core.ingest.base import IngestStrategy
from novaclips.core.dao import MediaDAO
from novaclips.core.models import MediaItem

logger = logging.getLogger(__name__)

class TelegramIngest(IngestStrategy):
    def __init__(self, dao: MediaDAO, session_name: str = "novaclips_session"):
        self.dao = dao
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        
        # Session path
        from novaclips.config import settings
        self.session_dir = settings.session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_path = self.session_dir / session_name
        
        self.session_name = str(self.session_path) # Telethon takes path as first arg if string

        self.client: Optional[TelegramClient] = None
        
        # Move to config
        from novaclips.config import settings
        self.raw_dir = settings.raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.max_history = 50

    async def _ensure_client(self):
        """Initializes and connects the Telegram client."""
        if not self.api_id or not self.api_hash:
            raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in env.")

        if self.client and self.client.is_connected():
            return

        self.client = TelegramClient(self.session_name, int(self.api_id), self.api_hash)
        await self.client.start()

    def result_sync(self, coroutine):
        """Helper to run async code in sync context."""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we are already in an event loop (rare for this sync CLI currently), use 'run_until_complete' might fail
            # But specific to this MVP, main is sync, so this is fine.
            return loop.run_until_complete(coroutine)
        else:
            return asyncio.run(coroutine)

    def scan(self) -> List[Path]:
        """
        Scanning in Telegram context means fetching history and identifying downloadable media.
        However, since we need to download to get the file path, scan might return metadata
        or we just implement the full ingest flow in a custom method and scan returns empty.
        
        Redefining scan for Telegram: Returns list of Message objects (or wrappers) that HAVE media.
        """
        # Note: This breaks the strict signature of returning List[Path] from base, 
        # but base says "scan() -> List[Path]". 
        # For Telegram, we probably want to download immediately or return placeholder paths.
        # Let's assume for now we don't return Paths to existing files, but rather we do the work in process_channel.
        logger.warning("scan() is not fully applicable to TelegramIngest in the same way as Local.")
        return []

    async def _fetch_history(self, channel_username: str):
        await self._ensure_client()
        messages = []
        async for message in self.client.iter_messages(channel_username, limit=self.max_history):
            if message.video or (message.document and message.document.mime_type.startswith('video/')):
                messages.append(message)
        return messages

    async def _download_media(self, message) -> Path:
        filename = f"tg_{message.id}_{message.date.strftime('%Y%m%d_%H%M%S')}"
        path = await self.client.download_media(message, file=self.raw_dir / filename)
        return Path(path)

    async def process_channel(self, channel_username: str):
        """
        Specific main entry point for Telegram Ingestion.
        """
        try:
            logger.info(f"Connecting to Telegram for channel {channel_username}...")
            await self._ensure_client()
            
            logger.info(f"Fetching history from {channel_username}...")
            messages = await self._fetch_history(channel_username)
            logger.info(f"Found {len(messages)} video messages.")

            for msg in messages:
                # Basic check if we already have this source_id
                # (Ideally DAO should have get_by_source_id too)
                # But we can also rely on hash check after download?
                # Relying on hash check requires downloading first which consumes bandwidth.
                # Better to check source_id (message.id) first.
                
                # Check DB for source_id (we need to implement get_by_source_id in DAO or manual query)
                # For now, let's just download and check hash (MVP strategy as defined in plan: "hash check")
                
                logger.info(f"Downloading message {msg.id}...")
                file_path = await self._download_media(msg)
                
                # Calculate Hash
                # Re-use LocalIngest logic or duplicate hash logic? 
                # Let's duplicate simple hash logic for now or refactor.
                file_hash = self._calculate_hash(file_path)

                if self.dao.get_by_hash(file_hash):
                    logger.info(f"Duplicate found for {file_path.name}, deleting.")
                    file_path.unlink() # Delete duplicate
                    continue

                # Save to DB
                item = MediaItem(
                    source_type="telegram",
                    source_id=f"{channel_username}_{msg.id}",
                    original_filename=file_path.name,
                    status="raw",
                    content_hash=file_hash,
                    raw_path=str(file_path),
                    upload_channel=channel_username
                )
                self.dao.add_item(item)
                logger.info(f"Ingested Telegram ID {msg.id}")

        except Exception as e:
            logger.error(f"Telegram processing failed: {e}")
            raise
        finally:
            if self.client:
                logger.info("Disconnecting Telethon client...")
                await self.client.disconnect()
                logger.info("Telethon client disconnected.")

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculates SHA-256 hash."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def download(self, item) -> Path:
        # Not used in the bulk flow above
        pass
