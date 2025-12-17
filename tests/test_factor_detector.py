"""
Unit tests for Factor Detector
"""

import pytest
import networkx as nx
from src.models import ModelAnalysis, CellInfo
from src.factor_detector import FactorDetector


def create_test_model():
    """Create a simple test model"""
    cells = {
        'Sheet1!A10': CellInfo(
            sheet='Sheet1',
            address='A10',
            value='売上',
            formula=None
        ),
        'Sheet1!B10': CellInfo(
            sheet='Sheet1',
            address='B10',
            value=1000,
            formula=None,
            dependencies=[]
        ),
        'Sheet1!C10': CellInfo(
            sheet='Sheet1',
            address='C10',
            value=1200,
            formula='=B10*1.2',
            dependencies=['Sheet1!B10']
        ),
        'Sheet1!D10': CellInfo(
            sheet='Sheet1',
            address='D10',
            value=1000,
            formula='=Sheet1!B10',  # Simple reference
            dependencies=['Sheet1!B10']
        ),
    }
    
    # Build dependency graph
    graph = nx.DiGraph()
    graph.add_edge('Sheet1!B10', 'Sheet1!C10')
    graph.add_edge('Sheet1!B10', 'Sheet1!D10')
    
    return ModelAnalysis(
        filename='test.xlsx',
        sheets=['Sheet1'],
        cells=cells,
        risks=[],
        health_score=100,
        dependency_graph=graph
    )


def test_factor_detection_basic():
    """Test basic factor detection"""
    model = create_test_model()
    detector = FactorDetector()
    
    factors = detector.detect_factors(model)
    
    # B10 should be detected as a factor (no formula, has label, has dependents)
    factor_ids = [f.id for f in factors]
    assert 'Sheet1!B10' in factor_ids
    
    # C10 should NOT be a factor (has complex formula)
    assert 'Sheet1!C10' not in factor_ids


def test_simple_reference_detection():
    """Test simple reference detection"""
    detector = FactorDetector()
    
    # Simple references
    assert detector._is_simple_reference('=A10')
    assert detector._is_simple_reference('=Sheet1!A10')
    assert detector._is_simple_reference("='Sheet Name'!A10")
    
    # Complex formulas (not simple references)
    assert not detector._is_simple_reference('=A10+B10')
    assert not detector._is_simple_reference('=SUM(A10:A20)')
    assert not detector._is_simple_reference('=A10*1.2')


def test_label_validation():
    """Test label quality validation"""
    detector = FactorDetector()
    
    # Valid labels
    assert detector._is_valid_label('売上')
    assert detector._is_valid_label('Revenue')
    assert detector._is_valid_label('Unit Price')
    
    # Invalid labels
    assert not detector._is_valid_label('=A10')  # Formula
    assert not detector._is_valid_label('A10')  # Cell address
    assert not detector._is_valid_label('123')  # Pure number
    assert not detector._is_valid_label('X')  # Too short


def test_factor_type_detection():
    """Test scalar vs series detection"""
    # Create model with series data
    cells = {
        'Sheet1!H10': CellInfo(sheet='Sheet1', address='H10', value=100),
        'Sheet1!I10': CellInfo(sheet='Sheet1', address='I10', value=110),
        'Sheet1!J10': CellInfo(sheet='Sheet1', address='J10', value=120),
        'Sheet1!K10': CellInfo(sheet='Sheet1', address='K10', value=130),
    }
    
    graph = nx.DiGraph()
    model = ModelAnalysis(
        filename='test.xlsx',
        sheets=['Sheet1'],
        cells=cells,
        risks=[],
        health_score=100,
        dependency_graph=graph
    )
    
    detector = FactorDetector()
    
    # H10 should be detected as series (has 3+ adjacent cells)
    factor_type = detector._detect_factor_type('Sheet1!H10', cells['Sheet1!H10'], model)
    assert factor_type == 'series'


def test_no_label_rescue():
    """Test rescue measure for cells without labels"""
    cells = {
        'Sheet1!H10': CellInfo(
            sheet='Sheet1',
            address='H10',
            value=1000,
            formula=None,
            dependencies=[]
        ),
        'Sheet1!I10': CellInfo(
            sheet='Sheet1',
            address='I10',
            value=1200,
            formula='=H10*1.2',
            dependencies=['Sheet1!H10']
        ),
    }
    
    graph = nx.DiGraph()
    graph.add_edge('Sheet1!H10', 'Sheet1!I10')
    
    model = ModelAnalysis(
        filename='test.xlsx',
        sheets=['Sheet1'],
        cells=cells,
        risks=[],
        health_score=100,
        dependency_graph=graph
    )
    
    detector = FactorDetector()
    factors = detector.detect_factors(model)
    
    # H10 should be detected with rescue label
    factor = next((f for f in factors if f.id == 'Sheet1!H10'), None)
    assert factor is not None
    assert '[No Label]' in factor.label
    assert 'H10' in factor.label


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
