# Remaining Issues - Post Context Fill

## Status: Contexts Now Filled ✅

Good news: All contexts are now being filled (no more empty columns in CSV).

## Issues Identified

### Issue 1: Date Format Pollution ✅ FIXED

**Problem:**
```
バイク製造費（百万VDN） @ 2022-08-01 00:00:00
システム維持コスト @ 2025-09-01 00:00:00
```

**Root Cause:** openpyxl converts date cells to Python `datetime` objects. When we call `str(cell.value)`, it outputs the full datetime string.

**Fix Applied:**
```python
# Handle datetime objects - convert to simple date format
from datetime import datetime
if isinstance(cell.value, datetime):
    # Format as YYYY-MM for column headers
    value_str = cell.value.strftime('%Y-%m')
else:
    value_str = str(cell.value).replace('\u3000', ' ').strip()
```

**Expected Output:**
```
バイク製造費（百万VDN） @ 2022-08
システム維持コスト @ 2025-09
```

Much cleaner! ✓

---

### Issue 2: Missing Hardcoded Values ⚠️ PARSER ISSUE

**Problem:**
```
計画書VNDコピー!G26...J26
Raw data:
  G26: =100630*0.02*5/12
  H26: =100630*0.02
  I26: =100630*0.02

Description: "Hardcoded value '100630' (4 instances)"
```

But J26 is missing! Should be 4 instances, not 3.

**Root Cause:** This is a **parser/tokenizer issue**, not a context issue. The hardcode detection in `_detect_hidden_hardcodes()` might be:
1. Missing some formulas
2. Not tokenizing correctly
3. Skipping certain cells

**Recommendation:**
- Check if J26 cell exists in the parsed cells
- Verify the formula tokenizer is catching all NUMBER tokens
- This is separate from the context labeling work

**Not Critical:** The detection is working for most cases. This is a refinement issue.

---

### Issue 3: AI Hallucination 🚨 CRITICAL

**Problem:**
```
プロジェクション円!K35, "年間収入" @ 2023-01-01 00:00:00, Hardcoded value '8'
```

But there is **NO "年間収入" in the sheet**!

**Root Cause:** The AI is **making up context** when it can't find real labels.

**Why This Happens:**
1. The AI prompt asks it to "provide a meaningful label"
2. When the AI can't find evidence, it **guesses** based on the cell value
3. The AI sees a number `8` and invents a plausible-sounding label

**This is DANGEROUS** because:
- Users will trust the context
- But it's fiction, not fact
- Leads to incorrect analysis

**Recommended Fix:**

Update the AI prompt to be more conservative:

```python
# CURRENT PROMPT (too creative)
Task: Look at the surrounding cells and provide a meaningful, specific label.

# BETTER PROMPT (more conservative)
Task: Look at the surrounding cells. If you find a clear text label, return it.
If you cannot find a clear label in the surrounding cells, return "NONE".

CRITICAL: Only return labels that actually exist in the surrounding cells.
Do NOT invent or guess labels based on the cell value.
Do NOT make assumptions about what the data might represent.

If uncertain, return "NONE".
```

**Alternative Approach:**
- Disable AI for cells with no surrounding context
- Use fallback placeholder `[Unknown Row X]` instead
- Better to show "Unknown" than fiction

**Action Required:**
1. Update `_build_context_prompt()` in `smart_context.py`
2. Add explicit instruction: "Do NOT invent labels"
3. Test with cells that have no nearby labels
4. Verify AI returns "NONE" when it should

---

## Summary

| Issue | Status | Severity | Action |
|-------|--------|----------|--------|
| Date format pollution | ✅ Fixed | Low | Applied datetime formatting |
| Missing hardcoded values | ⚠️ Parser issue | Low | Separate investigation needed |
| AI hallucination | 🚨 Critical | High | Update AI prompt immediately |

## Next Steps

1. **Immediate:** Fix AI hallucination by updating prompt
2. **Soon:** Investigate missing hardcode detection
3. **Test:** Re-run with Vietnam Plan and verify:
   - Dates are clean (YYYY-MM format)
   - AI doesn't invent context
   - Fallback placeholders used when appropriate

## Files Modified

**src/analyzer.py:**
- Added datetime handling for column labels
- Converts `datetime` objects to `YYYY-MM` format

**Needs Update:**
- `src/smart_context.py` - Update `_build_context_prompt()` to prevent hallucination
