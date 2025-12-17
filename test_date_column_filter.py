"""
Test: Date-Only Column Filter

Verify that date-only column labels are filtered out to prevent redundancy.

Example:
- "必要な年数の中間値 @ 2022-09" → "必要な年数の中間値"
- "IRR（年 @ 2022-08" → "IRR（年"
- "NPV ② @ 2022-08" → "NPV ②"
"""

from src.models import RiskAlert


def test_date_only_column_filter():
    """Test that date-only column labels are filtered out"""
    
    # Test Case 1: Date pattern YYYY-MM
    risk1 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="Low",
        sheet="プロジェクション円",
        cell="G37",
        description="Test",
        row_label="必要な年数の中間値",
        col_label="2022-09"
    )
    
    context1 = risk1.get_context()
    print(f"Test 1: '{context1}'")
    assert context1 == "必要な年数の中間値", f"Expected '必要な年数の中間値', got '{context1}'"
    
    # Test Case 2: Another date pattern
    risk2 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="Low",
        sheet="プロジェクション円",
        cell="F29",
        description="Test",
        row_label="IRR（年",
        col_label="2022-08"
    )
    
    context2 = risk2.get_context()
    print(f"Test 2: '{context2}'")
    assert context2 == "IRR（年", f"Expected 'IRR（年', got '{context2}'"
    
    # Test Case 3: NPV with date
    risk3 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="Low",
        sheet="プロジェクション円",
        cell="F40",
        description="Test",
        row_label="NPV ②",
        col_label="2022-08"
    )
    
    context3 = risk3.get_context()
    print(f"Test 3: '{context3}'")
    assert context3 == "NPV ②", f"Expected 'NPV ②', got '{context3}'"
    
    # Test Case 4: Non-date column label should be kept
    risk4 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="High",
        sheet="Sheet1",
        cell="E5",
        description="Test",
        row_label="Revenue",
        col_label="Scenario A"
    )
    
    context4 = risk4.get_context()
    print(f"Test 4: '{context4}'")
    assert context4 == "Revenue @ Scenario A", f"Expected 'Revenue @ Scenario A', got '{context4}'"
    
    # Test Case 5: Long row label (>30 chars) should drop column even if non-date
    risk5 = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="High",
        sheet="Sheet1",
        cell="E5",
        description="Test",
        row_label="This is a very long row label that exceeds thirty characters",
        col_label="Scenario A"
    )
    
    context5 = risk5.get_context()
    print(f"Test 5: '{context5}'")
    assert context5 == "This is a very long row label that exceeds thirty characters", \
        f"Expected long label only, got '{context5}'"
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_date_only_column_filter()
