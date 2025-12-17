# Diffusion Scoring Fix - Phase 7.3

## Problem Identified

Value **201.26** appears **423 times** across the workbook but was NOT ranked as the highest risk.

### Root Cause Analysis

The danger score calculation in `app.py` was **ignoring the Diffusion metric** completely.

**Old Formula:**
```
score = impact_count × 10 + KPI_bonus + severity_bonus
```

This only considered:
- **Dominance** (how many cells depend on it)
- KPI impact
- Severity level

But it completely ignored:
- **Diffusion** (how many times the value appears) ❌

### Evidence from CSV Export

**201.26 Diffusion:**
- プロジェクションVDN!F4: 1 instance
- プロジェクションVDN!F8...BM8: 60 instances
- プロジェクションVDN!G9...BN9: 60 instances
- プロジェクションVDN!F10...BM10: 60 instances
- プロジェクションVDN!F13...BN13: 61 instances
- プロジェクションVDN!H19...BN19: 59 instances
- プロジェクションVDN!F21...BN21: 61 instances
- プロジェクションVDN!F24...BN24: 61 instances
- **Total: 423 occurrences** 🔥

**1000000 Diffusion:**
- Total: 269 occurrences

Yet 201.26 was ranking lower because it had fewer dependents (Dominance).

## Solution Implemented

### New Danger Score Formula

```python
score = (Diffusion × 5) + (Dominance × 10) + KPI_bonus + Severity_bonus
```

**Weights:**
- **Diffusion**: 5 points per occurrence (NEW!)
- **Dominance**: 10 points per dependent cell
- **KPI Impact**: +1000 bonus
- **Severity**: +100 (High) or +200 (Critical)

### Why This Works

For value **201.26** with 423 occurrences:
```
score = 423 × 5 = 2,115 points from Diffusion alone
```

This ensures widespread values like 201.26 rank appropriately high, even if they have fewer dependents.

### Code Changes

**File: `app.py` (lines ~715-740)**

1. **Calculate Diffusion** for each risk:
```python
# Get diffusion (how many times this value appears)
hardcoded_value = risk.details.get('hardcoded_value', '')
diffusion = 0
for r in model.risks:
    if r.risk_type == "Hidden Hardcode" and r.details.get('hardcoded_value') == hardcoded_value:
        diffusion += r.details.get('instance_count', 1)
```

2. **Updated Score Calculation**:
```python
score = diffusion * 5  # NEW: Diffusion weight
score += impact_count * 10  # Dominance weight
if kpi_impact:
    score += 1000
if risk.severity == "High":
    score += 100
elif risk.severity == "Critical":
    score += 200
```

3. **Updated UI Display** to show Diffusion metric:
```python
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Diffusion", f"{diffusion}x", help="How many times this value appears")
with col2:
    st.metric("Dominance", f"{impact_count}", help="How many cells depend on this")
```

## Expected Result

After this fix, **201.26 should rank as #1 or very high** in the Top 3 Most Dangerous Hardcodes because:

- **Diffusion**: 423 occurrences → 2,115 points
- **Severity**: High → +100 points
- **Total**: 2,215+ points (before Dominance)

This is significantly higher than values with lower diffusion.

## Testing Instructions

1. Run the app: `streamlit run app.py`
2. Upload the same Excel file that generated `2025-12-03T06-08_export.csv`
3. Check the "Top 3 Most Dangerous Hardcodes" section
4. Verify that **201.26** now appears in the top rankings
5. Verify the Diffusion metric shows **423** or similar high count

## Business Impact

This fix ensures the AI analyzer correctly identifies **widespread hardcoded values** as high-risk, which is critical for:

- **Centralization refactoring**: Values appearing 400+ times need to be extracted to a single driver cell
- **Maintenance risk**: Changing 201.26 requires updating 423 locations (error-prone)
- **Model reliability**: Widespread hardcodes indicate poor model structure

The formula now balances both:
- **Diffusion** (how scattered the value is)
- **Dominance** (how much impact it has on other cells)

Both metrics are essential for accurate risk assessment.
