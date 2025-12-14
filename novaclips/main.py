import click
import logging
import sys
from pathlib import Path

# Configure logging
from novaclips.config import settings
log_path = settings.log_path
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_path))
    ]
)
logger = logging.getLogger("novaclips")

# Load env vars
from dotenv import load_dotenv
load_dotenv()

from novaclips.core.db import DatabaseManager
from novaclips.core.dao import MediaDAO
from novaclips.core.models import MediaItem
from novaclips.core.ingest.local import LocalIngest
from novaclips.core.ingest.telegram import TelegramIngest
from novaclips.core.upload.browser import BrowserManager
from novaclips.core.upload.youtube import YouTubeUploader
import asyncio

@click.group()
@click.pass_context
def cli(ctx):
    """NovaClips: Automated Video Pipeline"""
    # Ensure DB is ready
    db = DatabaseManager()
    ctx.obj = {'db': db, 'dao': MediaDAO(db)}
    logger.info("CLI initialized")

@cli.command()
@click.option('--source', type=click.Choice(['local', 'telegram']), required=True, help='Source type to ingest from')
@click.option('--path', help='Path for local source', required=False)
@click.option('--channel', help='Channel ID for telegram source', required=False)
@click.pass_context
def ingest(ctx, source, path, channel):
    """Ingest new media from source."""
    dao = ctx.obj['dao']
    logger.info(f"Starting ingestion from {source}")
    
    if source == 'local':
        if not path:
            click.echo("Error: --path is required for local source")
            return
        
        strategy = LocalIngest(dao, Path(path))
        files = strategy.scan()
        click.echo(f"Found {len(files)} potential files in {path}")
        
        count = 0
        for f in files:
            if strategy.process_file(f):
                count += 1
        
        click.echo(f"Successfully ingested {count} new files.")

    elif source == 'telegram':
        if not channel:
            click.echo("Error: --channel is required for telegram source")
            return
            
        strategy = TelegramIngest(dao)
        # Run async process in sync context
        asyncio.run(strategy.process_channel(channel))
        click.echo(f"Finished processing channel {channel}")

@cli.command()
@click.option('--batch-size', default=None, type=int, help='Maximum number of items to process')
@click.option('--id', 'item_id', type=int, help='Process specific item by ID')
@click.pass_context
def process(ctx, batch_size, item_id):
    """Process 'raw' items to 'clean' (normalize videos)."""
    from novaclips.core.processing import Uniquifier
    from novaclips.core.models import MediaItem
    from datetime import datetime
    
    dao = ctx.obj['dao']
    
    # Get items to process
    if item_id:
        # Process specific item
        query = "SELECT * FROM media_items WHERE id = ?"
        row = ctx.obj['db'].fetch_one(query, (item_id,))
        if not row:
            click.echo(f"Error: Item {item_id} not found")
            return
        items = [MediaItem.from_row(row)]
    else:
        # Process all raw items
        items = dao.get_pending_raw()
    
    if not items:
        click.echo("No items to process.")
        return
    
    # Apply batch size limit
    if batch_size:
        items = items[:batch_size]
    
    logger.info(f"Processing {len(items)} items")
    click.echo(f"Processing {len(items)} items...")
    
    # Use Uniquifier for full pipeline (Normalize + Subtitles + Effects)
    processor = Uniquifier()
    success_count = 0
    failed_count = 0
    
    for item in items:
        click.echo(f"\n[{item.id}] {item.original_filename}")
        
        # Validate raw_path exists
        if not item.raw_path:
            click.echo(f"  ✗ Error: No raw_path set")
            dao.update_status(item.id, 'failed', processing_error='no raw_path')
            failed_count += 1
            continue
        
        raw_path = Path(item.raw_path)
        if not raw_path.exists():
            click.echo(f"  ✗ Error: Raw file not found: {raw_path}")
            dao.update_status(item.id, 'failed', processing_error='raw file not found')
            failed_count += 1
            continue
        
        # Determine output path
        clean_dir = settings.clean_dir
        clean_dir.mkdir(parents=True, exist_ok=True)
        output_filename = f"{raw_path.stem}_unique.mp4"
        clean_path = clean_dir / output_filename
        
        # Process video
        try:
            success = processor.process(raw_path, clean_path)
            
            if success and clean_path.exists():
                click.echo(f"  ✓ Processed successfully")
                dao.update_status(
                    item.id,
                    'clean',
                    clean_path=str(clean_path),
                    processed_at=datetime.now()
                )
                success_count += 1
            else:
                click.echo(f"  ✗ Processing failed")
                dao.update_status(item.id, 'failed', processing_error='normalization failed')
                failed_count += 1
                
        except Exception as e:
            click.echo(f"  ✗ Error: {e}")
            logger.error(f"Processing error for item {item.id}: {e}", exc_info=True)
            dao.update_status(item.id, 'failed', processing_error=str(e))
            failed_count += 1
    
    click.echo(f"\n✓ Success: {success_count}")
    click.echo(f"✗ Failed: {failed_count}")
    logger.info(f"Processing complete: {success_count} success, {failed_count} failed")

