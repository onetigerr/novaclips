"""
Video processing module for NovaClips.

This module handles video normalization and uniquification.
"""

from .processor import VideoProcessor
from .normalizer import Normalizer

__all__ = ["VideoProcessor", "Normalizer"]
