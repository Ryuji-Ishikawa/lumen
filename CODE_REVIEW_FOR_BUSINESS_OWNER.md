# Code Review - Context & Grouping Logic

**For Business Owner Review**  
**Date:** December 2, 2025

---

## Issue Summary

The UAT is still showing:
1. **Context picking up formulas** - Context shows formulas instead of text labels
2. **Risk grouping too broad** - Scattered cells being grouped together

Let's review the code together to find the edge cases.

---

## 1. Context Extraction Logic (`_get_context_labels`)

### Full Source Code:

```python
def _get_context_labels(self, sheet: str, cell_address: str, 
                       cells: Dict[str, CellInfo]) -> tuple:
    """
    Find row and column labels for a cell.
    
    Args:
        sheet: Sheet name
        cell_address: Cell address (e.g., "E92")
        cells: Dictionary of all cells
        
    Returns:
        Tuple of (row_label, col_label)
    """
    import re
    from openpyxl.utils import column_index_from_string, get_column_letter
    
    # Parse cell address (e.g., "E92" -> col="E", row=92)
    match = re.match(r'^([A-Z]+)(\d+)$', cell_address)
    if not match:
        return None, None
    
    col_letter = match.group(1)
    row_num = int(match.group(2))
    col_num = column_index_from_string(col_letter)
    
    # Find row label: Nearest Neighbor Search with TYPE FILTER
    row_label = None
    
    # Strategy 1: Look LEFT from target cell until TEXT is found
    for check_col in range(col_num - 1, 0, -1):  # Scan ALL columns to the left
        check_col_letter = get_column_letter(check_col)
        key = f"{sheet}!{check_col_letter}{row_num}"
        cell = cells.get(key)
        
        # If cell is empty, keep moving left (don't stop)
        if not cell or not cell.value:
            continue  # Keep scanning left
        
        # TYPE FILTER: Accept ONLY text labels
        # CRITICAL: Check cell.formula FIRST, not cell.value
        if cell.formula:
            # This is a formula cell - REJECT and keep scanning
            continue
        
        # Now check the value
        value = cell.value
        
        if isinstance(value, str):
            value_str = value.strip()
            
            # REJECT if starts with =
            if value_str.startswith('='):
                continue  # Keep scanning left
            
            # ACCEPT non-empty text
            if value_str:
                row_label = value_str
                break
        
        elif isinstance(value, (int, float)):
            # REJECT numbers unless it looks like a year (2020-2030)
            if 2020 <= value <= 2030:
                row_label = str(int(value))
                break
            else:
                continue  # Keep scanning left
    
    # Strategy 2: If nothing found on left, check row above (header)
    if not row_label and row_num > 1:
        key = f"{sheet}!{col_letter}{row_num - 1}"
        cell = cells.get(key)
        
        if cell:
            # Apply same TYPE FILTER
            if cell.formula:
                pass  # Formula cell - reject
            elif cell.value:
                value = cell.value
                
                if isinstance(value, str):
                    value_str = value.strip()
                    # REJECT formulas, ACCEPT text
                    if not value_str.startswith('=') and value_str:
                        row_label = value_str
    
    # Find column label: Scan rows 1-20 in the same column
    col_label = None
    for check_row in range(1, min(21, row_num)):  # Rows 1-20
        key = f"{sheet}!{col_letter}{check_row}"
        cell = cells.get(key)
        
        if cell and cell.value:
            value_str = str(cell.value).strip()
            
            # Check if it matches a date pattern
            date_patterns = [
                r'\d{2}-\d{4}',  # 04-2024
                r'\d{4}-\d{2}',  # 2024-04
                r'[A-Z][a-z]{2}\s+\d{4}',  # Apr 2024
                r'Q\d',  # Q1, Q2, etc.
                r'FY\s*\d{4}',  # FY2024, FY 2024
            ]
            
            for pattern in date_patterns:
                if re.search(pattern, value_str):
                    col_label = value_str
                    break
            
            if col_label:
                break
    
    return row_label, col_label
```

