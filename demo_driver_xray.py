"""
Demo: Driver X-Ray Feature

This script demonstrates the Driver X-Ray functionality without running the full Streamlit app.
"""

import networkx as nx
from src.models import ModelAnalysis, CellInfo, RiskAlert
from src.analyzer import ModelAnalyzer


def create_demo_model():
    """Create a demo model with realistic dependencies"""
    
    # Create dependency graph
    # F4: Exchange Rate (driver)
    # F10: Unit Price = F4 * 1000 (hardcoded multiplier)
    # F20: Revenue = F10 * 100 (hardcoded quantity)
    # F30: Net Income = F20 - 50000 (hardcoded costs)
    
    graph = nx.DiGraph()
    graph.add_edge("Sheet1!F4", "Sheet1!F10")
    graph.add_edge("Sheet1!F10", "Sheet1!F20")
    graph.add_edge("Sheet1!F20", "Sheet1!F30")
    
    # Create cells
    cells = {
        "Sheet1!F4": CellInfo(
            sheet="Sheet1",
            address="F4",
            value=201.26,
            formula=None
        ),
        "Sheet1!F10": CellInfo(
            sheet="Sheet1",
            address="F10",
            value=201260,
            formula="=F4*1000"
        ),
        "Sheet1!F20": CellInfo(
            sheet="Sheet1",
            address="F20",
            value=20126000,
            formula="=F10*100"
        ),
        "Sheet1!F30": CellInfo(
            sheet="Sheet1",
            address="F30",
            value=20076000,
            formula="=F20-50000"
        )
    }
    
    # Create risks
    risks = [
        RiskAlert(
            risk_type="Hidden Hardcode",
            severity="High",
            sheet="Sheet1",
            cell="F10",
            description="Formula contains hardcoded value: 1000",
            row_label="Unit Price",
            col_label="2024-01"
        ),
        RiskAlert(
            risk_type="Hidden Hardcode",
            severity="High",
            sheet="Sheet1",
            cell="F20",
            description="Formula contains hardcoded value: 100",
            row_label="Revenue",
            col_label="2024-01"
        ),
        RiskAlert(
            risk_type="Hidden Hardcode",
            severity="High",
            sheet="Sheet1",
            cell="F30",
            description="Formula contains hardcoded value: 50000",
            row_label="Net Income",
            col_label="2024-01"
        )
    ]
    
    # Create model
    model = ModelAnalysis(
        filename="demo.xlsx",
        sheets=["Sheet1"],
        cells=cells,
        risks=risks,
        health_score=60,
        dependency_graph=graph
    )
    
    return model


