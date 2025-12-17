"""
Test: Japanese Date-Only Column Filter

Verify that the fix works with the actual examples from the user's CSV.
"""

from src.models import RiskAlert


def test_japanese_examples_from_csv():
    """Test with actual examples from the user's CSV that had @ symbols"""
    
    print("Testing examples from user's CSV:\n")
    
    # Test Case 1: From line 12 of old CSV
    risk1 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="High",
        sheet="プロジェクションVDN",
        cell="F4",
        description="Test",
        row_label="全体開発費（百万VDN）※7年償却",
        col_label="2022-08"
    )
    
    context1 = risk1.get_context()
    print(f"1. Old: '全体開発費（百万VDN）※7年償却 @ 2022-08'")
    print(f"   New: '{context1}'")
    assert " @ " not in context1, f"@ symbol should be removed, got: '{context1}'"
    assert context1 == "全体開発費（百万VDN）※7年償却", f"Expected row label only, got: '{context1}'"
    print(f"   ✅ PASS\n")
    
    # Test Case 2: From line 13 of old CSV
    risk2 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="High",
        sheet="プロジェクションVDN",
        cell="F8",
        description="Test",
        row_label="バイク製造費（百万VDN）",
        col_label="2022-08"
    )
    
    context2 = risk2.get_context()
    print(f"2. Old: 'バイク製造費（百万VDN） @ 2022-08'")
    print(f"   New: '{context2}'")
    assert " @ " not in context2, f"@ symbol should be removed, got: '{context2}'"
    assert context2 == "バイク製造費（百万VDN）", f"Expected row label only, got: '{context2}'"
    print(f"   ✅ PASS\n")
    
    # Test Case 3: From line 29 of old CSV (the user's specific example)
    risk3 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="Low",
        sheet="プロジェクション円",
        cell="G37",
        description="Test",
        row_label="必要な年数の中間値",
        col_label="2022-09"
    )
    
    context3 = risk3.get_context()
    print(f"3. Old: '必要な年数の中間値 @ 2022-09' (USER'S EXAMPLE)")
    print(f"   New: '{context3}'")
    assert " @ " not in context3, f"@ symbol should be removed, got: '{context3}'"
    assert context3 == "必要な年数の中間値", f"Expected row label only, got: '{context3}'"
    print(f"   ✅ PASS\n")
    
    # Test Case 4: From line 28 of old CSV
    risk4 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="Low",
        sheet="プロジェクション円",
        cell="F29",
        description="Test",
        row_label="IRR（年",
        col_label="2022-08"
    )
    
    context4 = risk4.get_context()
    print(f"4. Old: 'IRR（年 @ 2022-08'")
    print(f"   New: '{context4}'")
    assert " @ " not in context4, f"@ symbol should be removed, got: '{context4}'"
    assert context4 == "IRR（年", f"Expected row label only, got: '{context4}'"
    print(f"   ✅ PASS\n")
    
    # Test Case 5: From line 32 of old CSV
    risk5 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="Low",
        sheet="プロジェクション円",
        cell="F40",
        description="Test",
        row_label="NPV ②",
        col_label="2022-08"
    )
    
    context5 = risk5.get_context()
    print(f"5. Old: 'NPV ② @ 2022-08'")
    print(f"   New: '{context5}'")
    assert " @ " not in context5, f"@ symbol should be removed, got: '{context5}'"
    assert context5 == "NPV ②", f"Expected row label only, got: '{context5}'"
    print(f"   ✅ PASS\n")
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nSummary:")
    print("- Date-only column labels (YYYY-MM format) are now filtered out")
    print("- @ symbol no longer appears in context labels")
    print("- Row labels are shown cleanly without redundant date information")


if __name__ == "__main__":
    test_japanese_examples_from_csv()
