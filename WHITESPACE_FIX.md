# Whitespace Fix - "Silent Bug"

## Problem Identified

**UAT Feedback:** "The Context column in the CSV is still largely EMPTY."

**Root Cause:** The parser was extracting whitespace (spaces, newlines, tabs) and treating it as "valid", so it never triggered AI recovery.

**Log showed:** `[DEBUG] Summary: 0 empty, 0 poor quality, 0 AI calls`  
**Reality:** Many contexts were whitespace-only, counted as "valid"

## Fix Applied

### 1. Strict Whitespace Cleaning

**In `_get_context_labels()`:**

```python
if isinstance(value, str):
    # STRICT WHITESPACE CLEANING: Zero tolerance for silence
    value_str = value.strip()
    
    # REJECT empty strings after strip (whitespace-only cells)
    if not value_str:
        continue  # Keep scanning left
    
    # ACCEPT non-empty text
    row_label = value_str
    break
```

**Applied to 3 locations:**
- Row label extraction (scanning left)
- Row label extraction (checking above)
- Column label extraction (scanning rows 1-20)

### 2. Aggressive AI Trigger for Empty

**In `_add_context_labels()`:**

```python
# STRICT WHITESPACE CLEANING: Treat empty strings as None
if row_label and not row_label.strip():
    row_label = None

# Check if context is missing OR poor quality
is_empty = not row_label or row_label == ""

# AGGRESSIVE AI TRIGGER: Empty OR poor quality
if self.smart_context and self.smart_context.enabled and (is_empty or is_poor):
    ai_calls += 1
    print(f"[AI] Attempting recovery for {risk.sheet}!{risk.cell}")
    # ... AI recovery logic
```

### 3. Fallback Mechanism

**When AI fails:**

```python
if not row_label or row_label == "":
    # Extract row number from cell address
    row_match = re.match(r'^[A-Z]+(\d+)$', risk.cell)
    if row_match:
        row_num = row_match.group(1)
        row_label = f"[Unknown Row {row_num}]"
        print(f"[FALLBACK] Using coordinate placeholder: '{row_label}'")
```

**Result:** Better to show `[Unknown Row 24]` than a blank cell

## Test Results

Created `test_whitespace_fix.py` with 11 test cases:

**Whitespace Rejection Tests:**
- ✅ Spaces only: `"   "` → Rejected
- ✅ Newline only: `"\n"` → Rejected
- ✅ Tab only: `"\t"` → Rejected
- ✅ Mixed whitespace: `"  \n  "` → Rejected
- ✅ Empty string: `""` → Rejected

**Context Label Tests:**
- ✅ Whitespace-only cells → Empty (triggers AI)
- ✅ Good labels → Accepted

**Fallback Test:**
- ✅ Empty context + failed AI → `[Unknown Row 92]`

**Result: 11/11 tests passed ✅**

## Expected Behavior

When you run the app with "Vietnam Plan":

```
[DEBUG] _add_context_labels called with X risks

[VERBOSE] Risk #1: BS!E92
[VERBOSE] Raw label from parser: 'None'
[VERBOSE] Label is empty or whitespace-only
[AI] Attempting recovery for BS!E92
[AI] Context window for BS!E92:
  Left: []
  Above: ['Balance Sheet', 'Current Assets']
[AI] ✓ Recovered: 'Cash Balance'

[VERBOSE] Risk #2: BS!F24
[VERBOSE] Raw label from parser: '   '
[VERBOSE] Label is empty or whitespace-only
[AI] Attempting recovery for BS!F24
[AI] ✗ Recovery failed
[FALLBACK] Using coordinate placeholder: '[Unknown Row 24]'

[DEBUG] Summary: 15 empty, 5 poor quality, 20 AI calls
[AI] Summary: 12/20 successful recoveries
```

## Key Changes

1. **Zero Tolerance for Silence**
   - Whitespace-only values are treated as `None`
   - Empty strings after `.strip()` are rejected immediately

2. **Aggressive AI Trigger**
   - Empty contexts trigger AI immediately
   - No risk passes with empty context

3. **Fallback Mechanism**
   - If AI fails, inject `[Unknown Row X]` placeholder
   - User can at least find the cell in the spreadsheet

## Files Modified

1. **src/analyzer.py**
   - Enhanced `_get_context_labels()` with strict whitespace rejection (3 locations)
   - Updated `_add_context_labels()` with empty string detection
   - Added fallback placeholder mechanism

2. **test_whitespace_fix.py** (NEW)
   - Comprehensive test suite for whitespace handling
   - 11 test cases covering all scenarios

## Ready for UAT

The "Silent Bug" is fixed. Whitespace will no longer masquerade as valid context.

**Expected Log:** `X empty contexts detected, X AI calls triggered`

**Action:** Restart Streamlit and test with "Vietnam Plan"

```bash
streamlit run app.py
```

The map is no longer blank. 🗺️
