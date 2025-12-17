"""
Debug script to investigate Value and Impact issues
"""

from pathlib import Path
from src.parser import parse_excel_file
from src.analyzer import ModelAnalyzer

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
    
    print(f"\n📊 Total risks: {len(model.risks)}")
    
    # Find Inconsistent Formula risks
    inconsistent_formula_risks = [r for r in model.risks if r.risk_type == "Inconsistent Formula"]
    
    print(f"\n📋 Inconsistent Formula risks: {len(inconsistent_formula_risks)}")
    
    # Show first 10 with details
    for i, risk in enumerate(inconsistent_formula_risks[:10], 1):
        print(f"\n{i}. {risk.sheet}!{risk.cell}")
        print(f"   Context: {risk.get_context()}")
        print(f"   Impact: {risk.details.get('impact_count', 0)}")
        
        # Check value sources
        value = risk.details.get("value")
        cell_value = risk.details.get("cell_value")
        hardcoded_value = risk.details.get("hardcoded_value")
        formula = risk.details.get("formula")
        
        print(f"   Value sources:")
        print(f"     - value: {value}")
        print(f"     - cell_value: {cell_value}")
        print(f"     - hardcoded_value: {hardcoded_value}")
        print(f"     - formula: {formula[:50] if formula else None}")
        
        # Check if cell exists in dependency graph
        cell_address = f"{risk.sheet}!{risk.cell}"
        if cell_address in model.dependency_graph:
            print(f"   ✅ In dependency graph")
            
            # Check descendants
            import networkx as nx
            try:
                descendants = nx.descendants(model.dependency_graph, cell_address)
                print(f"   📊 Actual descendants: {len(descendants)}")
                if len(descendants) > 0 and len(descendants) <= 5:
                    print(f"   📋 Descendants: {list(descendants)}")
            except Exception as e:
                print(f"   ❌ Error getting descendants: {e}")
        else:
            print(f"   ❌ NOT in dependency graph")
            
            # Check if it's a multi-cell address
            if "," in risk.cell or ":" in risk.cell:
                print(f"   ⚠️ Multi-cell address detected: {risk.cell}")
                
                # Try individual cells
                if "," in risk.cell:
                    cells = [c.strip() for c in risk.cell.split(",")]
                    print(f"   🔍 Trying individual cells: {cells}")
                    for cell in cells:
                        test_addr = f"{risk.sheet}!{cell}"
                        if test_addr in model.dependency_graph:
                            print(f"     ✅ {test_addr} found in graph")
                            try:
                                desc = nx.descendants(model.dependency_graph, test_addr)
                                print(f"       Descendants: {len(desc)}")
                            except:
                                pass
                        else:
                            print(f"     ❌ {test_addr} NOT in graph")

if __name__ == "__main__":
    main()
