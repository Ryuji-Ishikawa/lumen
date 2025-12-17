#!/usr/bin/env python3
"""
Test what Lumen actually detects in Sample_Business Plan.xlsx
"""

import sys
sys.path.insert(0, 'src')

from parser import parse_excel_file
from analyzer import analyze_workbook

print("=" * 80)
print("TESTING LUMEN DETECTION")
print("=" * 80)
print()

# Test Sample file
print("📄 Testing: Sample_Business Plan.xlsx")
print()

try:
    wb_data = parse_excel_file('Sample_Business Plan.xlsx')
    results = analyze_workbook(wb_data)
    
    print(f"Total risks found: {len(results.all_risks)}")
    print()
    
    # Group by category
    by_category = {}
    for risk in results.all_risks:
        cat = risk.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(risk)
    
    for cat, risks in by_category.items():
        print(f"{cat}: {len(risks)} risks")
        for risk in risks[:3]:  # Show first 3
            print(f"  - {risk.title}")
    
    print()
    print("=" * 80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
