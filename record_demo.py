#!/usr/bin/env python3
"""
Lumen Professional Demo Recording Script
Automated browser recording with human-like mouse movements using Playwright
"""

import asyncio
import subprocess
import time
import math
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image
import os


class BezierCurve:
    """Generate smooth Bezier curve points for human-like mouse movement"""
    
    @staticmethod
    def cubic_bezier(t, p0, p1, p2, p3):
        """Calculate point on cubic Bezier curve at parameter t (0 to 1)"""
        return (
            (1 - t) ** 3 * p0 +
            3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * p2 +
            t ** 3 * p3
        )
    
    @staticmethod
    def generate_path(start_x, start_y, end_x, end_y, steps=50):
        """Generate smooth path from start to end with natural curve"""
        # Add control points for natural curve
        dx = end_x - start_x
        dy = end_y - start_y
        
        # Control points create slight arc
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
    """Move mouse smoothly along Bezier curve"""
    # Get current position (start from center if first move)
    try:
        current_pos = await page.evaluate("() => ({ x: window.lastMouseX || 640, y: window.lastMouseY || 100 })")
        start_x = current_pos['x']
        start_y = current_pos['y']
    except:
        start_x, start_y = 640, 100
    
    # Generate smooth path
    steps = max(30, int(duration_ms / 16))  # ~60fps
    path = BezierCurve.generate_path(start_x, start_y, target_x, target_y, steps)
    
    # Move along path
    for x, y in path:
        await page.mouse.move(x, y)
        await asyncio.sleep(duration_ms / 1000 / steps)
    
    # Store position for next move
    await page.evaluate(f"() => {{ window.lastMouseX = {target_x}; window.lastMouseY = {target_y}; }}")


async def smooth_click(page, x, y, duration_ms=800):
    """Move smoothly and click"""
    await smooth_move(page, x, y, duration_ms)
    await asyncio.sleep(0.1)
    await page.mouse.click(x, y)
    await asyncio.sleep(0.2)


async def record_demo():
    """Record professional demo of Lumen application"""
    
    print("🎬 Starting Lumen Demo Recording...")
    print("=" * 60)
    
    # Start Streamlit app
    print("📱 Starting Streamlit app...")
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    print("⏳ Waiting for app to initialize...")
    await asyncio.sleep(8)
    
    try:
        async with async_playwright() as p:
            # Launch browser with video recording
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
            
            # Navigate to app
            await page.goto('http://localhost:8501')
            await asyncio.sleep(3)
            
            # Scene 1: Upload file (0-3s)
            print("📤 Scene 1: File upload...")
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files('Sample_Business Plan.xlsx')
                print("   ✅ File selected")
                await asyncio.sleep(1)
            
            # Scene 2: Wait for analysis to complete (3-20s)
            print("⚙️  Scene 2: Waiting for analysis to complete...")
            # Wait for spinner to appear
            await asyncio.sleep(2)
            
            # Wait for analysis to finish (look for results)
            max_wait = 30  # Maximum 30 seconds
            wait_time = 0
            analysis_complete = False
            
            while wait_time < max_wait and not analysis_complete:
                # Check if results are visible (expanders appear after analysis)
                expanders = await page.query_selector_all('[data-testid="stExpander"]')
                if len(expanders) > 0:
                    print(f"   ✅ Analysis complete! ({wait_time}s)")
                    analysis_complete = True
                    break
                
                await asyncio.sleep(1)
                wait_time += 1
                if wait_time % 5 == 0:
                    print(f"   ⏳ Still analyzing... ({wait_time}s)")
            
            if not analysis_complete:
                print("   ⚠️  Analysis taking longer than expected")
            
            # Give UI time to settle
            await asyncio.sleep(2)
            
            # Scene 3: Scroll to view results (12-16s)
            print("📊 Scene 3: Viewing results...")
            await page.evaluate("window.scrollTo({ top: 400, behavior: 'smooth' })")
            await asyncio.sleep(2)
            
            # Scene 4: Click on a risk item (16-20s)
            print("🔍 Scene 4: Examining risk details...")
            # Try to find and click first risk item
            risk_items = await page.query_selector_all('[data-testid="stExpander"]')
            if risk_items and len(risk_items) > 0:
                box = await risk_items[0].bounding_box()
                if box:
                    await smooth_click(page, box['x'] + box['width'] / 2, box['y'] + 20, 600)
                    await asyncio.sleep(2)
            
            # Scene 5: Scroll through details (20-24s)
            print("📋 Scene 5: Reviewing details...")
            await page.evaluate("window.scrollTo({ top: 600, behavior: 'smooth' })")
            await asyncio.sleep(2)
            
            # Scene 6: Scroll back to top (24-27s)
            print("⬆️  Scene 6: Return to overview...")
            await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
            await asyncio.sleep(2)
            
            # Final pause
            await asyncio.sleep(1)
            
            print()
            print("✅ Recording complete!")
            print("💾 Saving video...")
            
            # Close browser (triggers video save)
            await context.close()
            await browser.close()
            
            # Get video path
            video_path = None
            recordings_dir = Path("./demo_recordings")
            if recordings_dir.exists():
                video_files = list(recordings_dir.glob("*.webm"))
                if video_files:
                    video_path = video_files[0]
            
            return video_path
            
    finally:
        # Stop Streamlit
        print("🛑 Stopping Streamlit app...")
        streamlit_process.terminate()
        streamlit_process.wait()


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
    except subprocess.CalledProcessError:
        # Fallback: just copy
        import shutil
        shutil.copy(video_path, output_webm)
        print(f"   ✅ Created: {output_webm} (copy)")
    except FileNotFoundError:
        print("   ⚠️  ffmpeg not found, copying original...")
        import shutil
        shutil.copy(video_path, output_webm)
        print(f"   ✅ Created: {output_webm} (copy)")
    
    # Create GIF
    print("🎞️  Creating GIF (this may take a moment)...")
    try:
        # Use ffmpeg for better quality GIF
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
        print("   💡 Install ffmpeg for GIF support: brew install ffmpeg")
    
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
    print("Usage:")
    print("   - Embed WebM in modern websites (smaller, better quality)")
    print("   - Use GIF for maximum compatibility (email, docs, etc.)")


async def main():
    """Main execution"""
    print()
    print("=" * 60)
    print("  LUMEN PROFESSIONAL DEMO RECORDER")
    print("  Automated recording with human-like interactions")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    try:
        import playwright
        print("   ✅ Playwright installed")
    except ImportError:
        print("   ❌ Playwright not found!")
        print("   Install: pip install playwright && playwright install chromium")
        return
    
    try:
        from PIL import Image
        print("   ✅ Pillow installed")
    except ImportError:
        print("   ⚠️  Pillow not found (optional for GIF)")
        print("   Install: pip install Pillow")
    
    print()
    
    # Record demo
    video_path = await record_demo()
    
    # Convert to formats
    if video_path:
        convert_to_formats(video_path)
    else:
        print("❌ Recording failed - no video file generated")


if __name__ == "__main__":
    asyncio.run(main())
