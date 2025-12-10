"""
Base class for video processing operations.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class VideoProcessor(ABC):
    """
    Abstract base class for all video processing operations.
    
    Subclasses should implement the process() method to perform
    specific video transformations.
    """
    
    def __init__(self):
        self.logger = logger
    
    @abstractmethod
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Process a video file.
        
        Args:
            input_path: Path to input video file
            output_path: Path where processed video should be saved
            
        Returns:
            True if processing succeeded, False otherwise
        """
        pass
    
    def validate_input(self, path: Path) -> bool:
        """
        Validate that input file exists and is a video file.
        
        Args:
            path: Path to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not path.exists():
            self.logger.error(f"Input file does not exist: {path}")
            return False
        
        if not path.is_file():
            self.logger.error(f"Input path is not a file: {path}")
            return False
        
        # Check file extension
        valid_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}
        if path.suffix.lower() not in valid_extensions:
            self.logger.warning(f"File extension {path.suffix} may not be a valid video format")
        
        return True
    
    def ensure_output_dir(self, output_path: Path) -> bool:
        """
        Ensure output directory exists.
        
        Args:
            output_path: Output file path
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create output directory: {e}")
            return False
