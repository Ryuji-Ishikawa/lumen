#!/usr/bin/env python3
"""
Debug version - takes screenshots to verify what's being recorded
"""

import asyncio
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright


async def record_demo_debug():
    """Debug version with screenshots"""
    
    print("🔍 Debug Mode: Recording with screenshots...")
    print("=" * 60)
    
    # Start Streamlit app
    print("📱 Starting Streamlit app...")
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait longer for app to start
    print("⏳ Waiting for app to initialize (15 seconds)...")
    await asyncio.sleep(15)
    
    try:
        async with async_playwright() as p:
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(
                headless=False,  # Show browser for debugging
                slow_mo=500  # Slow down actions
            )
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                record_video_dir="./demo_recordings",
                record_video_size={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            
            # Create screenshots directory
            screenshots_dir = Path("./debug_screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            
            print("🎥 Recording started...")
            print()
            
            # Navigate to app
            print("📍 Step 1: Navigate to app...")
            await page.goto('http://localhost:8501', wait_until='networkidle')
            await asyncio.sleep(3)
            await page.screenshot(path=screenshots_dir / "01_initial.png")
            print("   ✅ Screenshot saved: 01_initial.png")
            
            # Upload file
            print("📍 Step 2: Upload file...")
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files('Sample_Business Plan.xlsx')
                print("   ✅ File uploaded")
                await asyncio.sleep(3)
                await page.screenshot(path=screenshots_dir / "02_uploaded.png")
                print("   ✅ Screenshot saved: 02_uploaded.png")
            else:
                print("   ⚠️  File input not found!")
            
            # Wait for analysis
            print("📍 Step 3: Wait for analysis...")
            await asyncio.sleep(5)
            await page.screenshot(path=screenshots_dir / "03_analysis.png")
            print("   ✅ Screenshot saved: 03_analysis.png")
            
            # Scroll
            print("📍 Step 4: Scroll down...")
            await page.evaluate("window.scrollTo({ top: 400, behavior: 'smooth' })")
            await asyncio.sleep(2)
            await page.screenshot(path=screenshots_dir / "04_scrolled.png")
            print("   ✅ Screenshot saved: 04_scrolled.png")
            
            # Try to click risk item
            print("📍 Step 5: Click risk item...")
            risk_items = await page.query_selector_all('[data-testid="stExpander"]')
            print(f"   Found {len(risk_items)} risk items")
            if risk_items and len(risk_items) > 0:
                await risk_items[0].click()
                await asyncio.sleep(2)
                await page.screenshot(path=screenshots_dir / "05_clicked.png")
                print("   ✅ Screenshot saved: 05_clicked.png")
            else:
                print("   ⚠️  No risk items found!")
            
            # Final screenshot
            print("📍 Step 6: Final state...")
            await asyncio.sleep(2)
            await page.screenshot(path=screenshots_dir / "06_final.png")
            print("   ✅ Screenshot saved: 06_final.png")
            
            print()
            print("✅ Debug recording complete!")
            print(f"📸 Screenshots saved in: {screenshots_dir}")
            print("💾 Saving video...")
            
            # Close browser
            await context.close()
            await browser.close()
            
            # Get video path
            video_path = None
            recordings_dir = Path("./demo_recordings")
            if recordings_dir.exists():
                video_files = list(recordings_dir.glob("*.webm"))
                if video_files:
                    video_path = video_files[0]
                    print(f"📹 Video saved: {video_path}")
            
            return video_path
            
    finally:
        # Stop Streamlit
        print("🛑 Stopping Streamlit app...")
        streamlit_process.terminate()
        streamlit_process.wait()


async def main():
    print()
    print("=" * 60)
    print("  LUMEN DEBUG RECORDER")
    print("  Browser will be visible, actions will be slow")
    print("=" * 60)
    print()
    
    await record_demo_debug()
    
    print()
    print("🔍 Next steps:")
    print("1. Check screenshots in ./debug_screenshots/")
    print("2. Check video in ./demo_recordings/")
    print("3. Identify what went wrong")
    print()


if __name__ == "__main__":
    asyncio.run(main())
