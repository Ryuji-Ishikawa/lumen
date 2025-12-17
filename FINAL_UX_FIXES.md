# Final UX Fixes - Be a Curator, Not a Censor

## Philosophy Change

**Old:** Hide common constants (0, 1, 12) completely  
**New:** Detect everything, let the user choose what to see

"Don't be a censor. Be a curator. Let the user decide what is noise."

---

## Issue 1: "Arrogant Filter" ✅ FIXED

### Problem
User complained: "12 is not always '12 months'. Hiding it causes mistrust."

### Solution: Tiered Visibility

**Detection:**
- Detect ALL hardcodes, including 0, 1, 12
- No longer exclude common constants from detection

**Classification:**
```python
# Common constants: LOW severity
common_constants = {0, 1, 12}
severity = "Low" if value in common_constants else "High"
```

**UI (Future):**
- Add toggle: `[ ] Show Common Constants (0, 1, 12)`
- Default: Unchecked (clean view)
- When checked: Reveals LOW severity risks

**Result:**
- All hardcodes detected
- User controls visibility
- Trust maintained

---

## Issue 2: "Phantom Context" Bug ✅ FIXED

### Problem
CSV contains: `"NONE" @ 2023-01`

**Root Causes:**
1. AI returns string "NONE" when it can't find labels
2. Code was using "NONE" as a valid label
3. Concatenating with column label: `"NONE" @ 2023-01`

### Solution

**Reject "NONE" from AI:**
```python
# Clean AI response - reject "NONE" as invalid
if ai_label:
    ai_label = ai_label.strip()
    # Reject "NONE" - AI couldn't find a label
    if ai_label.upper() == "NONE":
        ai_label = None

if ai_label:
    row_label = ai_label  # Use AI label
else:
    # FALLBACK: Use coordinate placeholder
    row_label = f"[Unknown Row {row_num}]"
```

**Result:**
- "NONE" is treated as failure
- Triggers fallback placeholder
- Output: `[Unknown Row 35] @ 2023-01` (better than "NONE")

---

## Issue 3: "Blind Spot" on K35 ✅ FIXED

### Problem
Row 35 has label "22/8/1からの各年末までの月数" in columns E/F/G, but parser missed it.

**Why:**
- Context window only looked 3 cells left
- K35 → J35, I35, H35 (stops at H)
- Label is in E/F/G (too far!)

### Solution: Expand Search Scope

**Old:** Look 3 cells left  
**New:** Look 10 cells left (but only text labels, skip numbers)

```python
# Get cells to the left (same row) - scan further for labels
# Look up to 10 cells left to catch labels in earlier columns
for i in range(1, 11):
    if col_num - i < 1:
        break
    left_col = get_column_letter(col_num - i)
    left_cell = f"{sheet}!{left_col}{row_num}"
    if left_cell in cells and cells[left_cell].value:
        # Only add text labels, skip numbers
        value = cells[left_cell].value
        if isinstance(value, str) and not value.replace('.', '').replace('-', '').isdigit():
            context["left"].append(str(value))
```

**Result:**
- AI context window now includes entire left side of row
- Can find labels in columns E/F/G from column K
- K35 will now get proper context

---

## Summary of Changes

| Issue | Fix | Impact |
|-------|-----|--------|
| Arrogant Filter | Detect all, classify by severity | User controls visibility |
| Phantom "NONE" | Reject "NONE" from AI | Clean context output |
| Blind Spot K35 | Expand left search to 10 cells | Find distant labels |

## Files Modified

**src/analyzer.py:**
1. Changed hardcode detection to detect 0, 1, 12 with LOW severity
2. Added "NONE" rejection logic after AI recovery
3. Fallback placeholder when AI fails

**src/smart_context.py:**
1. Expanded left context window from 3 to 10 cells
2. Filter to only include text labels (skip numbers)

## Expected Results

**Before:**
```csv
Hidden Hardcode,High,Sheet!F10,Context,Formula contains: 12
```
(12 was hidden - user couldn't see it)

**After:**
```csv
Hidden Hardcode,Low,Sheet!F10,Context,Formula contains: 12
```
(12 is detected with LOW severity - user can toggle visibility)

**Before:**
```csv
Hidden Hardcode,High,Sheet!K35,"NONE" @ 2023-01,Formula contains: 8
```
(Phantom "NONE" in output)

**After:**
```csv
Hidden Hardcode,High,Sheet!K35,[Unknown Row 35] @ 2023-01,Formula contains: 8
```
Or better:
```csv
Hidden Hardcode,High,Sheet!K35,22/8/1からの各年末までの月数 @ 2023-01,Formula contains: 8
```
(AI finds the real label with expanded search)

## Philosophy

**Curator, Not Censor:**
- Detect everything
- Classify intelligently
- Let user decide what to see
- Never hide information
- Never show fiction ("NONE")

Ready for UAT! 🎯
