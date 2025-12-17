"""
Unit tests for Causal Tree Builder
"""

import pytest
import networkx as nx
from src.models import ModelAnalysis, CellInfo
from src.explanation_models import Factor
from src.causal_tree_builder import CausalTreeBuilder


def create_test_model_with_tree():
    """Create a test model with a simple causal tree"""
    cells = {
        # Labels
        'Sheet1!A10': CellInfo(sheet='Sheet1', address='A10', value='売上'),
        'Sheet1!A11': CellInfo(sheet='Sheet1', address='A11', value='単価'),
        'Sheet1!A12': CellInfo(sheet='Sheet1', address='A12', value='数量'),
        
        # Values and formulas
        'Sheet1!H10': CellInfo(
            sheet='Sheet1',
            address='H10',
            value=12000,
            formula='=H11*H12',
            dependencies=['Sheet1!H11', 'Sheet1!H12']
        ),
        'Sheet1!H11': CellInfo(
            sheet='Sheet1',
            address='H11',
            value=100,
            formula=None
        ),
        'Sheet1!H12': CellInfo(
            sheet='Sheet1',
            address='H12',
            value=120,
            formula=None
        ),
    }
    
    # Build dependency graph
    graph = nx.DiGraph()
    graph.add_edge('Sheet1!H11', 'Sheet1!H10')
    graph.add_edge('Sheet1!H12', 'Sheet1!H10')
    
    return ModelAnalysis(
        filename='test.xlsx',
        sheets=['Sheet1'],
        cells=cells,
        risks=[],
        health_score=100,
        dependency_graph=graph
    )


def test_basic_tree_construction():
    """Test basic tree construction"""
    model = create_test_model_with_tree()
    
    # Create factors
    factors = [
        Factor(
            id='Sheet1!H11',
            sheet='Sheet1',
            address='H11',
            label='単価',
            factor_type='scalar'
        ),
        Factor(
            id='Sheet1!H12',
            sheet='Sheet1',
            address='H12',
            label='数量',
            factor_type='scalar'
        ),
    ]
    
    builder = CausalTreeBuilder()
    tree = builder.build_causal_tree('Sheet1!H10', model, factors, max_depth=1)
    
    # Check root node
    assert tree.id == 'Sheet1!H10'
    assert tree.label == '売上'
    assert tree.depth == 0
    assert not tree.is_factor
    
    # Check children
    assert len(tree.children) == 2
    child_ids = [c.id for c in tree.children]
    assert 'Sheet1!H11' in child_ids
    assert 'Sheet1!H12' in child_ids
    
    # Check that children are factors
    for child in tree.children:
        assert child.is_factor
        assert child.depth == 1


def test_kpi_candidate_detection():
    """Test KPI candidate detection"""
    cells = {
        'Sheet1!A10': CellInfo(sheet='Sheet1', address='A10', value='売上'),
        'Sheet1!A11': CellInfo(sheet='Sheet1', address='A11', value='Revenue'),
        'Sheet1!A12': CellInfo(sheet='Sheet1', address='A12', value='Cost'),
        
        'Sheet1!H10': CellInfo(
            sheet='Sheet1',
            address='H10',
            value=12000,
            formula='=H11*H12',
            dependencies=['Sheet1!H11', 'Sheet1!H12']
        ),
        'Sheet1!H11': CellInfo(
            sheet='Sheet1',
            address='H11',
            value=10000,
            formula='=H12-H13',
            dependencies=['Sheet1!H12', 'Sheet1!H13']
        ),
        'Sheet1!H12': CellInfo(
            sheet='Sheet1',
            address='H12',
            value=5000,
            formula='=H13*2',
            dependencies=['Sheet1!H13']
        ),
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
    
    builder = CausalTreeBuilder()
    candidates = builder.get_kpi_candidates(model, [])
    
    # Should find H10 (売上) and H11 (Revenue)
    candidate_ids = [c['id'] for c in candidates]
    assert 'Sheet1!H10' in candidate_ids
    assert 'Sheet1!H11' in candidate_ids
    
    # Should NOT find H12 (Cost - no revenue keyword)
    assert 'Sheet1!H12' not in candidate_ids


def test_untraceable_detection():
    """Test untraceable node detection"""
    cells = {
        'Sheet1!H10': CellInfo(
            sheet='Sheet1',
            address='H10',
            value='#REF!',
            formula='=H11+H12',
            dependencies=[]
        ),
        'Sheet1!H11': CellInfo(
            sheet='Sheet1',
            address='H11',
            value=100,
            formula='=INDIRECT("A1")',
            dependencies=[],
            is_dynamic=True
        ),
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
    
    builder = CausalTreeBuilder()
    
    # H10 should be untraceable (formula error)
    assert builder._is_untraceable(cells['Sheet1!H10'], model)
    reason = builder._get_untraceable_reason(cells['Sheet1!H10'], model)
    assert '#REF!' in reason
    
    # H11 should be untraceable (dynamic reference)
    assert builder._is_untraceable(cells['Sheet1!H11'], model)
    reason = builder._get_untraceable_reason(cells['Sheet1!H11'], model)
    assert 'Dynamic' in reason or 'INDIRECT' in reason


def test_depth_control():
    """Test depth control in tree construction"""
    model = create_test_model_with_tree()
    factors = []
    
    builder = CausalTreeBuilder()
    
    # Build with depth 0 (only root)
    tree_depth0 = builder.build_causal_tree('Sheet1!H10', model, factors, max_depth=0)
    assert len(tree_depth0.children) == 0
    
    # Build with depth 1 (root + children)
    tree_depth1 = builder.build_causal_tree('Sheet1!H10', model, factors, max_depth=1)
    assert len(tree_depth1.children) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
