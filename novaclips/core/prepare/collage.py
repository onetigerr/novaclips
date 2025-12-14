import logging
from pathlib import Path
from typing import List
from PIL import Image

logger = logging.getLogger(__name__)

class CollageMaker:
    """Stitches images into a single horizontal collage."""

    def create_collage(self, image_paths: List[Path], output_path: Path) -> bool:
        """
        Merges images horizontally. Resizes them to same height if needed.
        """
        if not image_paths:
            return False

        try:
            images = [Image.open(p) for p in image_paths]
            
            # Find min height to resize all to same height (maintaining aspect ratio usually, but for frames from same video, height should be same)
            # We assume all frames are same size actually.
            width, height = images[0].size
            
            total_width = width * len(images)
            
            # Create new image
            collage = Image.new('RGB', (total_width, height))
            
            x_offset = 0
            for img in images:
                collage.paste(img, (x_offset, 0))
                x_offset += img.width
            
            collage.save(output_path, quality=85)
            logger.info(f"Collage saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collage: {e}")
            return False
