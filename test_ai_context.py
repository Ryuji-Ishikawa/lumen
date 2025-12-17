"""
Quick test to verify AI Context Recovery is working
"""

from src.smart_context import SmartContextRecovery
from src.models import CellInfo

# Create test data
cells = {
    "Sheet1!A5": CellInfo("Sheet1", "A5", "Revenue", None, []),
    "Sheet1!B5": CellInfo("Sheet1", "B5", 1000, "=SUM(C1:C4)", []),
    "Sheet1!C5": CellInfo("Sheet1", "C5", 2000, None, []),  # Target cell
}

# Test without API key
print("Test 1: Without API key")
smart_context = SmartContextRecovery("OpenAI", None)
result = smart_context.recover_context("Sheet1", "C5", cells)
print(f"Result: {result}")
print(f"Expected: None (no API key)")
print()

# Test with fake API key (will fail but show it's trying)
print("Test 2: With API key (will fail but show attempt)")
smart_context = SmartContextRecovery("OpenAI", "sk-test123")
result = smart_context.recover_context("Sheet1", "C5", cells)
print(f"Result: {result}")
print(f"Expected: None (invalid key, but attempted)")
print()

# Show grid extraction
print("Test 3: Grid extraction")
grid = smart_context._extract_grid("Sheet1", "C5", cells)
print("Extracted grid:")
for addr, val in sorted(grid.items()):
    print(f"  {addr}: {val}")
