#!/usr/bin/env python3
"""
Verification script for YouTube upload functionality.
Tests the upload flow with a specific video file.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from novaclips.core.upload.browser import BrowserManager
from novaclips.core.upload.youtube import YouTubeUploader

def main():
    # Test video path
    test_video = Path("data/storage/clean/tg_111496_20251209_100345_unique.mp4")
    
    if not test_video.exists():
        print(f"❌ Test video not found: {test_video}")
        return 1
    
    print(f"✓ Found test video: {test_video}")
    print(f"  Size: {test_video.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Check browser profile
    profile_dir = Path("data/browser_profile")
    if not profile_dir.exists():
        print(f"\n❌ Browser profile not found at {profile_dir}")
        print("   Please run: python -m novaclips.main auth")
        return 1
    
    print(f"✓ Browser profile found: {profile_dir}")
    
    # Initialize browser and uploader
    print("\n🚀 Starting upload test...")
    browser = BrowserManager(user_data_dir=profile_dir)
    
    try:
        # Launch browser (non-headless for debugging)
        browser.launch(headless=False)
        page = browser.get_page()
        
        # Create uploader
        uploader = YouTubeUploader(page)
        
        # Attempt upload
        print("\n📤 Uploading video...")
        success = uploader.upload_video(
            file_path=test_video,
            title="NovaClips Test Upload",
            description="Automated test upload from NovaClips pipeline",
            safety_mode=False  # Public
        )
        
        if success:
            print("\n✅ Upload completed successfully!")
            print("   Check your YouTube Studio for the uploaded video.")
            return 0
        else:
            print("\n❌ Upload failed. Check logs and screenshots in data/storage/debug/")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during upload: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        browser.close()
        print("\n🔒 Browser closed.")

if __name__ == "__main__":
    sys.exit(main())
