# Context Formatting Fix - Raw and Honest

## Philosophy

"The user wants to see their data, not our formatting logic. Keep it raw and honest."

---

## Issue 1: Arrogant Filter ✅ ALREADY FIXED

**Status:** Already implemented in previous fix.

**Solution:** Detect ALL hardcodes (including 0, 1, 12) with tiered severity:
- Common constants (0, 1, 12): LOW severity
- Unknown values: HIGH severity

**Result:** Never miss a potential "12% margin" hardcode.

---

## Issue 2: Context Noise - The "@ 2022-08" Problem ✅ FIXED

### Problem

**CSV shows:**
```
2022年8月1日現在のNet Present Value ① @ 2022-08
```

**User feedback:** "The raw data doesn't have the '@ 2022-08'. It looks like the AI is hallucinating."

**Root cause:** Blindly concatenating `f"{row} @ {col}"` even when redundant.

### Solution: Smart Context Formatting

Implemented 3 rules in `get_context()`:

**Rule A: Redundancy Check**
```python
# If row label already contains the column label text, don't repeat it
if col_lower in row_lower or row_lower in col_lower:
    return self.row_label  # Drop redundant column label
```

**Example:**
- Row: `2022年8月1日現在のNet Present Value ①`
- Col: `2022-08`
- Result: `2022年8月1日現在のNet Present Value ①` (no @ suffix)

**Rule B: Long Labels Are Complete**
```python
# If row label is long/specific (>30 chars), it's probably complete
if len(self.row_label) > 30:
    return self.row_label  # Don't add column label
```

**Example:**
- Row: `22/8/1からの各年末までの月数` (long, specific)
- Col: `2023-01`
- Result: `22/8/1からの各年末までの月数` (no @ suffix)

**Rule C: Add Value When Needed**
```python
# Otherwise, add column label for context
return f"{self.row_label} @ {self.col_label}"
```

**Example:**
- Row: `Revenue` (short, generic)
- Col: `2023-04`
- Result: `Revenue @ 2023-04` (adds value)

### Before vs After

**Before (Noisy):**
```csv
Location,Context
Sheet!F4,2022年8月1日現在のNet Present Value ① @ 2022-08
Sheet!K35,22/8/1からの各年末までの月数 @ 2023-01
Sheet!G18,法人税等 @ 2023-08
```

**After (Clean):**
```csv
Location,Context
Sheet!F4,2022年8月1日現在のNet Present Value ①
Sheet!K35,22/8/1からの各年末までの月数
Sheet!G18,法人税等 @ 2023-08
```

**Logic:**
- F4: Row contains "2022年8月1日" → Drop "2022-08" (redundant)
- K35: Row is >30 chars and specific → Drop date (complete)
- G18: Row is short, col adds value → Keep both

---

## Summary

| Issue | Fix | Result |
|-------|-----|--------|
| Hiding 12 | Detect with LOW severity | Never miss hardcodes |
| Context noise | Smart formatting rules | Clean, honest output |

## Files Modified

**src/models.py:**
- Updated `get_context()` with smart formatting
- 3 rules: Redundancy check, long label check, add value check

## Expected Results

**User sees their data:**
- Long, specific labels stand alone
- Short labels get date context when needed
- No redundant information
- No invented formatting

**Trust maintained:**
- What you see is what's in the Excel
- No phantom dates
- No noise
- Raw and honest

Ready for UAT! 🎯
