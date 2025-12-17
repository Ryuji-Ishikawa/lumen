"""
Debug script to investigate G6, G7 impact issue
"""

from pathlib import Path
from src.parser import parse_excel_file
from src.analyzer import ModelAnalyzer
import networkx as nx

def main():
    # Load the sample file
    sample_file = Path("Sample_Business Plan.xlsx")
    
    if not sample_file.exists():
        print(f"❌ File not found: {sample_file}")
        return
    
    print(f"📂 Loading {sample_file}...")
    
    # Read file
    with open(sample_file, 'rb') as f:
        file_bytes = f.read()
    
    # Parse
    print("🔄 Parsing Excel file...")
    model = parse_excel_file(file_bytes, sample_file.name)
    
    # Analyze
    print("🔍 Analyzing risks...")
    analyzer = ModelAnalyzer()
    model = analyzer.analyze(model, fiscal_start_month=1, allowed_constants=[])
    
    # Find the risk for G6, G7
    target_risk = None
    for risk in model.risks:
        if ("G6" in risk.cell or "G7" in risk.cell) and "プロジェクション円" in risk.sheet:
            target_risk = risk
            print(f"  Found candidate: {risk.sheet}!{risk.cell}")
            break
    
    if not target_risk:
        print("❌ Risk not found for プロジェクション円!G6, G7")
        print(f"\n📋 Total risks: {len(model.risks)}")
        print("\n📋 First 20 risks:")
        for i, risk in enumerate(model.risks[:20], 1):
            impact = risk.details.get('impact_count', 0)
            value = risk.details.get("value") or risk.details.get("cell_value") or risk.details.get("hardcoded_value") or risk.details.get("formula", "")
            value_str = str(value)[:30] if value else 'EMPTY'
            print(f"  {i}. {risk.sheet}!{risk.cell} (Impact: {impact}, Value: {value_str})")
        return
    
    print(f"\n✅ Found risk:")
    print(f"  Location: {target_risk.sheet}!{target_risk.cell}")
    print(f"  Context: {target_risk.get_context()}")
    print(f"  Impact: {target_risk.details.get('impact_count', 0)}")
    print(f"  Value: {target_risk.details.get('value', 'N/A')}")
    
    # Check if it's in the dependency graph
    cell_addresses = [f"{target_risk.sheet}!G6", f"{target_risk.sheet}!G7"]
    
    for cell_addr in cell_addresses:
        print(f"\n🔍 Checking {cell_addr}:")
        
        if cell_addr in model.dependency_graph:
            print(f"  ✅ Found in dependency graph")
            
            # Get descendants
            try:
                descendants = nx.descendants(model.dependency_graph, cell_addr)
                print(f"  📊 Descendants count: {len(descendants)}")
                
                if len(descendants) > 0:
                    print(f"  📋 First 10 descendants:")
                    for i, desc in enumerate(list(descendants)[:10], 1):
                        print(f"    {i}. {desc}")
                else:
                    print(f"  ⚠️ No descendants found")
                    
                    # Check out_degree
                    out_degree = model.dependency_graph.out_degree(cell_addr)
                    in_degree = model.dependency_graph.in_degree(cell_addr)
                    print(f"  📊 Out-degree: {out_degree}, In-degree: {in_degree}")
                    
            except Exception as e:
                print(f"  ❌ Error getting descendants: {e}")
        else:
            print(f"  ❌ NOT found in dependency graph")
            
        # Check if cell exists in model.cells
        if cell_addr in model.cells:
            cell_info = model.cells[cell_addr]
            print(f"  📄 Cell info:")
            print(f"    Formula: {cell_info.formula}")
            print(f"    Value: {cell_info.value}")
        else:
            print(f"  ❌ NOT found in model.cells")

if __name__ == "__main__":
    main()
