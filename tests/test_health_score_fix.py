"""
Health Score Fix Test

Tests the improved health score calculation with psychological safety.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.analyzer import ModelAnalyzer
from src.models import RiskAlert


class TestHealthScoreFix:
    """Test improved health score calculation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.analyzer = ModelAnalyzer()
    
    def test_floor_minimum_20(self):
        """Test that score never goes below 20 (psychological safety)"""
        # Create many high risks (would result in 0 with old formula)
        risks = [
            RiskAlert("Hidden Hardcode", "High", "Sheet1", "A1", "Test", {})
            for _ in range(50)  # 50 high risks = -250 points
        ]
        
        score = self.analyzer._calculate_health_score(risks)
        
        print(f"\n✓ 50 High Risks")
        print(f"✓ Score: {score}/100")
        
        # Should be 20 (floor), not 0
        assert score == 20, "Score should have floor of 20"
        print("✓ Psychological safety: Score floored at 20")
    
    def test_diminishing_returns_for_high_risks(self):
        """Test that high risks have diminishing returns after 10"""
        # 10 high risks
        risks_10 = [
            RiskAlert("Hidden Hardcode", "High", "Sheet1", f"A{i}", "Test", {})
            for i in range(10)
        ]
        score_10 = self.analyzer._calculate_health_score(risks_10)
        
        # 20 high risks
        risks_20 = [
            RiskAlert("Hidden Hardcode", "High", "Sheet1", f"A{i}", "Test", {})
            for i in range(20)
        ]
        score_20 = self.analyzer._calculate_health_score(risks_20)
        
        print(f"\n✓ 10 High Risks: Score = {score_10}")
        print(f"✓ 20 High Risks: Score = {score_20}")
        
        # First 10: -5 each = -50
        # Next 10: -2 each = -20
        # Total: -70
        expected_20 = 100 - 70
        
        assert score_10 == 50, "10 high risks should be 50"
        assert score_20 == 30, "20 high risks should be 30 (diminishing returns)"
        
        print("✓ Diminishing returns working correctly")
    
    def test_real_world_scenario(self):
        """Test with real-world scenario: 34 high risks"""
        # Simulate UAT scenario: 34 high risks
        risks = [
            RiskAlert("Hidden Hardcode", "High", "Sheet1", f"A{i}", "Test", {})
            for i in range(34)
        ]
        
        score = self.analyzer._calculate_health_score(risks)
        
        print(f"\n✓ Real-World Scenario: 34 High Risks")
        print(f"✓ Old Formula: Would be 0 (100 - 34*5 = -70)")
        print(f"✓ New Formula: {score}/100")
        
        # First 10: -50
        # Next 24: -48
        # Total: -98
        # Result: max(20, 100-98) = 20
        
        assert score == 20, "34 high risks should result in score of 20"
        print("✓ User sees '20/100' not '0/100' - Psychological safety achieved")
    
    def test_mixed_severity(self):
        """Test with mixed severity risks"""
        risks = [
            RiskAlert("Circular Ref", "Critical", "Sheet1", "A1", "Test", {}),
            RiskAlert("Circular Ref", "Critical", "Sheet1", "A2", "Test", {})
        ] + [
            RiskAlert("Hidden Hardcode", "High", "Sheet1", f"B{i}", "Test", {})
            for i in range(15)
        ] + [
            RiskAlert("Merged Cell", "Medium", "Sheet1", f"C{i}", "Test", {})
            for i in range(10)
        ]
        
        score = self.analyzer._calculate_health_score(risks)
        
        print(f"\n✓ Mixed Severity:")
        print(f"  - 2 Critical: -20")
        print(f"  - 15 High: -60 (10*5 + 5*2)")
        print(f"  - 10 Medium: -20")
        print(f"  - Total: -100")
        print(f"✓ Score: {score}/100 (floored at 20)")
        
        assert score == 20, "Mixed severity should floor at 20"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