### Potential Issues:

**ISSUE 1: Column Label Not Filtered**
```python
# Line ~730: Column label extraction
if cell and cell.value:
    value_str = str(cell.value).strip()
    # ⚠️ PROBLEM: No check for cell.formula here!
    # If the column header is a formula, it will be accepted
```

**Diagnosis:** The column label extraction (lines ~730-750) does NOT check `cell.formula`. If a column header contains a formula, it will be picked up as a label.

**Fix Needed:**
```python
# Find column label: Scan rows 1-20 in the same column
col_label = None
for check_row in range(1, min(21, row_num)):
    key = f"{sheet}!{col_letter}{check_row}"
    cell = cells.get(key)
    
    # ADD THIS CHECK:
    if cell and cell.value and not cell.formula:  # ← Check formula!
        value_str = str(cell.value).strip()
        # ... rest of logic
```

---

## 2. Context Concatenation Logic (`get_context`)

### Full Source Code:

```python
def get_context(self) -> str:
    """Return contextual label combining row and column labels"""
    if self.row_label and self.col_label:
        return f"{self.row_label} @ {self.col_label}"
    elif self.row_label:
        return self.row_label
    elif self.col_label:
        return self.col_label
    else:
        return ""
```

### Analysis:

This code is **CLEAN** - it only concatenates the labels. The issue is that the labels themselves contain formulas (from Issue 1 above).

---

## 3. Risk Grouping Logic (`_compress_risks` & `_split_by_spatial_proximity`)

### Full Source Code:

```python
def _compress_risks(self, risks: List[RiskAlert]) -> List[RiskAlert]:
    """
    Compress duplicate risks into grouped alerts with spatial proximity checking.
    """
    from collections import defaultdict
    
    # Group risks by type, sheet, and value
    risk_groups = defaultdict(list)
    
    for risk in risks:
        # Create a grouping key
        if risk.risk_type == "Hidden Hardcode":
            # Group hardcodes by sheet and value
            hardcoded_value = risk.details.get("hardcoded_value", "")
            key = (risk.risk_type, risk.sheet, hardcoded_value)
        else:
            # Don't compress other risk types
            key = (risk.risk_type, risk.sheet, risk.cell, id(risk))
        
        risk_groups[key].append(risk)
    
    # Create compressed risks with spatial proximity checking
    compressed = []
    for key, group in risk_groups.items():
        if len(group) == 1:
            # Single risk, no compression needed
            compressed.append(group[0])
        else:
            # Multiple risks - check spatial proximity before grouping
            if key[0] == "Hidden Hardcode":
                # Sort by row number for spatial analysis
                sorted_group = sorted(group, key=lambda r: self._extract_row_number(r.cell))
                
                # Split into spatially proximate clusters
                clusters = self._split_by_spatial_proximity(sorted_group)
                
                # Compress each cluster separately
                for cluster in clusters:
                    compressed.append(self._create_compressed_risk(cluster))
            else:
                # Non-hardcode risks: compress normally
                compressed.append(self._create_compressed_risk(group))
    
    return compressed

def _split_by_spatial_proximity(self, sorted_risks: List[RiskAlert], max_gap: int = 1) -> List[List[RiskAlert]]:
    """
    Split risks into spatially proximate clusters.
    
    Rule: If gap > 1 row/col, split the group.
    """
    if not sorted_risks:
        return []
    
    clusters = []
    current_cluster = [sorted_risks[0]]
    prev_row = self._extract_row_number(sorted_risks[0].cell)
    
    for risk in sorted_risks[1:]:
        curr_row = self._extract_row_number(risk.cell)
        
        # Only group if gap <= 1 (neighbors only)
        if curr_row - prev_row <= max_gap:
            # Close enough - add to current cluster
            current_cluster.append(risk)
        else:
            # Too far - start new cluster
            clusters.append(current_cluster)
            current_cluster = [risk]
        
        prev_row = curr_row
    
    # Add final cluster
    clusters.append(current_cluster)
    
    return clusters
```

