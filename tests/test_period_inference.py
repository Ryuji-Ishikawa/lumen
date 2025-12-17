"""
Unit tests for Period Inference Engine
"""

import pytest
from datetime import datetime
import networkx as nx
from src.models import ModelAnalysis, CellInfo
from src.period_inference import PeriodInferenceEngine


def create_test_model_with_periods():
    """Create a test model with period data"""
    cells = {
        # Headers
        'Sheet1!H1': CellInfo(sheet='Sheet1', address='H1', value='2024-01 Act'),
        'Sheet1!I1': CellInfo(sheet='Sheet1', address='I1', value='2024-02 Act'),
        'Sheet1!J1': CellInfo(sheet='Sheet1', address='J1', value='2024-03 Est'),
        'Sheet1!K1': CellInfo(sheet='Sheet1', address='K1', value='2024-04 Plan'),
        
        # Data rows (H column = hardcodes, I column = hardcodes, J/K = formulas)
        'Sheet1!H10': CellInfo(sheet='Sheet1', address='H10', value=1000, formula=None),
        'Sheet1!I10': CellInfo(sheet='Sheet1', address='I10', value=1100, formula=None),
        'Sheet1!J10': CellInfo(sheet='Sheet1', address='J10', value=1200, formula='=I10*1.1'),
        'Sheet1!K10': CellInfo(sheet='Sheet1', address='K10', value=1300, formula='=J10*1.1'),
        
        'Sheet1!H11': CellInfo(sheet='Sheet1', address='H11', value=2000, formula=None),
        'Sheet1!I11': CellInfo(sheet='Sheet1', address='I11', value=2100, formula=None),
        'Sheet1!J11': CellInfo(sheet='Sheet1', address='J11', value=2200, formula='=I11*1.1'),
        'Sheet1!K11': CellInfo(sheet='Sheet1', address='K11', value=2300, formula='=J11*1.1'),
    }
    
    graph = nx.DiGraph()
    
    return ModelAnalysis(
        filename='test.xlsx',
        sheets=['Sheet1'],
        cells=cells,
        risks=[],
        health_score=100,
        dependency_graph=graph
    )


def test_header_keyword_detection():
    """Test Priority 1: Header keyword detection"""
    engine = PeriodInferenceEngine()
    
    # ACTUAL keywords
    assert engine._check_header_keywords('2024-01 Act') == 'ACTUAL'
    assert engine._check_header_keywords('Actual 2024') == 'ACTUAL'
    assert engine._check_header_keywords('実績') == 'ACTUAL'
    
    # FORECAST keywords
    assert engine._check_header_keywords('2024-03 Est') == 'FORECAST'
    assert engine._check_header_keywords('Plan 2024') == 'FORECAST'
    assert engine._check_header_keywords('予測') == 'FORECAST'
    
    # No keywords
    assert engine._check_header_keywords('2024-01') is None
    assert engine._check_header_keywords('January') is None


def test_column_majority_vote():
    """Test Priority 2: Column majority vote"""
    model = create_test_model_with_periods()
    engine = PeriodInferenceEngine()
    
    # Column H (index 7): Majority hardcodes → ACTUAL
    result_h = engine._column_majority_vote(7, model)
    assert result_h is not None
    assert result_h['period_type'] == 'ACTUAL'
    assert result_h['hardcode_count'] > result_h['formula_count']
    
    # Column J (index 9): Majority formulas → FORECAST
    result_j = engine._column_majority_vote(9, model)
    assert result_j is not None
    assert result_j['period_type'] == 'FORECAST'
    assert result_j['formula_count'] > result_j['hardcode_count']


def test_date_parsing():
    """Test date parsing from headers"""
    engine = PeriodInferenceEngine()
    
    # YYYY-MM format
    date1 = engine._parse_date_from_header('2024-01')
    assert date1 == datetime(2024, 1, 1)
    
    # MM-YYYY format
    date2 = engine._parse_date_from_header('01-2024')
    assert date2 == datetime(2024, 1, 1)
    
    # Month name format
    date3 = engine._parse_date_from_header('Jan 2024')
    assert date3 == datetime(2024, 1, 1)
    
    date4 = engine._parse_date_from_header('January 2024')
    assert date4 == datetime(2024, 1, 1)
    
    # FY format
    date5 = engine._parse_date_from_header('FY2024')
    assert date5 == datetime(2024, 4, 1)
    
    # Quarter format
    date6 = engine._parse_date_from_header('Q1 2024')
    assert date6 == datetime(2024, 1, 1)
    
    date7 = engine._parse_date_from_header('Q2-2024')
    assert date7 == datetime(2024, 4, 1)
    
    # Invalid format
    date8 = engine._parse_date_from_header('Invalid')
    assert date8 is None


def test_date_fallback():
    """Test Priority 3: Date fallback"""
    engine = PeriodInferenceEngine()
    
    # Old date (> 3 months ago) → ACTUAL
    old_date = '2020-01'
    result = engine._date_fallback(old_date)
    assert result == 'ACTUAL'
    
    # Recent date → None (uncertain)
    from datetime import datetime, timedelta
    recent_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')
    result = engine._date_fallback(recent_month)
    assert result is None


def test_full_inference_priority():
    """Test full inference with priority system"""
    model = create_test_model_with_periods()
    engine = PeriodInferenceEngine()
    
    period_attrs = engine.infer_period_attributes(model)
    
    # Column H (index 7): Should be ACTUAL (keyword in header)
    assert 7 in period_attrs
    assert period_attrs[7].period_type == 'ACTUAL'
    assert period_attrs[7].confidence == 'HIGH'
    assert period_attrs[7].inference_method == 'header_keyword'
    
    # Column J (index 9): Should be FORECAST (keyword in header)
    assert 9 in period_attrs
    assert period_attrs[9].period_type == 'FORECAST'
    assert period_attrs[9].confidence == 'HIGH'
    assert period_attrs[9].inference_method == 'header_keyword'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
