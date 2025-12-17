#!/usr/bin/env python3
"""
Debug demo recording - check what's happening
"""

import asyncio
from playwright.async_api import async_playwright


async def debug_recording():
    """Debug the recording process"""
    
    print("🔍 Debug Demo Recording")
    print("=" * 60)
    
    async with async_playwright() as p:
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        print("📍 Step 1: Navigate to app")
        await page.goto('http://localhost:8501', wait_until='networkidle')
        await asyncio.sleep(2)
        
        print("📍 Step 2: Find file input")
        file_input = await page.query_selector('input[type="file"]')
        if not file_input:
            print("❌ File input not found!")
            await browser.close()
            return
        print("✅ File input found")
        
        print("📍 Step 3: Upload file")
        await file_input.set_input_files('Demo_Budget_With_Risks.xlsx')
        print("✅ File uploaded")
        
        print("📍 Step 4: Wait and check for analysis")
        for i in range(30):
            await asyncio.sleep(1)
            
            # Check for "Parsing Excel" text
            parsing = await page.query_selector('text="Parsing Excel"')
            if parsing:
                print(f"   [{i}s] 🔄 Parsing Excel...")
            
            # Check for expanders (results)
            expanders = await page.query_selector_all('[data-testid="stExpander"]')
            if expanders:
                print(f"   [{i}s] ✅ Found {len(expanders)} expanders - Analysis complete!")
                break
            
            # Check for any error messages
            errors = await page.query_selector_all('[data-testid="stException"]')
            if errors:
                print(f"   [{i}s] ❌ Error detected!")
                for error in errors:
                    text = await error.inner_text()
                    print(f"      {text}")
                break
            
            print(f"   [{i}s] ⏳ Waiting...")
        
        print("\n📍 Step 5: Check current page state")
        # Get all text content
        body = await page.query_selector('body')
        if body:
            text = await body.inner_text()
            if "Parsing Excel" in text:
                print("   🔄 Still showing 'Parsing Excel'")
            if "Health Score" in text or "健全性スコア" in text:
                print("   ✅ Health score visible")
            if "整合性リスク" in text:
                print("   ✅ Integrity risks tab visible")
        
        print("\n⏸️  Pausing for 10 seconds - DO NOT TOUCH THE BROWSER")
        await asyncio.sleep(10)
        
        print("✅ Debug complete")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_recording())
