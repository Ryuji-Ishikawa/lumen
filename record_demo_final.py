#!/usr/bin/env python3
"""
Lumen Professional Demo Recording - Final Version
Includes proper scrolling to show all UI elements
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import subprocess


class BezierCurve:
    """Generate smooth Bezier curve points for human-like mouse movement"""
    
    @staticmethod
    def cubic_bezier(t, p0, p1, p2, p3):
        return (
            (1 - t) ** 3 * p0 +
            3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * p2 +
            t ** 3 * p3
        )
    
    @staticmethod
    def generate_path(start_x, start_y, end_x, end_y, steps=50):
        dx = end_x - start_x
        dy = end_y - start_y
        
        ctrl1_x = start_x + dx * 0.25 + dy * 0.1
        ctrl1_y = start_y + dy * 0.25 - dx * 0.05
        ctrl2_x = start_x + dx * 0.75 - dy * 0.1
        ctrl2_y = start_y + dy * 0.75 + dx * 0.05
        
        points = []
        for i in range(steps + 1):
            t = i / steps
            x = BezierCurve.cubic_bezier(t, start_x, ctrl1_x, ctrl2_x, end_x)
            y = BezierCurve.cubic_bezier(t, start_y, ctrl1_y, ctrl2_y, end_y)
            points.append((x, y))
        
        return points


async def smooth_move(page, target_x, target_y, duration_ms=800):
    try:
        current_pos = await page.evaluate("() => ({ x: window.lastMouseX || 640, y: window.lastMouseY || 100 })")
        start_x = current_pos['x']
        start_y = current_pos['y']
    except:
        start_x, start_y = 640, 100
    
    steps = max(30, int(duration_ms / 16))
    path = BezierCurve.generate_path(start_x, start_y, target_x, target_y, steps)
    
    for x, y in path:
        await page.mouse.move(x, y)
        await asyncio.sleep(duration_ms / 1000 / steps)
    
    await page.evaluate(f"() => {{ window.lastMouseX = {target_x}; window.lastMouseY = {target_y}; }}")


async def smooth_click(page, x, y, duration_ms=800):
    await smooth_move(page, x, y, duration_ms)
    await asyncio.sleep(0.1)
    await page.mouse.click(x, y)
    await asyncio.sleep(0.2)


async def smooth_scroll(page, target_y, duration_ms=1000):
    """Smooth scroll animation"""
    current_y = await page.evaluate("() => window.pageYOffset")
    steps = 30
    for i in range(steps + 1):
        t = i / steps
        # Ease-in-out
        ease_t = t * t * (3 - 2 * t)
        y = current_y + (target_y - current_y) * ease_t
        await page.evaluate(f"window.scrollTo(0, {y})")
        await asyncio.sleep(duration_ms / 1000 / steps)


async def wait_for_analysis_complete(page, max_wait=15):
    """Wait for analysis to complete"""
    print("   ⏳ Waiting for analysis...")
    waited = 0
    while waited < max_wait:
        results = await page.query_selector('[data-testid="stExpander"]')
        if results:
            print(f"   ✅ Analysis complete ({waited}s)")
            return True
        await asyncio.sleep(1)
        waited += 1
    print(f"   ⚠️  Timeout after {max_wait}s")
    return False


async def record_demo():
    """Record professional demo with proper scrolling"""
    
    print("🎬 Lumen Demo Recording - Final Version")
    print("=" * 60)
    print()
    print("⚠️  Make sure Streamlit is running on http://localhost:8501")
    print()
    input("Press Enter when ready...")
    print()
    
    async with async_playwright() as p:
        print("🌐 Launching browser (1280x720)...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir="./demo_recordings",
            record_video_size={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        print("🎥 Recording started...")
        print()
        
        # Scene 1: Navigate and show initial state (0-3s)
        print("📍 Scene 1: Initial screen (0-3s)")
        await page.goto('http://localhost:8501', wait_until='networkidle')
        await asyncio.sleep(2)
        
        # Scene 2: Scroll sidebar to show file uploader (3-5s)
        print("📜 Scene 2: Scroll to file uploader (3-5s)")
        # Scroll the main content area to reveal file uploader if needed
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await asyncio.sleep(1)
        
        # Scene 3: Upload file (5-7s)
        print("📤 Scene 3: Upload file (5-7s)")
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files('Sample_Business Plan.xlsx')
            print("   ✅ File uploaded")
            await asyncio.sleep(1)
        else:
            print("   ❌ File input not found!")
            return None
        
        # Scene 4: Wait for analysis (7-15s)
        print("⚙️  Scene 4: Analysis in progress (7-15s)")
        analysis_complete = await wait_for_analysis_complete(page, max_wait=10)
        
        if not analysis_complete:
            print("   ⚠️  Analysis did not complete")
        
        await asyncio.sleep(1)
        
        # Scene 5: Scroll down to show health score and risk summary (15-18s)
        print("📊 Scene 5: Show health score (15-18s)")
        await smooth_scroll(page, 200, 1000)
        await asyncio.sleep(1)
        
        # Scene 6: Continue scrolling to show risk list (18-21s)
        print("📋 Scene 6: Show risk list (18-21s)")
        await smooth_scroll(page, 400, 1000)
        await asyncio.sleep(1)
        
        # Scene 7: Click on first risk item (21-24s)
        print("🔍 Scene 7: Expand risk details (21-24s)")
        risk_items = await page.query_selector_all('[data-testid="stExpander"]')
        print(f"   Found {len(risk_items)} risk items")
        if risk_items and len(risk_items) > 0:
            box = await risk_items[0].bounding_box()
            if box:
                # Scroll to make sure it's visible
                await page.evaluate(f"window.scrollTo({{ top: {box['y'] - 100}, behavior: 'smooth' }})")
                await asyncio.sleep(0.5)
                await smooth_click(page, box['x'] + box['width'] / 2, box['y'] + 20, 600)
                await asyncio.sleep(1)
                print("   ✅ Risk item expanded")
        
        # Scene 8: Scroll through risk details (24-27s)
        print("📖 Scene 8: Review risk details (24-27s)")
        await smooth_scroll(page, 600, 1000)
        await asyncio.sleep(1)
        
        # Scene 9: Scroll down more to show additional risks (27-30s)
        print("📑 Scene 9: Show more risks (27-30s)")
        await smooth_scroll(page, 800, 1000)
        await asyncio.sleep(1)
        
        # Final frame
        print("✨ Scene 10: Final frame (30s)")
        await asyncio.sleep(0.5)
        
        print()
        print("✅ Recording complete!")
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
                video_path = max(video_files, key=lambda p: p.stat().st_mtime)
        
        return video_path


def convert_to_formats(video_path):
    """Convert WebM to GIF and optimized WebM"""
    if not video_path or not video_path.exists():
        print("❌ Video file not found!")
        return
    
    print()
    print("🔄 Converting to output formats...")
    print("=" * 60)
    
    output_webm = Path("lumen_demo.webm")
    output_gif = Path("lumen_demo.gif")
    
    # Copy/optimize WebM
    print("📹 Creating optimized WebM...")
    try:
        subprocess.run([
            "ffmpeg", "-i", str(video_path),
            "-c:v", "libvpx-vp9",
            "-crf", "30",
            "-b:v", "0",
            "-y",
            str(output_webm)
        ], check=True, capture_output=True)
        print(f"   ✅ Created: {output_webm}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        import shutil
        shutil.copy(video_path, output_webm)
        print(f"   ✅ Created: {output_webm} (copy)")
    
    # Create GIF
    print("🎞️  Creating GIF...")
    try:
        subprocess.run([
            "ffmpeg", "-i", str(video_path),
            "-vf", "fps=15,scale=1280:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            "-loop", "0",
            "-y",
            str(output_gif)
        ], check=True, capture_output=True)
        print(f"   ✅ Created: {output_gif}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ⚠️  ffmpeg not available for GIF conversion")
    
    # File sizes
    print()
    print("📦 Output Files:")
    print("=" * 60)
    if output_webm.exists():
        size_mb = output_webm.stat().st_size / 1024 / 1024
        print(f"   WebM: {output_webm} ({size_mb:.2f} MB)")
    if output_gif.exists():
        size_mb = output_gif.stat().st_size / 1024 / 1024
        print(f"   GIF:  {output_gif} ({size_mb:.2f} MB)")
    
    print()
    print("🎉 Demo recording complete!")
    print()
    print("📹 Video shows:")
    print("   ✓ File upload process")
    print("   ✓ Analysis completion")
    print("   ✓ Health score display")
    print("   ✓ Risk list with scrolling")
    print("   ✓ Risk detail expansion")
    print("   ✓ Detailed risk information")


async def main():
    print()
    print("=" * 60)
    print("  LUMEN PROFESSIONAL DEMO RECORDER")
    print("  Final Version with Proper Scrolling")
    print("=" * 60)
    print()
    
    video_path = await record_demo()
    
    if video_path:
        convert_to_formats(video_path)
    else:
        print("❌ Recording failed")


if __name__ == "__main__":
    asyncio.run(main())
