# Code Changes Detail - UAT Critical Fixes

## Overview

This document provides the exact code changes made to fix the UAT failures.

---

## Change 1: Context Type Filter in `src/analyzer.py`

### Location: `_get_context_labels()` method, lines ~450-500

### Problem
The original code checked `cell.value.startswith('=')` to detect formulas, but `cell.value` contains the RESULT of a formula, not the formula itself.

Example:
- Cell B5 formula: `=D18*E18`
- `cell.value`: `200` (the result)
- `cell.formula`: `=D18*E18` (the actual formula)

### Solution
Check `cell.formula` FIRST, before checking `cell.value`.

### Code Change

**BEFORE:**
```python
for check_col in range(col_num - 1, 0, -1):
    check_col_letter = get_column_letter(check_col)
    key = f"{sheet}!{check_col_letter}{row_num}"
    cell = cells.get(key)
    
    if cell and cell.value:
        value = cell.value
        
        if isinstance(value, str):
            value_str = value.strip()
            
            # WRONG: This only catches if value LOOKS like formula
            if value_str.startswith('='):
                continue
            
            if value_str:
                row_label = value_str
                break
```

**AFTER:**
```python
for check_col in range(col_num - 1, 0, -1):
    check_col_letter = get_column_letter(check_col)
    key = f"{sheet}!{check_col_letter}{row_num}"
    cell = cells.get(key)
    
    if cell:
        # CRITICAL: Check cell.formula FIRST
        if cell.formula:
            # This is a formula cell - REJECT and keep scanning
            continue
        
        # Now check the value
        if cell.value:
            value = cell.value
            
            if isinstance(value, str):
                value_str = value.strip()
                
                # Double-check: REJECT if starts with =
                if value_str.startswith('='):
                    continue
                
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
```

### Key Differences

1. **Check `cell.formula` first** - This is the critical fix
2. **Reject numbers** - Unless they're years (2020-2030)
3. **Keep scanning** - Don't stop at first cell, keep going until text found

---

## Change 2: Graph Labels in `app.py`

### Location: Dependency Tree visualization, lines ~600-650

### Problem
Graph nodes were created with generic labels, not using the context extraction logic.

### Solution
Use `analyzer._get_context_labels()` to get row/column context for each node.

### Code Change

**BEFORE:**
```python
for node in display_graph.nodes():
    if '!' in node:
        sheet, address = node.split('!')
        
        # Get cell info for context
        cell = model.cells.get(node)
        context = ""
        
        if cell:
            # TYPE FILTER: Only show TEXT values, not formulas
            if isinstance(cell.value, str) and not cell.value.startswith('='):
                # Truncate long text
                text = cell.value.strip()
                if len(text) > 15:
                    context = f": {text[:12]}..."
                elif text:
                    context = f": {text}"
            elif cell.formula:
                context = " (fx)"
        
        # Always show address + context
        label = f"{address}{context}"
    else:
        label = node
    
    agraph_nodes.append(Node(
        id=node,
        label=label,
        size=20,
        color="#4A90E2",
        font={'size': 14, 'color': '#000000'}
    ))
```

**AFTER:**
```python
for node in display_graph.nodes():
    if '!' in node:
        sheet, address = node.split('!')
        
        # Get cell info for context
        cell = model.cells.get(node)
        context = ""
        
        if cell:
            # Get row and column labels from analyzer
            row_label, col_label = analyzer._get_context_labels(sheet, address, model.cells)
            
            # Build context string
            if row_label:
                # Truncate long labels
                if len(row_label) > 20:
                    context = f": {row_label[:17]}..."
                else:
                    context = f": {row_label}"
            elif cell.formula:
                context = " (fx)"
        
        # Always show address + context
        label = f"{address}{context}"
    else:
        label = node
    
    agraph_nodes.append(Node(
        id=node,
        label=label,
        size=25,
        color="#4A90E2",
        font={'size': 16, 'color': '#000000', 'face': 'arial'}
    ))
```

### Key Differences

