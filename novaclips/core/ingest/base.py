from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

class IngestStrategy(ABC):
    """Abstract base class for ingestion strategies."""

    @abstractmethod
    def scan(self) -> List[Path]:
        """Scans the source for new media."""
        pass

    @abstractmethod
    def download(self, item: Path | object) -> Path:
        """Downloads/Copies the media item to raw storage."""
        pass
