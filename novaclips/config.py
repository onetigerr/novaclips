import os
import yaml
from pathlib import Path
from typing import Any, Dict

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Loads configuration from YAML file."""
        if not self.config_path.exists():
            # Fallback or empty if not found, though in this case we expect it to exist
            # Could also raise an error.
            return

        with open(self.config_path, "r") as f:
            self.data = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    @property
    def env(self) -> str:
        return self.data.get("NOVACLIPS_ENV", "dev")

    @property
    def db_url(self) -> str:
        return self.data.get("DB_URL", "sqlite:///novaclips.db")

    @property
    def raw_dir(self) -> Path:
        return Path(self.data.get("RAW_DIR", "./data/storage/raw"))
    
    @property
    def clean_dir(self) -> Path:
        return Path(self.data.get("CLEAN_DIR", "./data/storage/clean"))
    
    @property
    def ready_dir(self) -> Path:
        return Path(self.data.get("READY_DIR", "./data/storage/ready"))

    @property
    def log_path(self) -> Path:
        return Path(self.data.get("LOG_PATH", "./data/logs/app.log"))

    @property
    def session_dir(self) -> Path:
        return Path(self.data.get("SESSION_DIR", "./data/sessions"))

    @property
    def db_path(self) -> Path:
        url = self.data.get("DB_URL", "sqlite:///data/db/novaclips.db")
        if url.startswith("sqlite:///"):
            return Path(url.replace("sqlite:///", ""))
        return Path("data/db/novaclips.db")

    @property
    def debug_dir(self) -> Path:
        return Path(self.data.get("DEBUG_DIR", "./data/storage/debug"))

    @property
    def music_dir(self) -> Path:
        return Path(self.data.get("MUSIC_DIR", "./data/music"))

    @property
    def subtitles(self) -> Dict[str, Any]:
        return self.data.get("SUBTITLES", {})

    @property
    def whisper(self) -> Dict[str, Any]:
        return self.data.get("WHISPER", {})

    @property
    def processing(self) -> Dict[str, Any]:
        return self.data.get("PROCESSING", {})

# Global instance
# Assuming config.yaml is in the project root (CWD usually)
# Adjust path if necessary depending on where the entry point is run from.
# Safe bet is relative to this file's parent's parent if standard layout, 
# or just assume CWD for now as requested.
settings = Config("config.yaml")
