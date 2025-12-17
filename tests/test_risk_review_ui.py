"""
Test suite for Risk Review System UI Components (Phase 11, Task 35-39)
Tests for:
- Checkbox UI
- Progress Display
- Filter System
- CSV Export
- Integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime

from src.models import RiskAlert, ReviewProgress
from src.risk_review import (
    RiskReviewStateManager, 
    DynamicScoreCalculator,
    format_context,
    export_risks_with_review_state
)


@pytest.fixture
def sample_risks():
    """Create sample risks for testing"""
    return [
        RiskAlert(
            sheet="Sheet1",
            cell="A1", 
            risk_type="Hidden Hardcode",
            severity="Critical",
            description="Critical risk 1",
            row_label="Revenue",
            col_label="Q1"
        ),
        RiskAlert(
            sheet="Sheet1",
            cell="B2",
            risk_type="Circular Reference", 
            severity="High",
            description="High risk 1",
            row_label="Costs",
            col_label="Q2"
        ),
        RiskAlert(
            sheet="Sheet2",
            cell="C3",
            risk_type="Structural Debt",
            severity="Medium", 
            description="Medium risk 1",
            row_label=None,
            col_label="Total"
        )
    ]


class TestFormatContext:
    """Test context formatting utility"""
    
    def test_both_labels(self):
        """Test with both row and column labels"""
        assert format_context("Revenue", "Q1") == "Revenue × Q1"
    
    def test_row_only(self):
        """Test with row label only"""
        assert format_context("Revenue", None) == "Revenue"
    
    def test_col_only(self):
        """Test with column label only"""
        assert format_context(None, "Q1") == "Q1"
    
    def test_no_labels(self):
        """Test with no labels"""
        assert format_context(None, None) == "-"


class TestCSVExport:
    """Test CSV export with review state"""
    
    def test_export_basic(self, sample_risks):
        """Test basic CSV export"""
        with patch('streamlit.session_state', MagicMock(risk_review_states={})):
            manager = RiskReviewStateManager()
            csv_data = export_risks_with_review_state(sample_risks, manager)
            
            # Should be valid CSV
            assert isinstance(csv_data, str)
            assert "確認済み" in csv_data
            assert "エクスポート日時" in csv_data
    
    def test_export_with_reviewed(self, sample_risks):
        """Test CSV export with some risks reviewed"""
        with patch('streamlit.session_state', MagicMock(risk_review_states={})):
            manager = RiskReviewStateManager()
            
            # Mark first risk as reviewed
            manager.set_reviewed(sample_risks[0], True)
            
            csv_data = export_risks_with_review_state(sample_risks, manager)
            
            # Should contain TRUE for reviewed risk
            assert "TRUE" in csv_data
            # Should contain FALSE for unreviewed risks
            assert "FALSE" in csv_data
    
    def test_export_timestamp(self, sample_risks):
        """Test CSV export includes timestamp"""
        with patch('streamlit.session_state', MagicMock(risk_review_states={})):
            manager = RiskReviewStateManager()
            csv_data = export_risks_with_review_state(sample_risks, manager)
            
            # Should contain timestamp column
            assert "エクスポート日時" in csv_data
            
            # Should contain current date
            current_date = datetime.now().strftime("%Y-%m-%d")
            assert current_date in csv_data


class TestReviewProgress:
    """Test ReviewProgress model methods"""
    
    def test_display_text(self):
        """Test display text generation"""
        progress = ReviewProgress(
            total_risks=10,
            reviewed_count=3,
            unreviewed_count=7,
            percentage=30.0,
            initial_score=70,
            current_score=80,
            improvement_delta=10
        )
        assert progress.display_text == "確認済み: 3/10 (30%)"
    
    def test_is_complete(self):
        """Test completion check"""
        complete = ReviewProgress(
            total_risks=5, reviewed_count=5, unreviewed_count=0,
            percentage=100.0, initial_score=70, current_score=100, improvement_delta=30
        )
        assert complete.is_complete()
        
        incomplete = ReviewProgress(
            total_risks=5, reviewed_count=3, unreviewed_count=2,
            percentage=60.0, initial_score=70, current_score=80, improvement_delta=10
        )
        assert not incomplete.is_complete()
    
    def test_is_halfway(self):
        """Test halfway check"""
        halfway = ReviewProgress(
            total_risks=10, reviewed_count=6, unreviewed_count=4,
            percentage=60.0, initial_score=70, current_score=80, improvement_delta=10
        )
        assert halfway.is_halfway()
        
        not_halfway = ReviewProgress(
            total_risks=10, reviewed_count=2, unreviewed_count=8,
            percentage=20.0, initial_score=70, current_score=75, improvement_delta=5
        )
        assert not not_halfway.is_halfway()
    
    def test_encouragement_complete(self):
        """Test encouragement message when complete"""
        complete = ReviewProgress(
            total_risks=5, reviewed_count=5, unreviewed_count=0,
            percentage=100.0, initial_score=70, current_score=100, improvement_delta=30
        )
        message = complete.get_encouragement_message()
        assert message is not None
        assert "🎉" in message
    
    def test_encouragement_halfway(self):
        """Test encouragement message when halfway"""
        halfway = ReviewProgress(
            total_risks=10, reviewed_count=6, unreviewed_count=4,
            percentage=60.0, initial_score=70, current_score=80, improvement_delta=10
        )
        message = halfway.get_encouragement_message()
        assert message is not None
        assert "💪" in message
        assert "4" in message
    
    def test_encouragement_early(self):
        """Test no encouragement message when early"""
        early = ReviewProgress(
            total_risks=10, reviewed_count=2, unreviewed_count=8,
            percentage=20.0, initial_score=70, current_score=75, improvement_delta=5
        )
        message = early.get_encouragement_message()
        assert message is None


class TestIntegration:
    """Test integration scenarios"""
    
    def test_full_workflow(self, sample_risks):
        """Test complete workflow: review -> calculate -> export"""
        with patch('streamlit.session_state', MagicMock(risk_review_states={})):
            manager = RiskReviewStateManager()
            calculator = DynamicScoreCalculator()
            
            # Initial state
            progress = calculator.calculate_progress(sample_risks, manager)
            assert progress.reviewed_count == 0
            assert progress.improvement_delta == 0
            
            # Review first risk (Critical)
            manager.set_reviewed(sample_risks[0], True)
            progress = calculator.calculate_progress(sample_risks, manager)
            assert progress.reviewed_count == 1
            assert progress.improvement_delta == 10  # Critical = 10 points
            
            # Review second risk (High)
            manager.set_reviewed(sample_risks[1], True)
            progress = calculator.calculate_progress(sample_risks, manager)
            assert progress.reviewed_count == 2
            assert progress.improvement_delta == 15  # Critical + High = 10 + 5
            
            # Export with review state
            csv_data = export_risks_with_review_state(sample_risks, manager)
            assert "TRUE" in csv_data  # Reviewed risks
            assert "FALSE" in csv_data  # Unreviewed risk


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