1. **Use `analyzer._get_context_labels()`** - Reuse the same logic
2. **Increased font size** - From 14px to 16px for better visibility
3. **Increased node size** - From 20 to 25 for better visibility
4. **Longer truncation** - From 12 chars to 17 chars

---

## Change 3: New Test File `tests/test_csv_export_validation.py`

### Purpose
Comprehensive end-to-end testing of CSV export to ensure no formulas appear in Context column.

### Test Cases

1. **test_csv_context_no_formulas** - Validates exact UAT scenario
   - Creates Excel with formulas in adjacent cells
   - Verifies Context contains text labels, NOT formulas
   - Checks for patterns like "=(", "=-", etc.

2. **test_csv_export_with_numbers_rejected** - Validates numbers are rejected
   - Creates Excel with numbers in adjacent cells
   - Verifies Context contains text labels, NOT numbers

3. **test_csv_export_empty_context_acceptable** - Validates empty is OK
   - Creates Excel with only formulas and numbers
   - Verifies Context can be empty if no text found
   - Ensures no formulas or numbers leak through

### Sample Test Code

```python
def test_csv_context_no_formulas(self):
    """CRITICAL: CSV Context column should NEVER contain formulas."""
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vietnam Plan"
    
    # Simulate Vietnam Plan layout
    ws['A18'] = '売上高'  # Text label
    ws['B18'] = '=D18*E18'  # Formula (should be IGNORED)
    ws['C18'] = '=100.5'  # Hardcoded value (will trigger risk)
    
    # Parse and analyze
    model = self.parser.parse(file_obj, 'vietnam.xlsx')
    model = self.analyzer.analyze(model, allowed_constants=[])
    
    # Convert to DataFrame (simulating CSV export)
    risk_data = []
    for risk in model.risks:
        risk_data.append({
            "Context": risk.get_context()
        })
    
    df = pd.DataFrame(risk_data)
    
    # CRITICAL VALIDATION: No formulas in Context
    for idx, row in df.iterrows():
        context = row['Context']
        assert not context.startswith('='), f"Context contains formula: {context}"
        assert '=(' not in context, f"Context contains formula pattern: {context}"
    
    # POSITIVE VALIDATION: Should find text labels
    contexts = df['Context'].tolist()
    assert any('売上高' in str(c) for c in contexts), "Should find '売上高' in context"
```

---

## Testing Strategy

### Unit Tests (8 tests)
- `test_reject_formulas_as_context` - Formulas are skipped
- `test_reject_numbers_as_context` - Numbers are skipped
- `test_accept_year_as_context` - Years are accepted
- `test_two_column_layout` - 2-column layouts work
- `test_vietnam_plan_scenario` - Exact UAT scenario

### Integration Tests (3 tests)
- `test_csv_context_no_formulas` - End-to-end CSV validation
- `test_csv_export_with_numbers_rejected` - Numbers rejected
- `test_csv_export_empty_context_acceptable` - Empty is OK

### Regression Tests (29 tests)
- All existing tests still pass
- No breaking changes

---

## Why This Fix Works

### The Root Cause

Excel cells have TWO properties:
1. `cell.formula` - The formula string (e.g., "=D18*E18")
2. `cell.value` - The calculated result (e.g., 200)

The original code only checked `cell.value.startswith('=')`, which would NEVER be true for formula cells because `cell.value` is the result, not the formula.

### The Solution

By checking `cell.formula` first, we correctly identify ALL formula cells, regardless of their calculated value.

This is a fundamental fix that addresses the root cause, not just the symptoms.

---

## Deployment Checklist

- [x] Code changes implemented
- [x] Unit tests written and passing
- [x] Integration tests written and passing
- [x] Regression tests passing
- [x] Real file verification passed
- [x] No syntax errors
- [x] No breaking changes
- [x] Documentation complete
- [ ] Business owner UAT approval
- [ ] Production deployment

---

**Developer:** Kiro AI Agent  
**Date:** 2025-12-02  
**Status:** READY FOR DEPLOYMENT (pending UAT approval)
