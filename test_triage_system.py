"""
Quick test for 3-tier triage system
"""

from src.models import RiskAlert, RiskCategory
from src.analyzer import classify_risk, check_hardcode_consistency, RiskTriageEngine

# Test 1: Fatal Errors
print("Test 1: Fatal Errors")
circular_ref = RiskAlert(
    risk_type="circular_reference",
    severity="Critical",
    sheet="Sheet1",
    cell="A1",
    description="Circular reference detected"
)
assert classify_risk(circular_ref) == RiskCategory.FATAL_ERROR
print("✓ Circular reference → Fatal Error")

phantom_link = RiskAlert(
    risk_type="phantom_link",
    severity="Critical",
    sheet="Sheet1",
    cell="B1",
    description="External link detected"
)
assert classify_risk(phantom_link) == RiskCategory.FATAL_ERROR
print("✓ Phantom link → Fatal Error")

# Test 2: Integrity Risks
print("\nTest 2: Integrity Risks")
inconsistent_formula = RiskAlert(
    risk_type="inconsistent_formula",
    severity="High",
    sheet="Sheet1",
    cell="C1",
    description="Formula pattern breaks"
)
assert classify_risk(inconsistent_formula) == RiskCategory.INTEGRITY_RISK
print("✓ Inconsistent formula → Integrity Risk")

inconsistent_value = RiskAlert(
    risk_type="inconsistent_value",
    severity="High",
    sheet="Sheet1",
    cell="D1",
    description="Same label, different values"
)
assert classify_risk(inconsistent_value) == RiskCategory.INTEGRITY_RISK
print("✓ Inconsistent value → Integrity Risk")

# Test 3: Structural Debt
print("\nTest 3: Structural Debt")
merged_cell = RiskAlert(
    risk_type="merged_cell",
    severity="Medium",
    sheet="Sheet1",
    cell="E1",
    description="Merged cell detected"
)
assert classify_risk(merged_cell) == RiskCategory.STRUCTURAL_DEBT
print("✓ Merged cell → Structural Debt")

# Test 4: Hardcode Consistency Check
print("\nTest 4: Hardcode Consistency")

# Consistent hardcodes (same value)
hardcode1 = RiskAlert(
    risk_type="hidden_hardcode",
    severity="High",
    sheet="Sheet1",
    cell="F1",
    description="Hardcoded value",
    row_label="Revenue",
    details={"hardcoded_value": 100}
)
hardcode2 = RiskAlert(
    risk_type="hidden_hardcode",
    severity="High",
    sheet="Sheet1",
    cell="F2",
    description="Hardcoded value",
    row_label="Revenue",
    details={"hardcoded_value": 100}
)
all_risks = [hardcode1, hardcode2]

assert check_hardcode_consistency(hardcode1, all_risks) == True
print("✓ Consistent hardcodes detected")

assert classify_risk(hardcode1, all_risks) == RiskCategory.STRUCTURAL_DEBT
print("✓ Consistent hardcode → Structural Debt")

# Inconsistent hardcodes (different values)
hardcode3 = RiskAlert(
    risk_type="hidden_hardcode",
    severity="High",
    sheet="Sheet1",
    cell="G1",
    description="Hardcoded value",
    row_label="Cost",
    details={"hardcoded_value": 50}
)
hardcode4 = RiskAlert(
    risk_type="hidden_hardcode",
    severity="High",
    sheet="Sheet1",
    cell="G2",
    description="Hardcoded value",
    row_label="Cost",
    details={"hardcoded_value": 75}  # Different value!
)
all_risks2 = [hardcode3, hardcode4]

assert check_hardcode_consistency(hardcode3, all_risks2) == False
print("✓ Inconsistent hardcodes detected")

assert classify_risk(hardcode3, all_risks2) == RiskCategory.INTEGRITY_RISK
print("✓ Inconsistent hardcode → Integrity Risk")

# Test 5: RiskTriageEngine
print("\nTest 5: RiskTriageEngine")
all_test_risks = [
    circular_ref,
    phantom_link,
    inconsistent_formula,
    inconsistent_value,
    merged_cell,
    hardcode1,
    hardcode2
]

triage = RiskTriageEngine(all_test_risks)
triage.classify_all()

counts = triage.get_tab_counts()
print(f"✓ Fatal Errors: {counts['fatal']}")
print(f"✓ Integrity Risks: {counts['integrity']}")
print(f"✓ Structural Debt: {counts['structural']}")

assert counts['fatal'] == 2  # circular_ref, phantom_link
assert counts['integrity'] == 2  # inconsistent_formula, inconsistent_value
assert counts['structural'] == 3  # merged_cell, hardcode1, hardcode2

assert triage.get_total_count() == 7
print(f"✓ Total risks: {triage.get_total_count()}")

print("\n✅ All tests passed!")
