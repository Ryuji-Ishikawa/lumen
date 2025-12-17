"""
Test the Context Quality Filter

This test verifies that the _is_poor_quality_label method correctly
identifies garbage labels that should trigger AI recovery.
"""

from src.analyzer import ModelAnalyzer

def test_quality_filter():
    """Test that quality filter catches all garbage patterns"""
    
    analyzer = ModelAnalyzer()
    
    # Test cases: (label, should_be_poor_quality, reason)
    test_cases = [
        # Formula debris
        ("=(D18*E18)", True, "Formula debris with ="),
        ("=SUM(A1:A10)", True, "Formula with ="),
        
        # Math operators
        ("A1*B2", True, "Math operators without spaces"),
        ("100+200", True, "Math operators without spaces"),
        ("A1/B2", True, "Division operator"),
        
        # Cell addresses (case insensitive)
        ("E92", True, "Cell address uppercase"),
        ("F24", True, "Cell address"),
        ("BN13", True, "Multi-letter cell address"),
        ("AA1", True, "Multi-letter cell address"),
        ("f24", True, "Cell address lowercase"),
        
        # Generic stopwords
        ("Total", True, "Generic stopword"),
        ("Sum", True, "Generic stopword"),
        ("合計", True, "Japanese stopword"),
        
        # Symbols/numeric only
        ("-", True, "Symbol only"),
        ("0", True, "Single digit"),
        ("123", True, "Pure number"),
        ("---", True, "Multiple symbols"),
        
        # Too short/long
        ("A", True, "Too short (1 char)"),
        ("X" * 51, True, "Too long (>50 chars)"),
        
        # Good quality labels (should pass)
        ("Cash Balance", False, "Good label with space"),
        ("Personnel Cost", False, "Good label"),
        ("Beginning Balance", False, "Good label"),
        ("現金残高", False, "Japanese label"),
        ("Revenue 2024", False, "Label with year"),
        ("Q1 Sales", False, "Label with quarter"),
    ]
    
    print("\n" + "="*80)
    print("QUALITY FILTER TEST")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for label, expected_poor, reason in test_cases:
        result = analyzer._is_poor_quality_label(label, verbose=False)
        status = "✓ PASS" if result == expected_poor else "✗ FAIL"
        
        if result == expected_poor:
            passed += 1
        else:
            failed += 1
            print(f"\n{status}: '{label}'")
            print(f"  Reason: {reason}")
            print(f"  Expected: {'Poor' if expected_poor else 'Good'}")
            print(f"  Got: {'Poor' if result else 'Good'}")
    
    print(f"\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80)
    
    if failed > 0:
        print("\n❌ QUALITY FILTER HAS ISSUES")
        return False
    else:
        print("\n✅ QUALITY FILTER WORKING CORRECTLY")
        return True

if __name__ == "__main__":
    success = test_quality_filter()
    exit(0 if success else 1)
