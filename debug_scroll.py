#!/usr/bin/env python3
"""
Debug Streamlit scroll structure
"""

import asyncio
from playwright.async_api import async_playwright


async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto('http://localhost:8501')
        await asyncio.sleep(3)
        
        # Upload file
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files('Sample_Business Plan.xlsx')
            await asyncio.sleep(8)
        
        # Find scrollable elements
        result = await page.evaluate("""
            () => {
                const elements = [];
                
                // Check common selectors
                const selectors = [
                    'body',
                    '[data-testid="stAppViewContainer"]',
                    '[data-testid="stApp"]',
                    '.main',
                    '[data-testid="stMainBlockContainer"]',
                    'section.main'
                ];
                
                selectors.forEach(sel => {
                    const el = document.querySelector(sel);
                    if (el) {
                        elements.push({
                            selector: sel,
                            scrollHeight: el.scrollHeight,
                            clientHeight: el.clientHeight,
                            scrollTop: el.scrollTop,
                            isScrollable: el.scrollHeight > el.clientHeight
                        });
                    }
                });
                
                return elements;
            }
        """)
        
        print("\n📊 Scrollable Elements:")
        print("=" * 80)
        for el in result:
            print(f"\nSelector: {el['selector']}")
            print(f"  scrollHeight: {el['scrollHeight']}px")
            print(f"  clientHeight: {el['clientHeight']}px")
            print(f"  scrollTop: {el['scrollTop']}px")
            print(f"  isScrollable: {el['isScrollable']}")
        
        print("\n" + "=" * 80)
        print("\nPress Enter to close...")
        input()
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug())