### Potential Issues:

**ISSUE 2: Only Checks Row Proximity, Not Column**
```python
# Line ~470: Only extracts row number
def _extract_row_number(self, cell_address: str) -> int:
    """Extract row number from cell address (e.g., 'F24' -> 24)"""
    match = re.match(r'[A-Z]+(\d+)', cell_address)
    return int(match.group(1)) if match else 0
```

**Diagnosis:** The grouping logic only checks ROW proximity, not COLUMN proximity. If you have:
- F4 (201.26)
- BN4 (201.26)

They are on the SAME ROW (row 4), so they will be grouped together even though they are many columns apart!

**Fix Needed:**
```python
def _split_by_spatial_proximity(self, sorted_risks: List[RiskAlert], max_gap: int = 1):
    """
    Split risks into spatially proximate clusters.
    
    Rule: If gap > 1 row OR column, split the group.
    """
    if not sorted_risks:
        return []
    
    clusters = []
    current_cluster = [sorted_risks[0]]
    prev_row, prev_col = self._extract_row_col(sorted_risks[0].cell)
    
    for risk in sorted_risks[1:]:
        curr_row, curr_col = self._extract_row_col(risk.cell)
        
        # Check BOTH row and column proximity
        row_gap = abs(curr_row - prev_row)
        col_gap = abs(curr_col - prev_col)
        
        if row_gap <= max_gap and col_gap <= max_gap:
            # Close enough - add to current cluster
            current_cluster.append(risk)
        else:
            # Too far - start new cluster
            clusters.append(current_cluster)
            current_cluster = [risk]
        
        prev_row, prev_col = curr_row, curr_col
    
    # Add final cluster
    clusters.append(current_cluster)
    
    return clusters

def _extract_row_col(self, cell_address: str) -> tuple:
    """Extract row and column from cell address (e.g., 'F24' -> (24, 6))"""
    from openpyxl.utils import column_index_from_string
    match = re.match(r'([A-Z]+)(\d+)', cell_address)
    if match:
        col_letter = match.group(1)
        row_num = int(match.group(2))
        col_num = column_index_from_string(col_letter)
        return row_num, col_num
    return 0, 0
```

---

## Summary of Issues Found

| Issue | Location | Problem | Impact |
|-------|----------|---------|--------|
| 1 | `_get_context_labels` (col_label) | No `cell.formula` check for column labels | Formulas in column headers picked up as labels |
| 2 | `_split_by_spatial_proximity` | Only checks row proximity, not column | F4 and BN4 grouped together (same row, different columns) |

---

## Recommended Fixes

### Fix 1: Add Formula Check to Column Label Extraction

**Location:** `src/analyzer.py`, line ~730

**Change:**
```python
# BEFORE:
if cell and cell.value:
    value_str = str(cell.value).strip()

# AFTER:
if cell and cell.value and not cell.formula:  # ← Add formula check
    value_str = str(cell.value).strip()
```

### Fix 2: Check Both Row AND Column Proximity

**Location:** `src/analyzer.py`, `_split_by_spatial_proximity` method

**Change:** Add column proximity checking (see code above)

---

## Questions for Business Owner

1. **Column Label Issue:** Are there formulas in the column headers (rows 1-20) in the Vietnam Plan file?

2. **Grouping Issue:** When you see `F4...BN13`, are F4 and BN13:
   - On the same row? (e.g., both row 4)
   - Or on different rows? (e.g., F4 and BN13)

3. **Context Format:** When you see `(うち利益剰余金) @ =J9+K19-12076`, is:
   - `うち利益剰余金` the row label?
   - `=J9+K19-12076` the column label?

This will help us pinpoint the exact issue!

---

**Next Steps:**
1. Business Owner reviews this code
2. Answers the questions above
3. We implement the fixes together
4. Re-test with Vietnam Plan file

---

**Prepared by:** Kiro AI Agent  
**Date:** December 2, 2025  
**Status:** AWAITING BUSINESS OWNER FEEDBACK
