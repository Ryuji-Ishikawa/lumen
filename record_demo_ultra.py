#!/usr/bin/env python3
"""
Lumen Ultra Demo Recording
All 4 issues fixed:
1. Sidebar scroll 1.5x more (650 → 975px)
2. Cursor movement to file upload button
3. New file with MANY risks
4. Diagnostic screen scroll MUCH more (3000→8000, 4000→10000, 5000→12000, 6000→15000)
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import subprocess


async def smooth_move(page, x, y, duration_ms=800):
    """Move cursor smoothly to position"""
    current = await page.evaluate("() => ({ x: window.lastMouseX || 0, y: window.lastMouseY || 0 })")
    start_x = current['x']
    start_y = current['y']
    
    steps = 20
    for i in range(steps + 1):
        progress = i / steps
        # Ease in-out
        t = progress if progress < 0.5 else 1 - progress
        eased = 2 * t * t if progress < 0.5 else -1 + (4 - 2 * progress) * progress
        
        curr_x = start_x + (x - start_x) * eased
        curr_y = start_y + (y - start_y) * eased
        
        await page.mouse.move(curr_x, curr_y)
        await asyncio.sleep(duration_ms / 1000 / steps)
    
    await page.evaluate(f"() => {{ window.lastMouseX = {x}; window.lastMouseY = {y}; }}")


async def smooth_scroll_element(page, selector, scroll_top, duration_ms=800):
    """Scroll a specific element smoothly"""
    await page.evaluate("""
        ({selector, targetY, duration}) => {
            const element = document.querySelector(selector);
            if (!element) return;
            
            const start = element.scrollTop;
            const change = targetY - start;
            const startTime = performance.now();
            
            function easeInOutQuad(t) {
                return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
            }
            
            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = easeInOutQuad(progress);
                
                element.scrollTop = start + (change * eased);
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            }
            
            requestAnimationFrame(animate);
        }
    """, {"selector": selector, "targetY": scroll_top, "duration": duration_ms})
    await asyncio.sleep(duration_ms / 1000)


async def wait_for_analysis(page, max_wait=15):
    """Wait for analysis to complete"""
    print("   ⏳ Waiting for analysis...")
    for i in range(max_wait):
        results = await page.query_selector('[data-testid="stExpander"]')
        if results:
            print(f"   ✅ Complete ({i}s)")
            return True
        await asyncio.sleep(1)
    return False


async def record_demo():
    """Record demo with ALL 4 fixes"""
    
    print("🎬 Lumen Ultra Demo Recording")
    print("=" * 60)
    print()
    print("⚠️  Streamlit must be running on http://localhost:8501")
    print()
    input("Press Enter when ready...")
    print()
    
    async with async_playwright() as p:
        print("🌐 Launching browser...")
        # headless=False to show cursor
        browser = await p.chromium.launch(
            headless=False,
            args=['--window-size=1280,720']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir="./demo_recordings",
            record_video_size={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        print("🎥 Recording...")
        print()
        
        # 1) Initial screen (0-2s)
        print("1️⃣  Initial screen (0-2s)")
        await page.goto('http://localhost:8501', wait_until='networkidle')
        await asyncio.sleep(2)
        
        # 2) Scroll LEFT sidebar down 1.5x MORE (2-4s)
        print("2️⃣  Scroll sidebar down 1.5x (2-4s)")
        # FIX #1: 650 → 975px (1.5x)
        try:
            await smooth_scroll_element(page, '[data-testid="stSidebar"] > div', 975, 1000)
            print("   ✅ Scrolled 975px (1.5x more)")
        except:
            print("   ℹ️  Sidebar not scrollable")
        await asyncio.sleep(1)
        
        # 3) Move cursor and click file upload button (4-6s)
        print("3️⃣  Upload file with cursor movement (4-6s)")
        # FIX #2: Cursor movement to file upload button
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            box = await file_input.bounding_box()
            if box:
                target_x = box['x'] + box['width'] / 2
                target_y = box['y'] + box['height'] / 2
                print(f"   🖱️  Moving cursor to ({target_x:.0f}, {target_y:.0f})")
                await smooth_move(page, target_x, target_y, 800)
                await asyncio.sleep(0.5)
            
            # FIX #3: Use new file with MANY risks
            await file_input.set_input_files('Demo_Budget_With_Risks.xlsx')
            print("   ✅ File uploaded (with MANY risks)")
            await asyncio.sleep(1)
        else:
            print("   ❌ File input not found!")
            return None
        
        # 4) Wait for analysis (6-18s)
        print("4️⃣  Analysis (6-18s)")
        if not await wait_for_analysis(page, max_wait=20):
            print("   ⚠️  Analysis timeout - continuing anyway")
        await asyncio.sleep(2)
        
        # 5) Health score display (12-14s)
        print("5️⃣  Health score (12-14s)")
        await asyncio.sleep(2)

        
        # 6) Scroll down main content MUCH MORE (14-16s)
        print("6️⃣  Scroll main content (14-16s)")
        # FIX #4: Scroll to bottom or 8000px
        await page.evaluate("window.scrollTo({ top: Math.min(document.body.scrollHeight, 8000), behavior: 'smooth' })")
        current_scroll = await page.evaluate("window.pageYOffset")
        print(f"   ✅ Scrolled to {current_scroll}px")
        await asyncio.sleep(2)
        
        # 7) Click "整合性リスク" tab (16-18s)
        print("7️⃣  Click 整合性リスク tab (16-18s)")
        tabs = await page.query_selector_all('button[role="tab"]')
        for tab in tabs:
            text = await tab.inner_text()
            if '整合性' in text or 'Integrity' in text:
                await tab.click()
                print("   ✅ Tab clicked")
                await asyncio.sleep(1)
                break
        await asyncio.sleep(1)
        
        # 8) Scroll down MUCH MORE (18-20s)
        print("8️⃣  Scroll down (18-20s)")
        # FIX #4: Scroll more
        await page.evaluate("window.scrollTo({ top: Math.min(document.body.scrollHeight, 10000), behavior: 'smooth' })")
        current_scroll = await page.evaluate("window.pageYOffset")
        print(f"   ✅ Scrolled to {current_scroll}px")
        await asyncio.sleep(2)
        
        # 9) Select a risk from list - DOUBLE CLICK for Streamlit (20-23s)
        print("9️⃣  Select risk - double click (20-23s)")
        await asyncio.sleep(1)
        risk_items = await page.query_selector_all('[data-testid="stExpander"]')
        print(f"   Found {len(risk_items)} risks")
        if risk_items and len(risk_items) > 0:
            box = await risk_items[0].bounding_box()
            if box:
                await page.evaluate(f"window.scrollTo({{ top: {max(0, box['y'] - 200)}, behavior: 'smooth' }})")
                await asyncio.sleep(0.8)
            # First click - sets session state, triggers rerun
            await page.evaluate("document.querySelectorAll('[data-testid=\"stExpander\"]')[0].click()")
            print("   🔄 First click (session state set)")
            await asyncio.sleep(1.2)
            # Second click - now detail shows
            await page.evaluate("document.querySelectorAll('[data-testid=\"stExpander\"]')[0].click()")
            print("   ✅ Second click (detail shown)")
            await asyncio.sleep(1)
        else:
            print("   ⚠️  No risks found")
        await asyncio.sleep(0.5)
        
        # 10) Scroll to show risk details MUCH MORE (23-26s)
        print("🔟 Show risk details (23-26s)")
        # FIX #4: Scroll more
        await page.evaluate("window.scrollTo({ top: Math.min(document.body.scrollHeight, 12000), behavior: 'smooth' })")
        current_scroll = await page.evaluate("window.pageYOffset")
        print(f"   ✅ Scrolled to {current_scroll}px")
        await asyncio.sleep(2)
        
        # Continue scrolling MUCH MORE (26-29s)
        # FIX #4: Scroll to near bottom
        await page.evaluate("window.scrollTo({ top: Math.min(document.body.scrollHeight, 15000), behavior: 'smooth' })")
        current_scroll = await page.evaluate("window.pageYOffset")
        print(f"   ✅ Scrolled to {current_scroll}px")
        await asyncio.sleep(2)
        
        # Final frame (29-31s)
        print("✨ Final frame (29-31s)")
        await asyncio.sleep(2)
        
        print()
        print("✅ Recording complete!")
        
        await context.close()
        await browser.close()
        
        # Get video
        recordings_dir = Path("./demo_recordings")
        if recordings_dir.exists():
            video_files = list(recordings_dir.glob("*.webm"))
            if video_files:
                return max(video_files, key=lambda p: p.stat().st_mtime)
        return None


def convert_to_formats(video_path):
    """Convert to WebM and GIF"""
    if not video_path or not video_path.exists():
        print("❌ Video not found!")
        return
    
    print()
    print("🔄 Converting...")
    
    output_webm = Path("lumen_demo.webm")
    output_gif = Path("lumen_demo.gif")
    
    # WebM
    try:
        subprocess.run([
            "ffmpeg", "-i", str(video_path),
            "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0",
            "-y", str(output_webm)
        ], check=True, capture_output=True)
        print(f"✅ {output_webm}")
    except:
        import shutil
        shutil.copy(video_path, output_webm)
        print(f"✅ {output_webm} (copy)")
    
    # GIF
    try:
        subprocess.run([
            "ffmpeg", "-i", str(video_path),
            "-vf", "fps=15,scale=1280:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            "-loop", "0", "-y", str(output_gif)
        ], check=True, capture_output=True)
        print(f"✅ {output_gif}")
    except:
        print("⚠️  GIF conversion failed (ffmpeg needed)")
    
    print()
    print("🎉 Done!")


async def main():
    print()
    print("=" * 60)
    print("  LUMEN ULTRA DEMO")
    print("  ALL 4 FIXES APPLIED")
    print("=" * 60)
    print()
    print("✅ Fix #1: Sidebar scroll 1.5x (650→975px)")
    print("✅ Fix #2: Cursor movement to upload button")
    print("✅ Fix #3: New file with MANY risks")
    print("✅ Fix #4: Diagnostic scroll MUCH more:")
    print("           - 3000 → 8000px")
    print("           - 4000 → 10000px")
    print("           - 5000 → 12000px")
    print("           - 6000 → 15000px")
    print()
    
    video_path = await record_demo()
    if video_path:
        convert_to_formats(video_path)
    else:
        print("❌ Failed")


if __name__ == "__main__":
    asyncio.run(main())
