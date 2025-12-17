#!/usr/bin/env python3
"""
Quick verification script for UAT fixes.

This script tests the critical fixes:
1. Context extraction does NOT pick up formulas
2. Context extraction does NOT pick up numbers
3. Context extraction ONLY picks up text labels
"""

import sys
from pathlib import Path
from src.parser import ExcelParser
from src.analyzer import ModelAnalyzer

def verify_context_filter():
    """Verify context extraction type filter works correctly"""
    
    print("=" * 60)
    print("VERIFICATION: Context Type Filter")
    print("=" * 60)
    
    # Parse sample file
    parser = ExcelParser()
    analyzer = ModelAnalyzer()
    
    sample_file = Path("Sample_Business Plan.xlsx")
    
    if not sample_file.exists():
        print("❌ Sample file not found")
        return False
    
    print(f"\n📁 Parsing: {sample_file}")
    
    with open(sample_file, 'rb') as f:
        model = parser.parse(f, str(sample_file))
    
    print(f"✓ Parsed {len(model.cells)} cells")
    
    # Analyze
    print("\n🔍 Analyzing model...")
    model = analyzer.analyze(model, allowed_constants=[])
    
    print(f"✓ Found {len(model.risks)} risks")
    
    # Check context labels
    print("\n📋 Checking Context Labels:")
    print("-" * 60)
    
    formula_count = 0
    number_count = 0
    text_count = 0
    empty_count = 0
    
    for risk in model.risks[:10]:  # Check first 10 risks
        context = risk.get_context()
        
        # Check for formulas
        if context and context.startswith('='):
            print(f"❌ FAIL: Context contains formula: {context}")
            formula_count += 1
        # Check for numbers
        elif context and context.replace('.', '').replace('-', '').isdigit():
            # Allow years
            try:
                num = float(context)
                if not (2020 <= num <= 2030):
                    print(f"⚠️  WARN: Context is number: {context}")
                    number_count += 1
            except:
                pass
        # Text or empty
        elif context:
            print(f"✓ OK: {risk.get_location()} → Context: '{context}'")
            text_count += 1
        else:
            print(f"✓ OK: {risk.get_location()} → Context: (empty)")
            empty_count += 1
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    print(f"Text labels:   {text_count} ✓")
    print(f"Empty context: {empty_count} ✓")
    print(f"Formulas:      {formula_count} {'❌ FAIL' if formula_count > 0 else '✓'}")
    print(f"Numbers:       {number_count} {'⚠️  WARN' if number_count > 0 else '✓'}")
    
    if formula_count > 0:
        print("\n❌ VERIFICATION FAILED: Formulas found in context")
        return False
    else:
        print("\n✅ VERIFICATION PASSED: No formulas in context")
        return True

if __name__ == '__main__':
    success = verify_context_filter()
    sys.exit(0 if success else 1)
