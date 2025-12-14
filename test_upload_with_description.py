import logging
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from novaclips.core.db import DatabaseManager
from novaclips.core.dao import MediaDAO
from novaclips.core.models import MediaItem
from novaclips.core.upload.browser import BrowserManager
from novaclips.core.upload.youtube import YouTubeUploader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_upload")

def main():
    target_id = 30
    logger.info(f"Starting test upload for ID {target_id}")

    # 1. Database Setup
    db = DatabaseManager()
    dao = MediaDAO(db)
    
    # 2. Get Item
    query = "SELECT * FROM media_items WHERE id = ?"
    row = db.fetch_one(query, (target_id,))
    
    if not row:
        logger.error(f"Item {target_id} not found!")
        return
        
    item = MediaItem.from_row(row)
    logger.info(f"Loaded item: {item.original_filename}")
    logger.info(f"Status: {item.status}")
    logger.info(f"Clean Path: {item.clean_path}")
    
    if not item.clean_path or not Path(item.clean_path).exists():
        logger.error("Clean file missing!")
        return

    # 3. Parse Metadata
    title = item.title or item.original_filename
    description = ""
    
    if item.upload_metadata:
        try:
            meta = json.loads(item.upload_metadata)
            logger.info(f"Metadata found: {meta}")
            
            # Title priority: Argument > Metadata > DB Title > Filename
            # But here we want to test the metadata title specifically
            if meta.get('title'):
                title = meta.get('title')
                
            d_text = meta.get('description', '')
            tags = meta.get('hashtags', [])
            
            # Format hashtags if list
            if isinstance(tags, list):
                tags = " ".join(tags)
            
            parts = []
            if d_text: parts.append(d_text)
            if tags: parts.append(tags)
            
            description = "\n\n".join(parts)
            
        except Exception as e:
            logger.error(f"Failed to parse metadata: {e}")
            
    logger.info(f"Final Title: {title}")
    logger.info(f"Final Description:\n{description}")

    # 4. Launch Browser & Upload
    # Ensure profile directory exists
    profile_dir = Path("data/browser_profile")
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Launching browser...")
    browser = BrowserManager(user_data_dir=profile_dir)
    browser.launch(headless=False) 
    
    try:
        page = browser.get_page()
        uploader = YouTubeUploader(page)
        
        logger.info("Starting upload flow...")
        success = uploader.upload_video(
            file_path=Path(item.clean_path),
            title=title,
            description=description,
            safety_mode=False
        )
        
        if success:
            logger.info("✅ Upload reported success!")
            # Update status just in case, though this is a test script
            # dao.update_status(item.id, 'uploaded') 
        else:
            logger.error("❌ Upload failed")
            
    except Exception as e:
        logger.error(f"Exception during test: {e}", exc_info=True)
    finally:
        # Keep open briefly to see
        # input("Press Enter to close...")
        browser.close()
        logger.info("Browser closed.")

if __name__ == "__main__":
    main()
