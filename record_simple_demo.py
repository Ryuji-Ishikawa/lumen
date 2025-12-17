#!/usr/bin/env python3
"""
Simple demo - use existing Sample file
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import subprocess


async def record_demo():
    print("🎬 Recording demo...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir="./demo_recordings"
        )
        page = await context.new_page()
        
        # Load page
        await page.goto('http://localhost:8501')
        await asyncio.sleep(3)
        
        # Scroll sidebar using mouse wheel
        sidebar = await page.query_selector('[data-testid="stSidebar"]')
        if sidebar:
            box = await sidebar.bounding_box()
            await page.mouse.move(box['x'] + 100, box['y'] + 100)
            # Scroll down with mouse wheel
            for _ in range(10):
                await page.mouse.wheel(0, 100)
                await asyncio.sleep(0.1)
        await asyncio.sleep(2)
        
        # Upload file
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files('Sample_Business Plan.xlsx')
            await asyncio.sleep(8)
        
        # Scroll main content a bit to show results
        main_area = await page.query_selector('[data-testid="stAppViewContainer"]')
        if main_area:
            box = await main_area.bounding_box()
            await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
            # Scroll down moderately
            for _ in range(15):  # Reduced from 50 to 15
                await page.mouse.wheel(0, 150)
                await asyncio.sleep(0.1)
        await asyncio.sleep(2)
        
        # Click 整合性リスク tab
        print("Clicking 整合性リスク tab...")
        tabs = await page.query_selector_all('button[role="tab"]')
        for tab in tabs:
            text = await tab.inner_text()
            if '整合性' in text or 'Integrity' in text:
                await tab.click()
                print(f"✅ Clicked tab: {text}")
                await asyncio.sleep(2)
                break
        
        # Wait for tab content to load
        await asyncio.sleep(3)
        
        # Scroll to show risks
        if main_area:
            for _ in range(10):
                await page.mouse.wheel(0, 150)
                await asyncio.sleep(0.1)
        await asyncio.sleep(2)
        
        # Click first risk to expand - try multiple approaches
        print("Clicking first risk...")
        try:
            # Wait a bit more and try to click
            await asyncio.sleep(1)
            
            # Try multiple selectors and methods
            result = await page.evaluate("""
                () => {
                    // Try different selectors
                    let clicked = false;
                    let found = 0;
                    
                    // Method 1: stExpander with summary
                    const expanders = document.querySelectorAll('[data-testid="stExpander"]');
                    found = expanders.length;
                    
                    if (expanders.length > 0) {
                        // Try clicking the summary element
                        const summary = expanders[0].querySelector('summary');
                        if (summary) {
                            summary.click();
                            clicked = true;
                        } else {
                            // Try clicking any button
                            const button = expanders[0].querySelector('button');
                            if (button) {
                                button.click();
                                clicked = true;
                            } else {
                                // Try clicking the details element
                                const details = expanders[0].querySelector('details');
                                if (details) {
                                    details.open = true;
                                    clicked = true;
                                } else {
                                    // Last resort: click the expander itself
                                    expanders[0].click();
                                    clicked = true;
                                }
                            }
                        }
                    }
                    
                    return { found, clicked };
                }
            """)
            
            if result['clicked']:
                print(f"✅ Clicked risk (found {result['found']} risks)")
                await asyncio.sleep(3)  # Wait longer for expansion
            else:
                print(f"⚠️  Found {result['found']} risks but could not click")
        except Exception as e:
            print(f"⚠️  Could not click risk: {e}")
        
        # Scroll to show risk details
        if main_area:
            for _ in range(10):
                await page.mouse.wheel(0, 150)
                await asyncio.sleep(0.1)
        await asyncio.sleep(3)
        
        await context.close()
        await browser.close()
        
        recordings_dir = Path("./demo_recordings")
        if recordings_dir.exists():
            video_files = list(recordings_dir.glob("*.webm"))
            if video_files:
                return max(video_files, key=lambda p: p.stat().st_mtime)
    return None


async def main():
    video_path = await record_demo()
    if video_path:
        print(f"✅ Video: {video_path}")
        # Copy to output
        import shutil
        shutil.copy(video_path, "lumen_demo.webm")
        print("✅ Saved: lumen_demo.webm")


if __name__ == "__main__":
    asyncio.run(main())
