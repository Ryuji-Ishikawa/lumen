#!/usr/bin/env python3
"""
Lumen Perfect Demo Recording
Follows exact user specifications with sidebar scrolling
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import subprocess


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
    """Record demo following exact user specifications"""
    
    print("🎬 Lumen Perfect Demo Recording")
    print("=" * 60)
    print()
    print("⚠️  Streamlit must be running on http://localhost:8501")
    print()
    input("Press Enter when ready...")
    print()
    
    async with async_playwright() as p:
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(headless=True)
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
        
        # 2) Scroll LEFT sidebar down (2-4s)
        print("2️⃣  Scroll sidebar down (2-4s)")
        # Scroll sidebar much more to show file uploader (1.3x more)
        try:
            await smooth_scroll_element(page, '[data-testid="stSidebar"] > div', 650, 1000)
        except:
            print("   ℹ️  Sidebar not scrollable (content fits)")
        await asyncio.sleep(1)
        
        # 3) Click file upload button (4-6s)
        print("3️⃣  Upload file (4-6s)")
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files('Demo_Budget_With_Risks.xlsx')
            print("   ✅ File uploaded")
            await asyncio.sleep(1)
        else:
            print("   ❌ File input not found!")
            return None
        
        # 4) Wait for analysis (6-12s)
        print("4️⃣  Analysis (6-12s)")
        await wait_for_analysis(page, max_wait=8)
        await asyncio.sleep(1)
        
        # 5) Health score display (12-14s)
        print("5️⃣  Health score (12-14s)")
        await asyncio.sleep(2)

        
        # 6) Scroll down main content (14-16s)
        print("6️⃣  Scroll main content (14-16s)")
        await page.evaluate("window.scrollTo({ top: 3000, behavior: 'smooth' })")
        await asyncio.sleep(2)
        
        # 7) Click "整合性リスク" tab (16-18s)
        print("7️⃣  Click 整合性リスク tab (16-18s)")
        # Find and click the tab
        tabs = await page.query_selector_all('button[role="tab"]')
        for tab in tabs:
            text = await tab.inner_text()
            if '整合性' in text or 'Integrity' in text:
                await tab.click()
                print("   ✅ Tab clicked")
                await asyncio.sleep(1)
                break
        await asyncio.sleep(1)
        
        # 8) Scroll down (18-20s)
        print("8️⃣  Scroll down (18-20s)")
        await page.evaluate("window.scrollTo({ top: 4000, behavior: 'smooth' })")
        await asyncio.sleep(2)
        
        # 9) Select a risk from list (20-22s)
        print("9️⃣  Select risk (20-22s)")
        # Wait a bit for UI to settle after tab click
        await asyncio.sleep(1)
        risk_items = await page.query_selector_all('[data-testid="stExpander"]')
        print(f"   Found {len(risk_items)} risks")
        if risk_items and len(risk_items) > 0:
            # Scroll to make the risk item visible
            box = await risk_items[0].bounding_box()
            if box:
                # Scroll so the item is in the middle of viewport
                await page.evaluate(f"window.scrollTo({{ top: {max(0, box['y'] - 200)}, behavior: 'smooth' }})")
                await asyncio.sleep(1)
            # Use JavaScript click as fallback
            await page.evaluate("document.querySelectorAll('[data-testid=\"stExpander\"]')[0].click()")
            print("   ✅ Risk selected")
            await asyncio.sleep(1)
        else:
            print("   ⚠️  No risks found")
        await asyncio.sleep(1)
        
        # 10) Scroll to show risk details (22-25s)
        print("🔟 Show risk details (22-25s)")
        await page.evaluate("window.scrollTo({ top: 5000, behavior: 'smooth' })")
        await asyncio.sleep(2)
        
        # Continue scrolling to show more details (25-28s)
        await page.evaluate("window.scrollTo({ top: 6000, behavior: 'smooth' })")
        await asyncio.sleep(2)
        
        # Final frame (28-30s)
        print("✨ Final frame (28-30s)")
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
    print("  LUMEN PERFECT DEMO")
    print("  Exact user specifications")
    print("=" * 60)
    print()
    
    video_path = await record_demo()
    if video_path:
        convert_to_formats(video_path)
    else:
        print("❌ Failed")


if __name__ == "__main__":
    asyncio.run(main())
