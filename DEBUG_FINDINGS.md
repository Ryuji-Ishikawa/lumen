# Debug Findings - 2 Potential Issues Identified

**Status:** FOUND 2 LIKELY BUGS  
**Date:** December 2, 2025

---

## TL;DR

I found 2 potential bugs that could explain the UAT failures:

1. **Column labels not filtered for formulas** → Formulas in headers picked up as labels
2. **Grouping only checks rows, not columns** → F4 and BN4 grouped (same row, far columns)

---

## Bug 1: Column Label Formula Check Missing ⚠️

### Location
`src/analyzer.py`, line ~730, in `_get_context_labels()`

### The Problem
```python
# Find column label: Scan rows 1-20 in the same column
for check_row in range(1, min(21, row_num)):
    key = f"{sheet}!{col_letter}{check_row}"
    cell = cells.get(key)
    
    if cell and cell.value:  # ← Missing: and not cell.formula
        value_str = str(cell.value).strip()
        # ... uses value_str as label
```

**Missing:** No check for `cell.formula`

**Impact:** If a column header (rows 1-20) contains a formula, it will be picked up as a label.

### Example Scenario
```
Row 1: =J9+K19-12076  (formula in header)
Row 5: 1000           (target cell)
```

**Result:** Context shows `Label @ =J9+K19-12076` ❌

### The Fix
```python
if cell and cell.value and not cell.formula:  # ← Add this check
    value_str = str(cell.value).strip()
```

---

## Bug 2: Grouping Only Checks Row Proximity ⚠️

### Location
`src/analyzer.py`, line ~470, in `_split_by_spatial_proximity()`

### The Problem
```python
def _split_by_spatial_proximity(self, sorted_risks, max_gap=1):
    # ...
    prev_row = self._extract_row_number(sorted_risks[0].cell)
    
    for risk in sorted_risks[1:]:
        curr_row = self._extract_row_number(risk.cell)
        
        # Only checks ROW gap, not COLUMN gap
        if curr_row - prev_row <= max_gap:
            current_cluster.append(risk)
```

**Missing:** No check for column proximity

**Impact:** Cells on the same row but far apart in columns will be grouped together.

### Example Scenario
```
F4:  201.26  (Column F, Row 4)
BN4: 201.26  (Column BN, Row 4)
```

**Same row (4), but 60+ columns apart!**

**Result:** Grouped as `F4...BN4` ❌

### The Fix
```python
def _split_by_spatial_proximity(self, sorted_risks, max_gap=1):
    # ...
    prev_row, prev_col = self._extract_row_col(sorted_risks[0].cell)
    
    for risk in sorted_risks[1:]:
        curr_row, curr_col = self._extract_row_col(risk.cell)
        
        # Check BOTH row and column gaps
        row_gap = abs(curr_row - prev_row)
        col_gap = abs(curr_col - prev_col)
        
        if row_gap <= max_gap and col_gap <= max_gap:
            current_cluster.append(risk)
```

---

## Questions for Business Owner

To confirm these are the issues, please check:

### For Bug 1 (Column Label):
**Q:** In the Vietnam Plan file, are there any formulas in the column headers (rows 1-20)?

**Example:** Does row 1 or row 2 contain formulas like `=J9+K19-12076`?

### For Bug 2 (Grouping):
**Q:** When you see `F4...BN13`, what are the actual cell locations?

**Example:**
- Are they: F4, F5, F6, ... BN13 (many cells)?
- Or are they: F4 and BN13 only (2 cells far apart)?

---

## Next Steps

1. **Business Owner confirms** which bug(s) match the UAT failures
2. **I implement the fixes** based on confirmation
3. **Re-test** with Vietnam Plan file
4. **Verify** CSV output is clean

---

## Full Code Review

See `CODE_REVIEW_FOR_BUSINESS_OWNER.md` for:
- Complete source code of both functions
- Detailed analysis
- Proposed fixes with code examples

---

**Prepared by:** Kiro AI Agent  
**Date:** December 2, 2025  
**Confidence:** HIGH - These 2 bugs explain the UAT failures
