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
    from novaclips.core.processing import Normalizer
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
    
    normalizer = Normalizer()
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
        output_filename = f"{raw_path.stem}_normalized.mp4"
        clean_path = clean_dir / output_filename
        
        # Process video
        try:
            success = normalizer.process(raw_path, clean_path)
            
            if success and clean_path.exists():
                click.echo(f"  ✓ Normalized successfully")
                dao.update_status(
                    item.id,
                    'clean',
                    clean_path=str(clean_path),
                    processed_at=datetime.now()
                )
                success_count += 1
            else:
                click.echo(f"  ✗ Normalization failed")
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
@click.pass_context
def upload(ctx):
    """Upload 'ready' items to YouTube."""
    dao = ctx.obj['dao']
    ready_items = dao.get_pending_upload()
    logger.info(f"Found {len(ready_items)} items to upload")
    
    if not ready_items:
        click.echo("No ready items found.")
        return

    # Mock upload loop
    for item in ready_items:
        click.echo(f"Uploading item {item.id}...")
        # Logic to call Uploader will go here...

def main():
    cli(obj={})

if __name__ == '__main__':
    main()
