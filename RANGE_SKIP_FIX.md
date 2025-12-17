# Range Skip Fix - Critical Bug

## Problem Identified

**From CSV Analysis:** Many risks have **EMPTY contexts** in the CSV export.

**Root Cause:** The code was **SKIPPING** compressed risks entirely!

```python
# OLD CODE - WRONG!
if ',' in risk.cell or '...' in risk.cell:
    continue  # Skip ranges completely - NO CONTEXT ADDED!
```

**Impact:**
- Compressed risks like `D5...K5`, `F8...BM8` were skipped
- They never got context labels
- They never triggered AI recovery
- Result: Empty contexts in CSV

**From CSV:**
```csv
Hidden Hardcode,High,計画書 円!D5...K5,,Hardcoded value '1000000' (8 instances)
Hidden Hardcode,High,プロジェクションVDN!F8...BM8,,Hardcoded value '201.26' (60 instances)
```

Notice the **empty Context column** (double comma `,,`)!

## Fix Applied

**Extract first cell from range for context lookup:**

```python
# NEW CODE - CORRECT!
# Handle compressed risks (ranges like "D5...K5")
# Extract first cell from range for context lookup
cell_for_context = risk.cell
if '...' in risk.cell:
    # Extract first cell from range "D5...K5" -> "D5"
    cell_for_context = risk.cell.split('...')[0]
elif ',' in risk.cell:
    # Extract first cell from list "E189, F189" -> "E189"
    cell_for_context = risk.cell.split(',')[0].strip()

# Get row and column labels (use first cell from range)
row_label, col_label = self._get_context_labels(risk.sheet, cell_for_context, cells)
```

**Logic:**
1. If risk is a range (`D5...K5`), extract first cell (`D5`)
2. Use first cell to look up context
3. Apply context to the entire range
4. Trigger AI if context is missing/poor

## Expected Behavior

**Before Fix:**
```csv
Hidden Hardcode,High,計画書 円!D5...K5,,Hardcoded value '1000000' (8 instances)
```
Context: **EMPTY** ❌

**After Fix:**
```csv
Hidden Hardcode,High,計画書 円!D5...K5,売上高,Hardcoded value '1000000' (8 instances)
```
Context: **売上高** (Revenue) ✓

**Or if AI recovery needed:**
```
[DEBUG] Row label missing for 計画書 円!D5...K5. Triggering AI.
[AI] Attempting recovery for 計画書 円!D5...K5
[AI] Context window for 計画書 円!D5:
  Left: ['売上高']
  Above: ['2022年度']
[AI] ✓ Recovered: '売上高'
```

## Log Output

**Expected:**
```
[VERBOSE] Risk #1: 計画書 円!D5...K5
[VERBOSE] Using first cell for context: D5
[VERBOSE] Row label after nuclear trim: 'None'
[DEBUG] Row label missing for 計画書 円!D5...K5. Triggering AI.
[AI] Attempting recovery for 計画書 円!D5...K5
[AI] ✓ Recovered: '売上高'

[DEBUG] Summary: 45 empty, 10 poor quality, 55 AI calls
[AI] Summary: 40/55 successful recoveries
```

## Key Changes

1. **Don't Skip Ranges** - Process them like any other risk
2. **Extract First Cell** - Use it for context lookup
3. **Apply to Entire Range** - Context applies to all cells in range
4. **Trigger AI** - If context is missing/poor for the range

## Files Modified

**src/analyzer.py:**
- Removed `continue` statement that skipped ranges
- Added logic to extract first cell from range
- Use `cell_for_context` for all context operations
- Added verbose logging for range handling

## Why This Matters

**From the CSV:** ~50% of risks are compressed ranges!

Without this fix:
- 50% of risks have NO context
- AI is never triggered for them
- User sees empty CSV columns

With this fix:
- ALL risks get context (or AI recovery attempt)
- Ranges use first cell for context lookup
- CSV is complete and useful

## Ready for UAT

This was the **critical missing piece**. The code was working correctly for individual cells, but skipping ranges entirely.

**Action:** Restart Streamlit and re-export CSV

```bash
streamlit run app.py
```

**Expected:** Context column should be filled for ALL risks, including ranges.

The gatekeeper wasn't just too permissive - it was **closed for ranges**! Now it's open. 🚪
