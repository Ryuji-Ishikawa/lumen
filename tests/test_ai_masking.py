"""
AI Data Masking Test Suite

Tests enterprise-grade data masking to ensure NO raw financial values
are ever sent to LLM providers.

CRITICAL: This is a security feature. All tests must pass.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ai_explainer import DataMasker, MaskedContext


class TestDataMasking:
    """Test suite for data masking"""
    
    def test_mask_simple_formula(self):
        """Test masking a simple formula with numbers"""
        formula = "=B2*1.1"
        
        masked, mapping = DataMasker.mask_formula(formula)
        
        print(f"\n✓ Original: {formula}")
        print(f"✓ Masked: {masked}")
        print(f"✓ Mapping: {mapping}")
        
        # Should replace number with token
        assert "<NUM_1>" in masked, "Should contain token"
        assert "1.1" not in masked, "Should not contain raw number"
        assert mapping["<NUM_1>"] == 1.1, "Mapping should be correct"
    
    def test_mask_complex_formula(self):
        """Test masking a complex formula with multiple numbers"""
        formula = "=B2*1.1+5000-C3*0.95"
        
        masked, mapping = DataMasker.mask_formula(formula)
        
        print(f"\n✓ Original: {formula}")
        print(f"✓ Masked: {masked}")
        print(f"✓ Mapping: {mapping}")
        
        # Should replace all numbers
        assert "<NUM_1>" in masked, "Should contain first token"
        assert "<NUM_2>" in masked, "Should contain second token"
        assert "<NUM_3>" in masked, "Should contain third token"
        
        # Should not contain raw numbers
        assert "1.1" not in masked
        assert "5000" not in masked
        assert "0.95" not in masked
        
        # Mapping should be correct
        assert len(mapping) == 3, "Should have 3 mappings"
        assert mapping["<NUM_1>"] == 1.1
        assert mapping["<NUM_2>"] == 5000.0
        assert mapping["<NUM_3>"] == 0.95
    
    def test_mask_value(self):
        """Test masking a single value"""
        # Numeric values should be masked
        assert DataMasker.mask_value(10000000) == "<NUM_VAL>"
        assert DataMasker.mask_value(1.5) == "<NUM_VAL>"
        
        # Non-numeric values should be converted to string
        assert DataMasker.mask_value("Revenue") == "Revenue"
        
        print("\n✓ Single value masking works correctly")
    
    def test_create_masked_context(self):
        """Test creating a complete masked context"""
        formula = "=B2*1.1+5000"
        cell_labels = {
            'row_label': '売上高',
            'col_label': '04-2025'
        }
        dependencies = ['B2', 'C3']
        
        context = DataMasker.create_masked_context(formula, cell_labels, dependencies)
        
        print(f"\n✓ Masked Context:")
        print(f"  Formula: {context.formula_structure}")
        print(f"  Labels: {context.cell_labels}")
        print(f"  Dependencies: {context.dependencies}")
        print(f"  Mapping: {context.value_mapping}")
        
        # Verify masking
        assert "<NUM_" in context.formula_structure, "Formula should be masked"
        assert "1.1" not in context.formula_structure, "Raw numbers should be removed"
        assert "5000" not in context.formula_structure, "Raw numbers should be removed"
        
        # Verify context is preserved
        assert context.cell_labels == cell_labels
        assert context.dependencies == dependencies
        assert len(context.value_mapping) == 2
    
    def test_no_numbers_in_formula(self):
        """Test formula with no numbers"""
        formula = "=B2+C3-D4"
        
        masked, mapping = DataMasker.mask_formula(formula)
        
        print(f"\n✓ Original: {formula}")
        print(f"✓ Masked: {masked}")
        
        # Should remain unchanged
        assert masked == formula, "Formula without numbers should be unchanged"
        assert len(mapping) == 0, "Should have no mappings"
    
    def test_security_guarantee(self):
        """
        CRITICAL TEST: Verify that masked context NEVER contains raw values
        """
        # Simulate real P&L data
        sensitive_formula = "=10000000*1.15+5000000"  # Revenue calculation
        
        masked, mapping = DataMasker.mask_formula(sensitive_formula)
        
        print(f"\n✓ SECURITY TEST:")
        print(f"  Original (SENSITIVE): {sensitive_formula}")
        print(f"  Masked (SAFE): {masked}")
        
        # CRITICAL: Raw values must NOT appear in masked version
        assert "10000000" not in masked, "SECURITY BREACH: Raw value leaked!"
        assert "5000000" not in masked, "SECURITY BREACH: Raw value leaked!"
        
        # Tokens should be present
        assert "<NUM_" in masked, "Tokens should be present"
        
        print("✓ SECURITY GUARANTEE: No raw values in masked output")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
