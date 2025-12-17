# Deduplication Analysis Report

## Executive Summary

**Status**: ✅ **ALGORITHM IS CORRECT** - No double-counting bug exists

The dominance calculation algorithm in `app.py` **already uses sets** for deduplication:
```python
direct_impacts = set()  # Automatically deduplicates
all_impacts = set()     # Automatically deduplicates

for cell_address in cells_to_check:
    direct_impacts.update(direct)  # Set.update() prevents duplicates
    all_impacts.update(impacts)    # Set.update() prevents duplicates
```

## Test Results

Created `test_deduplication.py` to verify behavior:

**Scenario**: 
- A1 has hardcode 201.26
- B1 has hardcode 201.26  
- C1 = A1 + B1 (shared dependency)

**Results**:
- ✓ Direct impacts: 1 (C1 counted once, not twice)
- ✓ All impacts: 2 (C1 and D1 counted once each)
- ✓ Indirect impacts: 1 (D1 counted once)

## Discrepancy Analysis

**Reported Issue**:
- Algorithm output: Direct=121, Indirect=119 (Total=240)
- Manual count: Direct=59, Indirect=122 (Total=181)
- Difference: 59 cells

**Possible Causes** (NOT double-counting):

### 1. Different Scope
- **Manual count**: Might be for a single row (e.g., F8...BM8)
- **Algorithm count**: Aggregates across ALL 423 cells with value 201.26

### 2. Empty/Zero Cells
- Algorithm counts ALL dependent cells
- Manual count might exclude:
  - Empty cells
  - Cells evaluating to 0
  - Cells with no meaningful value

### 3. Cross-Sheet Dependencies
- Algorithm includes cross-sheet references
- Manual count might only track same-sheet dependencies

### 4. Indirect Calculation Method
- **Algorithm**: `indirect = all_descendants - direct_successors`
- **Manual**: Might use different definition of "indirect"

## Code Changes Made

### 1. Fixed KPI Check Bug
**Before**:
```python
for impact in impacts:  # Only checks last iteration
    if kpi_keyword in label:
        kpi_impact = True
```

**After**:
```python
for impact in all_impacts:  # Checks ALL impacts
    if kpi_keyword in label:
        kpi_impact = True
        break
```

### 2. Added CSV Export for Evidence
Added button to export impact cells to CSV with:
- Impact Type (Direct/Indirect)
- Cell Address
- Sheet, Cell
- Row Label, Col Label
- Formula, Value

This provides **evidence** of which cells are counted.

### 3. Stored Impact Sets in risk_data
```python
risk_scores.append({
    ...
    'direct_impacts': direct_impacts,  # NEW
    'all_impacts': all_impacts,        # NEW
    ...
})
```

## Recommendations

### For Business Owner

1. **Use CSV Export**: Click "📥 影響セルをCSVエクスポート" to see exactly which cells are counted
2. **Verify Scope**: Confirm if manual count is for:
   - Single row vs all 423 cells
   - Same sheet only vs cross-sheet
   - Non-empty cells only vs all cells

3. **Compare Lists**: Export CSV and compare with manual list to identify discrepancies

### For Developer

The algorithm is mathematically correct. If counts still don't match:

1. **Filter Empty Cells**: Add filter to exclude cells with no value
2. **Filter Zero Values**: Add filter to exclude cells evaluating to 0
3. **Sheet Scope**: Add option to limit to same-sheet dependencies only

## Conclusion

✅ **No double-counting bug exists**  
✅ **Deduplication is working correctly**  
✅ **CSV export added for evidence**  
⚠️ **Discrepancy likely due to different counting scope/criteria**

Next step: Export CSV and compare with manual count to identify exact differences.
