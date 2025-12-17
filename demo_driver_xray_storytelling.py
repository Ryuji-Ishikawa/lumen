"""
Demo: Driver X-Ray Storytelling Update

This script demonstrates the enhanced storytelling features.
"""

import networkx as nx
from src.models import ModelAnalysis, CellInfo, RiskAlert


def create_storytelling_demo():
    """Create a demo model that showcases storytelling features"""
    
    # Create dependency graph with a clear villain and victims
    # F4: Exchange Rate (HARDCODED - THE VILLAIN)
    # F10: Unit Price = F4 * 1000
    # F20: Revenue = F10 * Quantity
    # F30: Net Income = F20 - Costs (CRITICAL KPI - THE VICTIM)
    # F35: Cash Flow = F30 + Adjustments (CRITICAL KPI - THE VICTIM)
    
    graph = nx.DiGraph()
    graph.add_edge("Sheet1!F4", "Sheet1!F10")
    graph.add_edge("Sheet1!F10", "Sheet1!F20")
    graph.add_edge("Sheet1!F20", "Sheet1!F30")
    graph.add_edge("Sheet1!F30", "Sheet1!F35")
    
    # Create cells
    cells = {
        "Sheet1!F4": CellInfo(
            sheet="Sheet1",
            address="F4",
            value=201.26,
            formula="=201.26"  # Hardcoded!
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
        ),
        "Sheet1!F35": CellInfo(
            sheet="Sheet1",
            address="F35",
            value=20076000,
            formula="=F30"
        )
    }
    
    # Create risks - F4 is the villain
    risks = [
        RiskAlert(
            risk_type="Hidden Hardcode",
            severity="High",
            sheet="Sheet1",
            cell="F4",
            description="Formula contains hardcoded value: 201.26",
            row_label="Exchange Rate",
            col_label="2024-01"
        ),
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
            row_label="Net Income",  # KPI keyword!
            col_label="2024-01"
        )
    ]
    
    # Create model
    model = ModelAnalysis(
        filename="storytelling_demo.xlsx",
        sheets=["Sheet1"],
        cells=cells,
        risks=risks,
        health_score=50,
        dependency_graph=graph
    )
    
    return model


def demo_storytelling():
    """Demonstrate storytelling features"""
    
    print("=" * 80)
    print("DRIVER X-RAY: STORYTELLING UPDATE DEMO")
    print("=" * 80)
    print()
    
    model = create_storytelling_demo()
    
    print("📊 Scenario: Analyzing F10 (Unit Price)")
    print()
    
    # Analyze F10
    cell_address = "Sheet1!F10"
    drivers = model.get_precedents(cell_address)
    impacts = model.get_dependents(cell_address)
    
    # Find root causes
    root_causes = []
    for driver in drivers:
        driver_risk = next((r for r in model.risks if r.get_location() == driver), None)
        if driver_risk and driver_risk.risk_type == "Hidden Hardcode":
            root_causes.append((driver, driver_risk.row_label))
    
    # Find critical impacts
    kpi_keywords = ["profit", "income", "cash", "sales", "revenue"]
    critical_impacts = []
    for impact in impacts:
        impact_risk = next((r for r in model.risks if r.get_location() == impact), None)
        if impact_risk and impact_risk.row_label:
            label_lower = impact_risk.row_label.lower()
            if any(kw in label_lower for kw in kpi_keywords):
                critical_impacts.append((impact, impact_risk.row_label))
    
    # STORYTELLING: Natural Language Summary
    print("📖 ANALYSIS SUMMARY")
    print("-" * 80)
    
    if len(drivers) == 1:
        print(f"This cell depends on {len(drivers)} driver.")
    else:
        print(f"This cell depends on {len(drivers)} drivers.")
    
    if root_causes:
        root_str = ", ".join([f"{addr} ({label})" for addr, label in root_causes])
        print(f"🚨 ROOT CAUSE DETECTED: {root_str} contains hardcoded values.")
    
    if critical_impacts:
        impact_str = ", ".join([label for _, label in critical_impacts])
        print(f"⚠️ CRITICAL IMPACT: Changes will affect {impact_str}.")
    elif len(impacts) > 5:
        print(f"⚠️ Changes will cascade to {len(impacts)} cells.")
    else:
        print(f"Changes will affect {len(impacts)} cell(s).")
    
    print()
    print()
    
    # SOURCE (with villain highlighting)
    print("⬆️ SOURCE (Where the value comes from)")
    print("-" * 80)
    
    if drivers:
        for driver in drivers:
            driver_cell = model.cells.get(driver)
            driver_risk = next((r for r in model.risks if r.get_location() == driver), None)
            
            if driver_risk and driver_risk.risk_type == "Hidden Hardcode":
                print(f"🚨 {driver}: {driver_risk.row_label} = {driver_cell.value} ← ROOT CAUSE (RED)")
            else:
                print(f"   {driver}: {driver_cell.value}")
    else:
        print("🚨 No sources found - This cell likely contains hardcoded values")
    
    print()
    print()
    
    # CONSEQUENCES (with victim highlighting)
    print("⬇️ CONSEQUENCES (What this affects)")
    print("-" * 80)
    
    if impacts:
        for impact in impacts:
            impact_cell = model.cells.get(impact)
            impact_risk = next((r for r in model.risks if r.get_location() == impact), None)
            
            is_kpi = False
            if impact_risk and impact_risk.row_label:
                label_lower = impact_risk.row_label.lower()
                is_kpi = any(kw in label_lower for kw in kpi_keywords)
            
            if is_kpi:
                label = impact_risk.row_label if impact_risk else impact
                print(f"⚠️ {impact}: {label} = {impact_cell.value} ← CRITICAL KPI (BOLD)")
            else:
                label = impact_risk.row_label if impact_risk else impact
                print(f"   {impact}: {label} = {impact_cell.value}")
    else:
        print("   No consequences (this is an output cell)")
    
    print()
    print()
    
    # WHAT TO DO
    print("💡 WHAT TO DO")
    print("-" * 80)
    
    if root_causes:
        print(f"🚨 Fix the root cause first: {len(root_causes)} driver(s) contain hardcoded values.")
        print("   Action: Extract them to input cells.")
    
    if critical_impacts:
        print(f"⚠️ High priority: This affects {len(critical_impacts)} critical KPI(s).")
        print("   Action: Test changes carefully.")
    elif len(impacts) > 10:
        print(f"⚠️ Wide impact: Changes will cascade to {len(impacts)} cells.")
        print("   Action: Review all impacts before modifying.")
    
    if len(drivers) == 1 and len(impacts) <= 3:
        print("✅ Low complexity: Simple dependency chain.")
        print("   Action: Safe to modify with proper testing.")
    
    print()
    print()
    
    # COMPARISON
    print("=" * 80)
    print("BEFORE vs AFTER")
    print("=" * 80)
    print()
    
    print("BEFORE (Database Dump):")
    print("  - F4: Exchange Rate = 201.26")
    print("  - F20: Revenue = 20126000")
    print("  - F30: Net Income = 20076000")
    print()
    
    print("AFTER (Storytelling):")
    print("  🚨 F4: Exchange Rate = 201.26 ← ROOT CAUSE (RED)")
    print("     F20: Revenue = 20126000")
    print("  ⚠️ F30: Net Income = 20076000 ← CRITICAL KPI (BOLD)")
    print()
    
    print("✅ The villain (F4) and victims (F30) are now obvious!")
    print()


if __name__ == "__main__":
    demo_storytelling()
