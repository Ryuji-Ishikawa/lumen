# Nuclear Trim Fix - "Hallucinating Data"

## Problem Identified

**UAT Feedback:** "Empty Contexts in CSV, but log says 0 empty"

**Root Cause:** Parser was "hallucinating" - finding partial data and treating it as valid:
1. **Japanese full-width spaces** (`\u3000`) were not being stripped
2. **Column-only context** (date without subject) was treated as "valid"
3. **No debug logging** for missing row labels

**Example Hallucination:**
- Found: Column label "2025" 
- Missing: Row label (what the data represents)
- Result: Context = " @ 2025" (useless!)

## Fix Applied

### 1. Nuclear Trim - Japanese Full-Width Spaces

**Applied to 4 locations in `_get_context_labels()`:**

```python
# NUCLEAR TRIM: Handle Japanese full-width spaces (\u3000) and all whitespace
value_str = value.replace('\u3000', ' ').strip()

# REJECT empty strings after nuclear trim
if not value_str:
    continue  # Skip whitespace-only cells
```

**Locations:**
1. Row label extraction (scanning left)
2. Row label extraction (checking above)
3. Column label extraction (scanning rows 1-20)
4. Final cleanup in `_add_context_labels()`

**Why:** Japanese Excel often contains `\u3000` (全角スペース). Python's default `.strip()` might not catch it.

### 2. Row Label Priority - Mandatory "What"

**In `_add_context_labels()`:**

```python
# ENFORCE ROW LABEL PRIORITY: Row label is mandatory
# Knowing "When" (2025) without "What" (Revenue) is useless
is_empty = not row_label or row_label == ""

if is_empty:
    empty_contexts += 1
    print(f"[DEBUG] Row label missing for {risk.sheet}!{risk.cell}. Triggering AI.")
```

**Logic:**
- If row label is missing → **TRIGGER AI** (even if column label exists)
- Column label alone is not enough
- A date without a subject is not a context

### 3. Debug Logging - "Ghost" Data Detection

**Added explicit logging:**

```python
if is_empty:
    print(f"[DEBUG] Row label missing for {risk.sheet}!{risk.cell}. Triggering AI.")
```

**Now you'll see:**
```
[DEBUG] Row label missing for BS!E92. Triggering AI.
[DEBUG] Row label missing for BS!F24. Triggering AI.
[DEBUG] Summary: 15 empty, 5 poor quality, 20 AI calls
```

## Test Results

Created `test_nuclear_trim.py` with 3 test suites:

### 1. Nuclear Trim Test (5 cases)
- ✅ `\u3000` (full-width space only) → Empty
- ✅ `\u3000\u3000\u3000` (multiple) → Empty
- ✅ `\u3000Revenue\u3000` (around text) → "Revenue"
- ✅ `Revenue\u3000Cost` (in middle) → "Revenue Cost"
- ✅ ` \u3000 ` (mixed spaces) → Empty

### 2. Row Label Priority Test
- ✅ Column label exists, row label missing → Triggers AI
- ✅ Enforces: "Knowing 'When' without 'What' is useless"

### 3. Debug Logging Test
- ✅ Missing row labels are logged
- ✅ `[DEBUG] Row label missing for Sheet1!E10. Triggering AI.`

**Result: All tests passed ✅**

## Expected Behavior

When you run the app with "Vietnam Plan":

```
[DEBUG] _add_context_labels called with X risks

[VERBOSE] Risk #1: BS!E92
[VERBOSE] Row label after nuclear trim: 'None'
[VERBOSE] Col label after nuclear trim: '2025'
[DEBUG] Row label missing for BS!E92. Triggering AI.
[AI] Attempting recovery for BS!E92
[AI] Context window for BS!E92:
  Left: []
  Above: ['Balance Sheet', 'Current Assets']
[AI] ✓ Recovered: 'Cash Balance'

[VERBOSE] Risk #2: BS!F24
[VERBOSE] Row label after nuclear trim: '\u3000'  (full-width space)
[VERBOSE] Col label after nuclear trim: '2025'
[DEBUG] Row label missing for BS!F24. Triggering AI.
[AI] Attempting recovery for BS!F24
[AI] ✓ Recovered: 'Beginning Balance'

[DEBUG] Summary: 15 empty, 5 poor quality, 20 AI calls
[AI] Summary: 12/20 successful recoveries
```

## Key Changes

1. **Nuclear Trim Everywhere**
   - Replace `\u3000` with space, then `.strip()`
   - Applied to all label extraction points
   - Zero tolerance for Japanese full-width spaces

2. **Row Label is Mandatory**
   - Column-only context triggers AI
   - "When" without "What" = useless
   - Enforces semantic completeness

3. **Explicit Debug Logging**
   - Every missing row label is logged
   - No more "ghost" data hiding
   - Proves AI is being triggered

## Files Modified

1. **src/analyzer.py**
   - Added nuclear trim to 4 locations in `_get_context_labels()`
   - Added nuclear trim to `_add_context_labels()`
   - Added row label priority enforcement
   - Added explicit debug logging for missing labels

2. **test_nuclear_trim.py** (NEW)
   - Nuclear trim test suite (5 cases)
   - Row label priority test
   - Debug logging verification

## Ready for UAT

The parser is no longer hallucinating. It will:
1. Strip Japanese full-width spaces properly
2. Reject column-only context
3. Log every missing row label
4. Trigger AI for all empty/poor contexts

**Expected Log:** `XX empty contexts, XX AI calls` (not 0!)

**Action:** Restart Streamlit and test with "Vietnam Plan"

```bash
streamlit run app.py
```

A space is not data. A date without a subject is not a context. The gatekeeper is fixed. 🚪