def demo_driver_xray():
    """Demonstrate Driver X-Ray functionality"""
    
    print("=" * 70)
    print("DRIVER X-RAY DEMO")
    print("=" * 70)
    print()
    
    # Create demo model
    model = create_demo_model()
    
    print(f"📊 Model: {model.filename}")
    print(f"🛡️ Health Score: {model.health_score}/100")
    print(f"⚠️ Risks Detected: {len(model.risks)}")
    print()
    
    # Demo 1: Trace F10 (Unit Price with hardcoded multiplier)
    print("=" * 70)
    print("DEMO 1: Tracing F10 (Unit Price)")
    print("=" * 70)
    print()
    
    cell_address = "Sheet1!F10"
    risk = next((r for r in model.risks if r.get_location() == cell_address), None)
    
    print(f"📍 Selected Cell: {cell_address}")
    print(f"   Context: {risk.get_context()}")
    print(f"   Risk: {risk.risk_type} ({risk.severity})")
    print(f"   Formula: {model.cells[cell_address].formula}")
    print(f"   Value: {model.cells[cell_address].value}")
    print()
    
    # Get drivers
    drivers = model.get_precedents(cell_address)
    print("⬆️ DRIVERS (Precedents):")
    if drivers:
        for driver in drivers:
            driver_cell = model.cells.get(driver)
            print(f"   - {driver}: {driver_cell.value}")
    else:
        print("   No drivers found")
    print()
    
    # Get impacts
    impacts = model.get_dependents(cell_address)
    print("⬇️ IMPACTS (Dependents):")
    if impacts:
        for impact in impacts:
            impact_cell = model.cells.get(impact)
            print(f"   - {impact}: {impact_cell.value}")
    else:
        print("   No impacts found")
    print()
    
    # Insights
    print("💡 INSIGHTS:")
    if drivers and len(drivers) == 1:
        print("   ✅ Simple Dependency: Easy to trace")
    if impacts and len(impacts) > 0:
        print(f"   ⚠️ Impact: Changes will affect {len(impacts)} cell(s)")
    print()
    
    # Demo 2: Trace F4 (Root Driver)
    print("=" * 70)
    print("DEMO 2: Tracing F4 (Exchange Rate - Root Driver)")
    print("=" * 70)
    print()
    
    cell_address = "Sheet1!F4"
    cell = model.cells[cell_address]
    
    print(f"📍 Selected Cell: {cell_address}")
    print(f"   Value: {cell.value}")
    print(f"   Formula: {cell.formula or 'None (input cell)'}")
    print()
    
    # Get drivers
    drivers = model.get_precedents(cell_address)
    print("⬆️ DRIVERS (Precedents):")
    if drivers:
        for driver in drivers:
            print(f"   - {driver}")
    else:
        print("   No drivers found (this is a root driver)")
    print()
    
    # Get impacts
    impacts = model.get_dependents(cell_address)
    print("⬇️ IMPACTS (Dependents):")
    if impacts:
        for impact in impacts:
            impact_cell = model.cells.get(impact)
            print(f"   - {impact}: {impact_cell.value}")
    else:
        print("   No impacts found")
    print()
    
    # Insights
    print("💡 INSIGHTS:")
    if not drivers and not cell.formula:
        print("   ✅ Root Driver: This is an input cell")
    if impacts and len(impacts) > 0:
        print(f"   ⚠️ High Impact: This drives {len(impacts)} cell(s)")
    print()
    
    # Demo 3: Trace F30 (Net Income - End of Chain)
    print("=" * 70)
    print("DEMO 3: Tracing F30 (Net Income - End of Chain)")
    print("=" * 70)
    print()
    
    cell_address = "Sheet1!F30"
    risk = next((r for r in model.risks if r.get_location() == cell_address), None)
    
    print(f"📍 Selected Cell: {cell_address}")
    print(f"   Context: {risk.get_context()}")
    print(f"   Formula: {model.cells[cell_address].formula}")
    print(f"   Value: {model.cells[cell_address].value}")
    print()
    
    # Get drivers
    drivers = model.get_precedents(cell_address)
    print("⬆️ DRIVERS (Precedents):")
    if drivers:
        for driver in drivers:
            driver_cell = model.cells.get(driver)
            print(f"   - {driver}: {driver_cell.value}")
    else:
        print("   No drivers found")
    print()
    
    # Get impacts
    impacts = model.get_dependents(cell_address)
    print("⬇️ IMPACTS (Dependents):")
    if impacts:
        for impact in impacts:
            print(f"   - {impact}")
    else:
        print("   No impacts found (this is an output cell)")
    print()
    
    # Insights
    print("💡 INSIGHTS:")
    if not impacts:
        print("   ℹ️ Output Cell: No other cells depend on this")
    if drivers and len(drivers) == 1:
        print("   ✅ Simple Dependency: Easy to trace")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Dependency Chain:")
    print("  F4 (Exchange Rate)")
    print("   ↓")
    print("  F10 (Unit Price) = F4 * 1000 [HARDCODED]")
    print("   ↓")
    print("  F20 (Revenue) = F10 * 100 [HARDCODED]")
    print("   ↓")
    print("  F30 (Net Income) = F20 - 50000 [HARDCODED]")
    print()
    print("Action Items:")
    print("  1. Extract hardcoded multiplier (1000) to a driver cell")
    print("  2. Extract hardcoded quantity (100) to a driver cell")
    print("  3. Extract hardcoded costs (50000) to a driver cell")
    print()
    print("✅ Driver X-Ray makes these dependencies visible!")
    print()


if __name__ == "__main__":
    demo_driver_xray()
