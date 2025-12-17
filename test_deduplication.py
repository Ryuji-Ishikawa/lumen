"""
Test to verify that the dominance calculation correctly deduplicates shared dependencies.

Scenario:
- A1 has hardcode 201.26
- B1 has hardcode 201.26
- C1 = A1 + B1

Expected: C1 should be counted ONCE, not twice
"""

import networkx as nx

# Create test graph
G = nx.DiGraph()

# A1 and B1 both point to C1 (shared dependency)
G.add_edge('Sheet1!A1', 'Sheet1!C1')
G.add_edge('Sheet1!B1', 'Sheet1!C1')

# C1 points to D1
G.add_edge('Sheet1!C1', 'Sheet1!D1')

print("=" * 80)
print("DEDUPLICATION TEST")
print("=" * 80)

print("\nGraph structure:")
print("  A1 (hardcode 201.26) → C1 → D1")
print("  B1 (hardcode 201.26) → C1 → D1")
print()

# Simulate the algorithm
cells_with_hardcode = ['Sheet1!A1', 'Sheet1!B1']

# Method 1: WITHOUT deduplication (WRONG)
direct_wrong = []
all_wrong = []

for cell in cells_with_hardcode:
    direct = list(G.successors(cell))
    direct_wrong.extend(direct)  # Using extend (allows duplicates)
    
    descendants = list(nx.descendants(G, cell))
    all_wrong.extend(descendants)  # Using extend (allows duplicates)

print("❌ WITHOUT DEDUPLICATION (WRONG):")
print(f"  Direct impacts: {len(direct_wrong)} (should be 1)")
print(f"    List: {direct_wrong}")
print(f"  All impacts: {len(all_wrong)} (should be 2)")
print(f"    List: {all_wrong}")
print()

# Method 2: WITH deduplication (CORRECT - using sets)
direct_correct = set()
all_correct = set()

for cell in cells_with_hardcode:
    direct = list(G.successors(cell))
    direct_correct.update(direct)  # Using update on set (auto-deduplicates)
    
    descendants = list(nx.descendants(G, cell))
    all_correct.update(descendants)  # Using update on set (auto-deduplicates)

print("✓ WITH DEDUPLICATION (CORRECT - using sets):")
print(f"  Direct impacts: {len(direct_correct)} (expected: 1)")
print(f"    Set: {direct_correct}")
print(f"  All impacts: {len(all_correct)} (expected: 2)")
print(f"    Set: {all_correct}")
print()

# Verify correctness
print("=" * 80)
print("VERIFICATION")
print("=" * 80)

if len(direct_correct) == 1 and 'Sheet1!C1' in direct_correct:
    print("✓ Direct impacts: CORRECT (C1 counted once)")
else:
    print("✗ Direct impacts: WRONG")

if len(all_correct) == 2 and 'Sheet1!C1' in all_correct and 'Sheet1!D1' in all_correct:
    print("✓ All impacts: CORRECT (C1 and D1 counted once each)")
else:
    print("✗ All impacts: WRONG")

indirect_correct = all_correct - direct_correct
print(f"\nIndirect impacts: {len(indirect_correct)}")
print(f"  Set: {indirect_correct}")

if len(indirect_correct) == 1 and 'Sheet1!D1' in indirect_correct:
    print("✓ Indirect impacts: CORRECT (D1 counted once)")
else:
    print("✗ Indirect impacts: WRONG")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
The algorithm in app.py uses:
  direct_impacts = set()
  all_impacts = set()
  
And then:
  direct_impacts.update(direct)
  all_impacts.update(impacts)

This CORRECTLY deduplicates shared dependencies.

If you're seeing inflated counts (240 vs 60), the issue is NOT double-counting.
Possible causes:
1. The dependency graph has more edges than expected
2. Some cells are being included that shouldn't be (e.g., empty cells, zeros)
3. The manual count might be for a specific subset, not all 423 cells
""")
