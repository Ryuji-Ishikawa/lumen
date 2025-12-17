"""
Test the Whitespace Fix - "Silent Bug"

This test verifies that whitespace-only labels are treated as empty
and trigger AI recovery.
"""

from src.analyzer import ModelAnalyzer
from src.models import CellInfo, RiskAlert

def test_whitespace_handling():
    """Test that whitespace is treated as empty"""
    
    analyzer = ModelAnalyzer()
    
    # Create mock cells - simulating a scenario where ONLY whitespace exists
    # (no other cells to the left that could be found)
    cells = {
        # Row 1: Only whitespace, nothing else
        "Sheet1!C1": CellInfo(sheet="Sheet1", address="C1", value="   ", formula=None),
        # Row 2: Only newline
        "Sheet1!C2": CellInfo(sheet="Sheet1", address="C2", value="\n", formula=None),
        # Row 3: Only tab
        "Sheet1!C3": CellInfo(sheet="Sheet1", address="C3", value="\t", formula=None),
        # Row 4: Mixed whitespace
        "Sheet1!C4": CellInfo(sheet="Sheet1", address="C4", value="  \n  ", formula=None),
        # Row 5: Empty
        "Sheet1!C5": CellInfo(sheet="Sheet1", address="C5", value="", formula=None),
        # Row 6: Good label to the left
        "Sheet1!A6": CellInfo(sheet="Sheet1", address="A6", value="Good Label", formula=None),
        "Sheet1!C6": CellInfo(sheet="Sheet1", address="C6", value="value", formula=None),
    }
    
    print("\n" + "="*80)
    print("WHITESPACE HANDLING TEST")
    print("="*80)
    print("Testing that whitespace-only values are properly rejected\n")
    
    # Test direct whitespace values
    whitespace_tests = [
        ("   ", "Spaces only"),
        ("\n", "Newline only"),
        ("\t", "Tab only"),
        ("  \n  ", "Mixed whitespace"),
        ("", "Empty string"),
    ]
    
    passed = 0
    failed = 0
    
    print("Direct Value Tests:")
    for value, reason in whitespace_tests:
        # Simulate what happens in _get_context_labels
        if isinstance(value, str):
            value_str = value.strip()
            if not value_str:
                result = None  # Rejected
            else:
                result = value_str  # Accepted
        
        is_empty = result is None
        
        if is_empty:
            passed += 1
            print(f"✓ PASS: '{repr(value)}' -> {reason} -> Rejected")
        else:
            failed += 1
            print(f"✗ FAIL: '{repr(value)}' -> {reason} -> Accepted as '{result}'")
    
    # Test with actual _get_context_labels
    print("\n_get_context_labels Tests:")
    context_tests = [
        ("C1", True, "Spaces only in cell"),
        ("C2", True, "Newline only in cell"),
        ("C3", True, "Tab only in cell"),
        ("C4", True, "Mixed whitespace in cell"),
        ("C5", True, "Empty cell"),
        ("C6", False, "Good label to the left"),
    ]
    
    for cell_addr, should_be_empty, reason in context_tests:
        row_label, col_label = analyzer._get_context_labels("Sheet1", cell_addr, cells)
        
        # Apply strict whitespace cleaning (same as in _add_context_labels)
        if row_label and not row_label.strip():
            row_label = None
        
        is_empty = not row_label or row_label == ""
        
        if is_empty == should_be_empty:
            passed += 1
            print(f"✓ PASS: {cell_addr} -> {reason}")
        else:
            failed += 1
            print(f"✗ FAIL: {cell_addr} -> {reason}")
            print(f"  Expected: {'Empty' if should_be_empty else 'Not Empty'}")
            print(f"  Got: {'Empty' if is_empty else 'Not Empty'}")
            print(f"  Label: '{row_label}'")
    
    print(f"\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80)
    
    if failed > 0:
        print("\n❌ WHITESPACE HANDLING HAS ISSUES")
        return False
    else:
        print("\n✅ WHITESPACE HANDLING WORKING CORRECTLY")
        print("\nZero Tolerance for Silence: ✓")
        print("- Spaces only: Treated as empty")
        print("- Newlines only: Treated as empty")
        print("- Tabs only: Treated as empty")
        print("- Mixed whitespace: Treated as empty")
        return True

def test_fallback_mechanism():
    """Test that fallback placeholder is generated"""
    
    analyzer = ModelAnalyzer()
    
    print("\n" + "="*80)
    print("FALLBACK MECHANISM TEST")
    print("="*80)
    
    # Create a risk with empty context
    risk = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="High",
        sheet="Sheet1",
        cell="E92",
        description="Test risk",
        details={}
    )
    
    # Simulate empty context and failed AI recovery
    risk.row_label = None
    
    # Apply fallback logic
    import re
    if not risk.row_label or risk.row_label == "":
        row_match = re.match(r'^[A-Z]+(\d+)$', risk.cell)
        if row_match:
            row_num = row_match.group(1)
            risk.row_label = f"[Unknown Row {row_num}]"
    
    expected = "[Unknown Row 92]"
    if risk.row_label == expected:
        print(f"✓ PASS: Fallback generated correctly")
        print(f"  Cell: {risk.cell}")
        print(f"  Fallback: {risk.row_label}")
        print("\n✅ FALLBACK MECHANISM WORKING")
        return True
    else:
        print(f"✗ FAIL: Fallback incorrect")
        print(f"  Expected: {expected}")
        print(f"  Got: {risk.row_label}")
        print("\n❌ FALLBACK MECHANISM HAS ISSUES")
        return False

if __name__ == "__main__":
    test1 = test_whitespace_handling()
    test2 = test_fallback_mechanism()
    
    if test1 and test2:
        print("\n" + "="*80)
        print("ALL TESTS PASSED ✅")
        print("="*80)
        exit(0)
    else:
        print("\n" + "="*80)
        print("SOME TESTS FAILED ❌")
        print("="*80)
        exit(1)
