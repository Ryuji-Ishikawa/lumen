"""
Test: Driver X-Ray Feature (Phase 6)

Verify that the Driver X-Ray feature correctly traces dependencies.
"""

import networkx as nx
from src.models import ModelAnalysis, CellInfo, RiskAlert


def test_driver_xray_basic():
    """Test basic driver and impact tracing"""
    
    # Create a simple dependency graph
    # F4 (Driver: Exchange Rate = 201.26)
    # F24 (Calculation) = F4 * 1000
    # F30 (Net Income) depends on F24
    
    graph = nx.DiGraph()
    graph.add_edge("Sheet1!F4", "Sheet1!F24")  # F24 depends on F4
    graph.add_edge("Sheet1!F24", "Sheet1!F30")  # F30 depends on F24
    
    # Create cells
    cells = {
        "Sheet1!F4": CellInfo(
            sheet="Sheet1",
            address="F4",
            value=201.26,
            formula=None
        ),
        "Sheet1!F24": CellInfo(
            sheet="Sheet1",
            address="F24",
            value=201260,
            formula="=F4*1000"
        ),
        "Sheet1!F30": CellInfo(
            sheet="Sheet1",
            address="F30",
            value=201260,
            formula="=F24"
        )
    }
    
    # Create model
    model = ModelAnalysis(
        filename="test.xlsx",
        sheets=["Sheet1"],
        cells=cells,
        risks=[],
        health_score=100,
        dependency_graph=graph
    )
    
    # Test 1: Get drivers of F24
    drivers = model.get_precedents("Sheet1!F24")
    print(f"Test 1: Drivers of F24: {drivers}")
    assert "Sheet1!F4" in drivers, "F24 should depend on F4"
    assert len(drivers) == 1, "F24 should have exactly 1 driver"
    
    # Test 2: Get impacts of F24
    impacts = model.get_dependents("Sheet1!F24")
    print(f"Test 2: Impacts of F24: {impacts}")
    assert "Sheet1!F30" in impacts, "F24 should impact F30"
    assert len(impacts) == 1, "F24 should have exactly 1 impact"
    
    # Test 3: Get drivers of F4 (root driver)
    drivers_f4 = model.get_precedents("Sheet1!F4")
    print(f"Test 3: Drivers of F4: {drivers_f4}")
    assert len(drivers_f4) == 0, "F4 should have no drivers (it's a root)"
    
    # Test 4: Get impacts of F4
    impacts_f4 = model.get_dependents("Sheet1!F4")
    print(f"Test 4: Impacts of F4: {impacts_f4}")
    assert "Sheet1!F24" in impacts_f4, "F4 should impact F24"
    
    print("\n✅ All Driver X-Ray tests passed!")


def test_driver_xray_with_risks():
    """Test Driver X-Ray with actual risks"""
    
    # Create a graph with a hardcoded value
    graph = nx.DiGraph()
    graph.add_edge("Sheet1!F4", "Sheet1!F24")
    
    cells = {
        "Sheet1!F4": CellInfo(
            sheet="Sheet1",
            address="F4",
            value=201.26,
            formula=None
        ),
        "Sheet1!F24": CellInfo(
            sheet="Sheet1",
            address="F24",
            value=201260,
            formula="=F4*1000"
        )
    }
    
    # Create a risk for F24
    risk = RiskAlert(
        risk_type="Hidden Hardcode",
        severity="High",
        sheet="Sheet1",
        cell="F24",
        description="Formula contains hardcoded value: 1000",
        row_label="Total Cost",
        col_label="2024-01"
    )
    
    model = ModelAnalysis(
        filename="test.xlsx",
        sheets=["Sheet1"],
        cells=cells,
        risks=[risk],
        health_score=80,
        dependency_graph=graph
    )
    
    # Test: Trace the risk back to its driver
    drivers = model.get_precedents("Sheet1!F24")
    print(f"\nRisk at F24 has drivers: {drivers}")
    assert len(drivers) == 1, "Should find the driver F4"
    
    # Get the driver cell
    driver_cell = model.cells.get(drivers[0])
    print(f"Driver cell F4 value: {driver_cell.value}")
    assert driver_cell.value == 201.26, "Should get the driver value"
    
    print("\n✅ Risk tracing test passed!")


if __name__ == "__main__":
    test_driver_xray_basic()
    test_driver_xray_with_risks()