@cli.command()
@click.option('--id', 'item_id', type=int, help='Process specific item by ID')
@click.pass_context
def prepare(ctx, item_id):
    """Prepare 'clean' items for upload (Generate Description + Rename)."""
    import json
    from novaclips.core.prepare.extractor import FrameExtractor
    from novaclips.core.prepare.collage import CollageMaker
    from novaclips.core.prepare.generator import DescriptionGenerator
    from novaclips.core.prepare.renamer import FileRenamer
    
    dao = ctx.obj['dao']
    
    # Get items
    query = "SELECT * FROM media_items WHERE status = 'clean'"
    if item_id:
        query += " AND id = ?"
        rows = ctx.obj['db'].fetch_all(query, (item_id,))
    else:
        rows = ctx.obj['db'].fetch_all(query)
        
    items = [MediaItem.from_row(r) for r in rows]
    
    if not items:
        click.echo("No clean items found to prepare.")
        return
        
    click.echo(f"Preparing {len(items)} items...")
    
    extractor = FrameExtractor()
    collage_maker = CollageMaker()
    generator = DescriptionGenerator()
    renamer = FileRenamer(dao)
    
    temp_dir = Path("data/temp_prepare")
    temp_dir.mkdir(exist_ok=True, parents=True)
    
    success_count = 0
    
    for item in items:
        click.echo(f"\n[{item.id}] Preparing: {item.original_filename}")
        
        try:
            video_path = Path(item.clean_path)
            if not video_path.exists():
                click.echo("  ✗ Error: Video file not found")
                continue
                
            # 1. Extract Frames
            click.echo("  - Extracting frames...")
            frames = extractor.extract_frames(video_path, temp_dir / str(item.id))
            if not frames:
                click.echo("  ✗ Failed to extract frames")
                continue
                
            # 2. Make Collage
            collage_path = temp_dir / f"{item.id}_collage.jpg"
            if not collage_maker.create_collage(frames, collage_path):
                 click.echo("  ✗ Failed to create collage")
                 continue
                 
            # 3. Read Subtitles (if any)
            srt_path = video_path.with_suffix('.srt')
            transcript = None
            if srt_path.exists():
                try:
                    transcript = srt_path.read_text(encoding='utf-8')
                    click.echo("  - Found subtitles")
                except:
                    pass
            
            # 4. Generate Description
            click.echo("  - Generating description (AI)...")
            meta = generator.generate(collage_path, transcript)
            
            if not meta:
                click.echo("  ⚠ AI generation failed or skipped (no key?). Using defaults.")
                meta = {
                    "title": item.original_filename,
                    "description": "",
                    "hashtags": "",
                    "slug": f"video_{item.id}"
                }
            else:
                click.echo(f"  ✓ Generated: {meta.get('title', 'No Title')}")
                
            # 5. Rename File
            slug = meta.get('slug', f"video_{item.id}")
            # sanitize slug lightly
            slug = "".join([c for c in slug if c.isalnum() or c in '-_']).strip()
            
            new_path = renamer.rename_item(item.id, video_path, slug)
            click.echo(f"  - Renamed to: {new_path.name}")
            
            # 6. Update DB
            # Add cta link if configured (globally) - assumed added by user manually or we can add here
            # For now just save what AI gave + maybe existing config
            default_cta = settings.get('DEFAULT_CTA_LINK') # direct access or config object?
            # Config is a module usually. Let's assume user wants raw AI output for now.
            
            # We need to save as JSON
            import json
            meta_json = json.dumps(meta)
            
            dao.update_status(
                item.id,
                'ready',
                clean_path=str(new_path),
                upload_metadata=meta_json
            )
            success_count += 1
            click.echo("  ✓ Ready for upload")
            
        except Exception as e:
            click.echo(f"  ✗ Error: {e}")
            logger.error(f"Prepare error for {item.id}: {e}", exc_info=True)
            
    # Cleanup
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except:
        pass
        
    click.echo(f"\nPrepared {success_count} items.")


