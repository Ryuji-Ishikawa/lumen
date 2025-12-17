"""
Test to verify NetworkX graph behavior for successors vs descendants
"""

import networkx as nx

# Create a simple test graph
# A -> B -> C -> D
#  \-> E -> F
G = nx.DiGraph()
G.add_edges_from([
    ('A', 'B'),
    ('B', 'C'),
    ('C', 'D'),
    ('A', 'E'),
    ('E', 'F')
])

print("Graph structure:")
print("A -> B -> C -> D")
print(" \\-> E -> F")
print()

# Test successors (direct children)
successors_A = list(G.successors('A'))
print(f"Successors of A (direct children): {successors_A}")
print(f"Count: {len(successors_A)}")
print()

# Test descendants (all children recursively)
descendants_A = list(nx.descendants(G, 'A'))
print(f"Descendants of A (all children): {descendants_A}")
print(f"Count: {len(descendants_A)}")
print()

# Check if successors are subset of descendants
successors_set = set(successors_A)
descendants_set = set(descendants_A)

print(f"Are successors a subset of descendants? {successors_set.issubset(descendants_set)}")
print(f"Successors: {successors_set}")
print(f"Descendants: {descendants_set}")
print()

# Calculate indirect (should be descendants - successors)
indirect = descendants_set - successors_set
print(f"Indirect (descendants - successors): {indirect}")
print(f"Count: {len(indirect)}")
print()

print("EXPECTED BEHAVIOR:")
print(f"  Direct: {len(successors_set)} (B, E)")
print(f"  Indirect: {len(indirect)} (C, D, F)")
print(f"  Total: {len(descendants_set)} (B, C, D, E, F)")
