"""
Debug script to trace dominance calculation for 201.26 value
Compares algorithm output with manual count expectations:
- Expected: Direct=59, Indirect=122
- Actual: Direct=121, Indirect=119
"""

import sys
sys.path.insert(0, '.')

from src.parser import ExcelParser
from src.models import ModelAnalysis
import networkx as nx

# Parse the file
parser = ExcelParser()
model = parser.parse('Sample_Business Plan.xlsx')

print("Sheets in workbook:")
import openpyxl
wb = openpyxl.load_workbook('Sample_Business Plan.xlsx', data_only=False)
for sheet_name in wb.sheetnames:
    print(f"  - {sheet_name}")
print()

# Run analyzer to detect risks
from src.analyzer import ModelAnalyzer
analyzer = ModelAnalyzer()
model = analyzer.analyze(model)

print("=" * 80)
print("DOMINANCE CALCULATION DEBUG FOR 201.26")
print("=" * 80)

# Find all cells with hardcoded value 201.26
target_value = "201.26"
target_sheet = "プロジェクションVDN"
cells_with_value = []

print(f"Total risks found: {len(model.risks)}")

# First, let's see what sheets we have
print("\nAll sheets with risks:")
sheets = set()
for risk in model.risks:
    sheets.add(risk.sheet)
for sheet in sorted(sheets):
    print(f"  - {sheet}")

# First, let's see what hardcoded values we have on the target sheet
print(f"\nAll hardcoded values found on sheet '{target_sheet}':")
for risk in model.risks:
    if risk.risk_type == "Hidden Hardcode" and risk.sheet == target_sheet:
        hardcoded_value = risk.details.get("hardcoded_value", "")
        cell_count = risk.details.get("instance_count", 1)
        print(f"  Value: {hardcoded_value}, Instances: {cell_count}, Location: {risk.sheet}!{risk.cell}")

for risk in model.risks:
    if risk.risk_type == "Hidden Hardcode" and risk.sheet == target_sheet:
        hardcoded_value = risk.details.get("hardcoded_value", "")
        # Try both string and float comparison
        try:
            if str(hardcoded_value) == target_value or abs(float(hardcoded_value) - float(target_value)) < 0.01:
                # Get all cells for this risk
                if 'cells' in risk.details and risk.details['cells']:
                    for cell in risk.details['cells']:
                        cells_with_value.append(f"{risk.sheet}!{cell}")
                else:
                    cells_with_value.append(risk.get_location())
        except:
            pass

print(f"\nFound {len(cells_with_value)} cells with value {target_value}")
print("Cells:", cells_with_value[:10], "..." if len(cells_with_value) > 10 else "")

# Calculate direct and indirect impacts
direct_impacts = set()
all_impacts = set()

print("\n" + "=" * 80)
print("CALCULATING IMPACTS FOR EACH CELL")
print("=" * 80)

for i, cell_address in enumerate(cells_with_value[:5], 1):  # Show first 5 for detail
    print(f"\n[{i}] Cell: {cell_address}")
    
    # Direct impacts (successors)
    if cell_address in model.dependency_graph:
        direct = list(model.dependency_graph.successors(cell_address))
        print(f"  Direct successors: {len(direct)}")
        if direct:
            print(f"    Examples: {direct[:3]}")
        direct_impacts.update(direct)
    else:
        print(f"  Not in dependency graph")
    
    # All impacts (descendants)
    try:
        descendants = list(nx.descendants(model.dependency_graph, cell_address))
        print(f"  All descendants: {len(descendants)}")
        if descendants:
            print(f"    Examples: {descendants[:3]}")
        all_impacts.update(descendants)
    except:
        print(f"  No descendants found")

# Process remaining cells silently
for cell_address in cells_with_value[5:]:
    if cell_address in model.dependency_graph:
        direct = list(model.dependency_graph.successors(cell_address))
        direct_impacts.update(direct)
    
    try:
        descendants = list(nx.descendants(model.dependency_graph, cell_address))
        all_impacts.update(descendants)
    except:
        pass

print("\n" + "=" * 80)
print("FINAL RESULTS")
print("=" * 80)

total_dominance = len(all_impacts)
direct_dominance = len(direct_impacts)
indirect_dominance = total_dominance - direct_dominance

print(f"\nDirect impacts (successors): {direct_dominance}")
print(f"All impacts (descendants): {total_dominance}")
print(f"Indirect impacts (descendants - successors): {indirect_dominance}")

print("\n" + "=" * 80)
print("COMPARISON WITH MANUAL COUNT")
print("=" * 80)

expected_direct = 59
expected_indirect = 122
expected_total = expected_direct + expected_indirect

print(f"\nExpected:")
print(f"  Direct: {expected_direct}")
print(f"  Indirect: {expected_indirect}")
print(f"  Total: {expected_total}")

print(f"\nActual:")
print(f"  Direct: {direct_dominance} (diff: {direct_dominance - expected_direct:+d})")
print(f"  Indirect: {indirect_dominance} (diff: {indirect_dominance - expected_indirect:+d})")
print(f"  Total: {total_dominance} (diff: {total_dominance - expected_total:+d})")

# Analyze the discrepancy
print("\n" + "=" * 80)
print("DISCREPANCY ANALYSIS")
print("=" * 80)

print(f"\nDirect impacts are {direct_dominance - expected_direct:+d} off")
print(f"Indirect impacts are {indirect_dominance - expected_indirect:+d} off")

# Check if there's overlap between direct and all impacts
print(f"\nDirect impacts that are also in all impacts: {len(direct_impacts & all_impacts)}")
print(f"This should be {len(direct_impacts)} (all direct should be in all)")

# Sample some direct impacts to see what they are
print(f"\nSample direct impacts:")
for cell in list(direct_impacts)[:10]:
    print(f"  {cell}")

print(f"\nSample all impacts:")
for cell in list(all_impacts)[:10]:
    print(f"  {cell}")

# Check if direct impacts are a subset of all impacts
if direct_impacts.issubset(all_impacts):
    print("\n✓ Direct impacts are a proper subset of all impacts (correct)")
else:
    print("\n✗ ERROR: Direct impacts are NOT a subset of all impacts!")
    only_in_direct = direct_impacts - all_impacts
    print(f"  Cells only in direct: {len(only_in_direct)}")
    print(f"  Examples: {list(only_in_direct)[:5]}")