@cli.command()
@click.option('--status', default='clean', help='Status to cleanup (default: clean)')
@click.pass_context
def cleanup(ctx, status):
    """Remove DB entries for missing files."""
    dao = ctx.obj['dao']
    
    # We only support cleaning up 'clean' for now as requested
    if status != 'clean':
        click.echo("Currently only 'clean' status cleanup is supported.")
        return

    items = dao.get_items_by_status('clean')
    if not items:
        click.echo("No clean items found.")
        return
        
    click.echo(f"Scanning {len(items)} clean items for missing files...")
    
    removed_count = 0
    for item in items:
        if not item.clean_path:
            # Should not happen typically for 'clean' but possible
             dao.delete_item(item.id)
             click.echo(f"  [x] Removed {item.id} (No path)")
             removed_count += 1
             continue
             
        p = Path(item.clean_path)
        if not p.exists():
            # File deleted manually
            dao.delete_item(item.id)
            click.echo(f"  [x] Removed {item.id} (File missing: {p.name})")
            removed_count += 1
            
    click.echo(f"Cleanup complete. Removed {removed_count} orphan entries.")


@cli.command()
def auth():
    """Launch browser for manual authentication (Google Login)."""
    click.echo("Launching browser for authentication...")
    click.echo("Please log in to your Google Account/YouTube Channel.")
    click.echo("Press Enter in this terminal when you are done to save the session.")
    
    # Ensure profile directory exists
    profile_dir = Path("data/browser_profile")
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    browser = BrowserManager(user_data_dir=profile_dir)
    try:
        browser.launch(headless=False)
        page = browser.get_page()
        page.goto("https://www.youtube.com")
        
        # Wait for user to manually interact
        input("Press Enter to close browser and save session...")
        
    except Exception as e:
        click.echo(f"Error during auth: {e}")
        logger.error(f"Auth error: {e}", exc_info=True)
    finally:
        browser.close()
        click.echo("Browser closed. Session saved.")

@cli.command()
@click.option('--batch-size', default=None, type=int, help='Maximum number of videos to upload')
@click.pass_context
def upload(ctx, batch_size):
    """Upload 'ready' items to YouTube."""
    import json
    dao = ctx.obj['dao']
    ready_items = dao.get_pending_upload()
    
    # Apply batch size limit
    if batch_size:
        ready_items = ready_items[:batch_size]

    logger.info(f"Found {len(ready_items)} items to upload")
    
    if not ready_items:
        click.echo("No ready items found.")
        return

    # Initialize Browser
    profile_dir = Path("data/browser_profile")
    if not profile_dir.exists():
        click.echo("Error: Browser profile not found. Please run 'novaclips auth' first.")
        return

    browser = BrowserManager(user_data_dir=profile_dir)
    browser.launch(headless=False) # Use false for now to debug
    page = browser.get_page()
    uploader = YouTubeUploader(page)

    uploaded_count = 0
    
    try:
        for item in ready_items:
            click.echo(f"\nUploading item {item.id}...")
            
            # Determine file path (check clean_path)
            if not item.clean_path:
                click.echo("  ✗ Error: clean_path is missing")
                continue
                
            file_path = Path(item.clean_path)
            if not file_path.exists():
                click.echo(f"  ✗ Error: File not found {file_path}")
                continue

            # Parse Description/Title
            title = item.title # Explicit override
            desc = ""
            
            if item.upload_metadata:
                try:
                    meta = json.loads(item.upload_metadata)
                    if not title:
                        title = meta.get('title')
                    
                    d_text = meta.get('description', '')
                    tags = meta.get('hashtags', '')
                    
                    parts = []
                    if d_text: parts.append(d_text)
                    
                    # Add CTA if in config
                    # cta = settings.get('DEFAULT_CTA_LINK')
                    # if cta: parts.append(cta)
                    
                    if tags: parts.append(tags)
                    
                    desc = "\n\n".join(parts)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse metadata: {e}")
            
            if not title:
                title = item.original_filename

            click.echo(f"  Title: {title}")
            
            success = uploader.upload_video(
                file_path=file_path,
                title=title, 
                description=desc, 
                safety_mode=False  # Public
            )
            
            if success:
                click.echo("  ✓ Uploaded successfully")
                dao.update_status(item.id, 'uploaded')
                uploaded_count += 1
            else:
                click.echo("  ✗ Upload failed")
                # Don't fail the batch, just log
                
    except Exception as e:
        click.echo(f"Critical error during upload batch: {e}")
        logger.error(f"Upload batch error: {e}", exc_info=True)
    finally:
        browser.close()
        click.echo(f"\nUpload run complete. Uploaded: {uploaded_count}")

def main():
    cli(obj={})

if __name__ == '__main__':
    main()
