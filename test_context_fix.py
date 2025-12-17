"""
Test script to verify context detection improvements.

Run this after making changes to verify:
1. Leftmost cell selection for ranges
2. AI context window extraction (skip formulas)
3. Column position scoring
"""

import re
from openpyxl.utils import column_index_from_string

def test_leftmost_cell():
    """Test leftmost cell selection"""
    print("\n=== Test 1: Leftmost Cell Selection ===")
    
    test_cases = [
        (["H22", "K22"], "H22"),
        (["AB12", "BW12"], "AB12"),
        (["BL24"], "BL24"),
        (["E189", "F189"], "E189"),
    ]
    
    for cells, expected in test_cases:
        # Simulate _get_leftmost_cell logic
        leftmost = cells[0]
        leftmost_col_num = 999999
        
        for cell in cells:
            match = re.match(r'^([A-Z]+)(\d+)$', cell)
            if match:
                col_letter = match.group(1)
                col_num = column_index_from_string(col_letter)
                
                if col_num < leftmost_col_num:
                    leftmost_col_num = col_num
                    leftmost = cell
        
        status = "✓" if leftmost == expected else "✗"
        print(f"{status} {cells} -> {leftmost} (expected: {expected})")

def test_column_scoring():
    """Test column position scoring"""
    print("\n=== Test 2: Column Position Scoring ===")
    
    test_cases = [
        ("A", 1, 300),    # A column = 300 points
        ("T", 20, 110),   # T column = 110 points
        ("U", 21, 90),    # U column = 90 points
        ("AD", 30, 0),    # AD column = 0 points
        ("AE", 31, -10),  # AE column = -10 points
        ("BW", 75, -450), # BW column = -450 points
    ]
    
    for col_letter, col_num, expected_score in test_cases:
        # Simulate column scoring logic
        if col_num <= 20:  # A-T columns (1-20)
            score = 300 - (col_num - 1) * 10
        elif col_num <= 30:  # U-AD columns (21-30)
            score = 90 - (col_num - 21) * 9
        else:  # AE+ columns (31+)
            score = -(col_num - 30) * 10
        
        status = "✓" if score == expected_score else "✗"
        print(f"{status} Column {col_letter} (#{col_num}) = {score} points (expected: {expected_score})")

def test_formula_skip():
    """Test formula string detection"""
    print("\n=== Test 3: Formula String Detection ===")
    
    test_cases = [
        ("=BJ24", True),           # Formula string
        ("=BI24", True),           # Formula string
        ("Revenue", False),        # Text label
        ("Fixed salary", False),   # Text label
        ("123", True),             # Numeric string
        ("1,234.56", True),        # Numeric string with formatting
        ("", True),                # Empty string
        ("  ", True),              # Whitespace only
    ]
    
    for value, should_skip in test_cases:
        # Simulate skip logic
        skip = False
        
        if not value or not value.strip():
            skip = True
        elif value.startswith('='):
            skip = True
        else:
            cleaned = value.replace('.', '').replace('-', '').replace(',', '').replace(' ', '').replace('+', '')
            if cleaned.isdigit():
                skip = True
        
        status = "✓" if skip == should_skip else "✗"
        action = "SKIP" if skip else "KEEP"
        print(f"{status} '{value}' -> {action} (expected: {'SKIP' if should_skip else 'KEEP'})")

if __name__ == "__main__":
    test_leftmost_cell()
    test_column_scoring()
    test_formula_skip()
    print("\n=== All Tests Complete ===")
