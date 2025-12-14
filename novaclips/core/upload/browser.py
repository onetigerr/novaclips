import logging
from pathlib import Path
from playwright.sync_api import sync_playwright, BrowserContext, Page

logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Manages a persistent Playwright browser context for YouTube upload.
    Stores session data (cookies, localStorage) in `data/browser_profile`.
    """
    
    def __init__(self, user_data_dir: Path):
        self.user_data_dir = user_data_dir
        self.playwright = None
        self.context: BrowserContext = None
        self.page: Page = None
        
    def launch(self, headless: bool = True):
        """
        Launches the browser with persistent context.
        
        Args:
            headless: If True, runs without invisible UI. 
                     Set False for debugging or initial auth.
        """
        if self.context:
            logger.warning("Browser is already running")
            return

        logger.info(f"Launching browser (Headless: {headless})...")
        self.playwright = sync_playwright().start()
        
        # Args to make it slightly less distinct as a bot (basic strictness)
        # For full anti-detect, more args are needed, but this is MVP.
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
        ]
        
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=headless,
            args=args,
            viewport={"width": 1280, "height": 720},
            # Basic user agent override can be added here if needed
        )
        
        # Create a new page or get existing
        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()
            
        logger.info("Browser launched successfully")

    def get_page(self) -> Page:
        if not self.page:
            raise RuntimeError("Browser not launched. Call launch() first.")
        return self.page
        
    def close(self):
        if self.context:
            self.context.close()
            self.context = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        logger.info("Browser closed")
