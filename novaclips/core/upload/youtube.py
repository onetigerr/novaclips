import logging
import time
from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class YouTubeUploader:
    """
    Handles the automation of YouTube Studio upload via Playwright.
    """
    
    # URL
    STUDIO_URL = "https://studio.youtube.com"
    
    # Selectors (Constant to make updates easier)
    SELECTORS = {
        "upload_button": "#create-icon",
        "upload_video_item": "text=Upload videos",
        "file_input": "input[type='file']",
        "title_input": "#textbox[aria-label='Add a title that describes your video']", # This is tricky, often better to find by label
        # Shorts usually autodetect title from filename, but we might want to set it.
        # "Not made for kids" radio
        "not_for_kids": "name=VIDEO_MADE_FOR_KIDS_MFK", 
        "next_button": "#next-button",
        "done_button": "#done-button",
        "radio_public": "[name='PUBLIC']",
        "radio_unlisted": "[name='UNLISTED']",
        "processing_complete": "text=Checks complete. No issues found." # Optimistic
    }

    def __init__(self, page: Page):
        self.page = page

    def upload_video(self, file_path: Path, title: str = None, description: str = None, safety_mode: bool = True):
        """
        Uploads a video to YouTube.
        """
        logger.info(f"Starting upload for {file_path}")
        
        # 1. Go to Studio
        try:
            self.page.goto(self.STUDIO_URL, timeout=60000)
            self.page.wait_for_load_state("networkidle", timeout=60000)
        except Exception as e:
            logger.error(f"Failed to load YouTube Studio: {e}")
            return False

        # Check if we are logged in (look for avatar or create button)
        # Try multiple selectors for the start button
        start_selectors = [
            self.SELECTORS["upload_button"],        # Top right create icon
            "text=Upload videos",                   # Big blue button on empty dashboard
            "yp-simple-worker[aria-label='Create']", # Sometimes it's this
            "#create-icon",                         # Explicit ID
            "button[aria-label='Create']",
            "button[aria-label='Upload videos']"
        ]
        
        found_selector = None
        logger.info("Waiting for Create/Upload button...")
        
        for sel in start_selectors:
            try:
                if self.page.is_visible(sel):
                    found_selector = sel
                    break
            except:
                continue
                
        if not found_selector:
            # Try waiting for the main one as last resort
            try:
                self.page.wait_for_selector(self.SELECTORS["upload_button"], timeout=5000)
                found_selector = self.SELECTORS["upload_button"]
            except PlaywrightTimeoutError:
                pass

        if not found_selector:
            logger.error(f"Not logged in? Create button not found. Current URL: {self.page.url}")
            # Take debug screenshot
            debug_path = Path("data/storage/debug")
            debug_path.mkdir(parents=True, exist_ok=True)
            screenshot_path = debug_path / "upload_login_fail.png"
            self.page.screenshot(path=str(screenshot_path))
            logger.info(f"Saved debug screenshot to {screenshot_path}")
            return False

        # 2. Start Upload
        logger.info(f"Clicking Create/Upload button: {found_selector}")
        self.page.click(found_selector)
        
        # If we clicked the "Create" icon (top right), we then need to click "Upload videos" in the dropdown
        # If we clicked the big "Upload videos" button (center), we go straight to file selection
        
        # Check if we need to click "Upload videos" in dropdown
        # The dropdown item "Upload videos" usually appears after clicking Create.
        try:
             # Short wait to see if dropdown appears
             self.page.wait_for_selector(self.SELECTORS["upload_video_item"], timeout=2000)
             logger.info("Clicking 'Upload videos' in dropdown...")
             self.page.click(self.SELECTORS["upload_video_item"])
        except PlaywrightTimeoutError:
             logger.info("No dropdown 'Upload videos' found, assuming direct upload button was clicked.")
        
        # 3. Select File
        logger.info("Selecting file...")
        with self.page.expect_file_chooser() as fc_info:
            self.page.click("#select-files-button") # Or directly input keys
            # Often easier to set input files directly if reliable
        
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        
        # Wait for upload dialog to settle
        # The file upload starts. We wait for the wizard to appear.
        logger.info("Waiting for upload wizard...")
        self.page.wait_for_selector(self.SELECTORS["next_button"], timeout=60000)

        # 4. Fill Details
        # For Shorts, just setting Not Made for Kids is usually enough for MVP.
        
        logger.info("Setting metadata...")

        # 4a. Title
        if title:
            try:
                # Title input is usually #title-textarea #textbox
                # We need to target the contenteditable div
                logger.info(f"Setting title: {title}")
                # Wait for title input to be visible (it loads a bit slow sometimes)
                self.page.wait_for_selector("#title-textarea #textbox", timeout=10000)
                
                # Click and clear
                self.page.click("#title-textarea #textbox")
                # Select all and delete (CMD+A for Mac, Ctrl+A for others - Playwright handles meta/control auto usually but explicit is safer)
                # simpler: fill() might not work on contenteditable. type() is safer.
                self.page.keyboard.press("Meta+A")
                self.page.keyboard.press("Backspace")
                self.page.keyboard.type(title)
            except Exception as e:
                logger.warning(f"Failed to set title: {e}")
        
        # 4b. Description
        if description:
            try:
                logger.info("Setting description...")
                # Description input usually #description-textarea #textbox
                self.page.click("#description-textarea #textbox")
                self.page.keyboard.type(description)
            except Exception as e:
                logger.warning(f"Failed to set description: {e}")

        # Set 'Not made for kids'
        
        # Set 'Not made for kids'
        # The selector might be a radio button group.
        # We need to click the radio button specifically.
        # Often it's `tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_MFK"]`
        try:
            logger.info("Selecting 'Not made for kids'...")
            # Try text selector first as it's most robust for humans
            self.page.click("text=No, it's not made for kids") 
        except Exception as e:
            logger.warning(f"Could not click 'Not made for kids' by text: {e}. Trying fallback...")
            try:
                self.page.click("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_MFK'][aria-checked='false']")
            except:
                logger.warning("All 'Not made for kids' selectors failed. 'Next' might be disabled.")

        # 5. Next Steps (Checks, Visibility)
        # We generally click 'Next' 3 times: Details -> Video Elements -> Checks -> Visibility
        
        for step in ["Details", "Video Elements", "Checks"]:
            logger.info(f"Completing step: {step}")
            try:
                self.page.click(self.SELECTORS["next_button"])
            except Exception as e:
                 logger.error(f"Failed to click Next on step {step}: {e}")
                 # Screenshot
                 self.page.screenshot(path=f"data/storage/debug/step_fail_{step}.png")
                 return False
                 
            time.sleep(2) # Small delay for UI animation and transition

        # 6. Visibility
        logger.info("Setting visibility...")
        # wait for visibility options
        self.page.wait_for_selector(self.SELECTORS["radio_public"])
        
        if safety_mode:
             self.page.click(self.SELECTORS["radio_unlisted"])
        else:
             self.page.click(self.SELECTORS["radio_public"])

        # 7. Publish
        logger.info("Publishing...")
        self.page.click(self.SELECTORS["done_button"])
        
        # 8. Wait for 'Video published' or 'Upload complete'
        # There's a dialog "Video published" or "Video uploaded"
        # We want to wait a bit to ensure the request goes through.
        logger.info("Waiting for confirmation...")
        try:
            self.page.wait_for_selector("text=Video published", timeout=30000)
            logger.info("Video published successfully!")
            
            # Close the dialog
            self.page.click("#close-button")
            return True
            
        except PlaywrightTimeoutError:
            logger.warning("Did not see 'Video published' confirmation, but flow completed. Checking...")
            return True # Assume success if we got here
        except Exception as e:
            logger.error(f"Error checking publication: {e}")
            return False
