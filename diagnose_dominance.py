"""
Diagnostic script to understand dominance calculation discrepancies

Usage: python diagnose_dominance.py <excel_file> <hardcoded_value>
Example: python diagnose_dominance.py "Sample_Business Plan.xlsx" "201.26"
"""

import sys
sys.path.insert(0, '.')

from src.parser import ExcelParser
from src.analyzer import ModelAnalyzer
import networkx as nx

if len(sys.argv) < 3:
    print("Usage: python diagnose_dominance.py <excel_file> <hardcoded_value>")
    print('Example: python diagnose_dominance.py "Sample_Business Plan.xlsx" "201.26"')
    sys.exit(1)

excel_file = sys.argv[1]
target_value = sys.argv[2]

print("=" * 80)
print(f"DOMINANCE DIAGNOSTIC FOR VALUE: {target_value}")
print(f"FILE: {excel_file}")
print("=" * 80)

# Parse and analyze
parser = ExcelParser()
model = parser.parse(excel_file)

analyzer = ModelAnalyzer()
model = analyzer.analyze(model)

# Find all cells with the target value
cells_with_value = []
matching_risks = []

for risk in model.risks:
    if risk.risk_type == "Hidden Hardcode":
        hardcoded_value = str(risk.details.get("hardcoded_value", ""))
        if hardcoded_value == target_value:
            matching_risks.append(risk)
            if 'cells' in risk.details and risk.details['cells']:
                for cell in risk.details['cells']:
                    cells_with_value.append(f"{risk.sheet}!{cell}")
            else:
                cells_with_value.append(risk.get_location())

print(f"\nFound {len(matching_risks)} risk groups with value {target_value}")
print(f"Total cells: {len(cells_with_value)}")

if not cells_with_value:
    print("\n❌ No cells found with this value!")
    print("\nAvailable hardcoded values:")
    values = set()
    for risk in model.risks:
        if risk.risk_type == "Hidden Hardcode":
            values.add(str(risk.details.get("hardcoded_value", "")))
    for val in sorted(values):
        print(f"  - {val}")
    sys.exit(1)

# Show risk groups
print("\nRisk groups:")
for i, risk in enumerate(matching_risks, 1):
    cell_count = risk.details.get("instance_count", 1)
    print(f"  {i}. {risk.sheet}!{risk.cell} - {cell_count} cells")
    print(f"     Context: {risk.row_label}")

# Calculate impacts
print("\n" + "=" * 80)
print("CALCULATING IMPACTS")
print("=" * 80)

direct_impacts = set()
all_impacts = set()

# Track per-cell statistics
cells_with_no_deps = []
cells_with_deps = []

for cell_address in cells_with_value:
    # Check if cell is in graph
    if cell_address not in model.dependency_graph:
        cells_with_no_deps.append(cell_address)
        continue
    
    # Get direct
    direct = list(model.dependency_graph.successors(cell_address))
    if direct:
        cells_with_deps.append((cell_address, len(direct)))
    direct_impacts.update(direct)
    
    # Get all
    try:
        descendants = list(nx.descendants(model.dependency_graph, cell_address))
        all_impacts.update(descendants)
    except:
        pass

print(f"\nCells in dependency graph: {len(cells_with_value) - len(cells_with_no_deps)}/{len(cells_with_value)}")
print(f"Cells with no dependents: {len(cells_with_no_deps)}")
print(f"Cells with dependents: {len(cells_with_deps)}")

if cells_with_deps:
    print(f"\nSample cells with dependents:")
    for cell, count in cells_with_deps[:5]:
        print(f"  {cell}: {count} direct dependents")

# Final counts
total_dominance = len(all_impacts)
direct_dominance = len(direct_impacts)
indirect_dominance = total_dominance - direct_dominance

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

print(f"\n📊 Impact Counts:")
print(f"  Direct impacts: {direct_dominance}")
print(f"  Indirect impacts: {indirect_dominance}")
print(f"  Total impacts: {total_dominance}")

# Verify subset relationship
if direct_impacts.issubset(all_impacts):
    print(f"\n✓ Direct impacts are a subset of all impacts (correct)")
else:
    print(f"\n✗ ERROR: Direct impacts are NOT a subset of all impacts!")
    only_in_direct = direct_impacts - all_impacts
    print(f"  Cells only in direct: {len(only_in_direct)}")

# Show sample impacts
print(f"\nSample direct impacts:")
for cell in list(direct_impacts)[:5]:
    print(f"  {cell}")

print(f"\nSample indirect impacts (in all but not in direct):")
indirect_only = all_impacts - direct_impacts
for cell in list(indirect_only)[:5]:
    print(f"  {cell}")

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

print(f"""
The algorithm found:
- {len(cells_with_value)} cells containing the value {target_value}
- {direct_dominance} unique cells that directly depend on these cells
- {indirect_dominance} unique cells that indirectly depend (through chains)
- {total_dominance} total unique dependent cells

If your manual count differs, possible reasons:
1. Manual count might be for a single row, not all {len(cells_with_value)} cells
2. Some dependencies might not be captured in formulas
3. Circular references or complex formula patterns
4. Cross-sheet references that weren't parsed correctly
""")
