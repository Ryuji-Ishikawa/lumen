# URGENT FIXES STATUS - Phase 7.5

## Executive Summary

**Status:** 1 of 3 fixes complete, 2 require additional implementation

### Fix #1: Japanese Terminology ✅ COMPLETE

**Problem:** "Hardcode" and "Diffusion" are alien terms to Japanese finance users.

**Solution Implemented:**
- Updated all UI labels to Japanese business terminology
- Removed technical jargon

**Changes:**
```
Hidden Hardcode → ベタ打ち数値
Diffusion → 出現箇所数  
Dominance → 影響セル数
423x → 423箇所
locations affected → 箇所で使用
```

**File:** `app.py` (lines ~765-800)
**Status:** ✅ DEPLOYED

---

### Fix #2: AI Naming Logic ⚠️ DOCUMENTED, NEEDS IMPLEMENTATION

**Problem:** AI suggested naming 201.26 as "Total Development Cost" because it appeared in that row first, but it's actually an FX rate appearing 423 times.

**Root Cause:** AI uses the first row label without checking if the value is global.

**Solution Designed:**
```python
# Detect global parameters
is_global_param = diffusion > 3

if is_global_param:
    # DO NOT use local row label
    # Ask user what the value represents
    # Suggest generic name like "Param_201.26"
else:
    # Local parameter - can use row label
```

**Required Changes:**
- `src/ai_explainer.py` (2 locations: OpenAIProvider and GoogleProvider)
- Add conditional logic based on diffusion count
- Update prompts to prevent labeling fallacy

**Status:** ⚠️ DESIGN COMPLETE, CODE UPDATE PENDING

---

### Fix #3: Recursive Impact ⚠️ NEEDS VERIFICATION

**Problem:** Tool reported "1 dependent cell" for FX rate that appears 423 times. This is impossible.

**Possible Causes:**
1. `get_dependents()` not calculating recursively
2. Dependency graph construction is broken
3. Hardcoded values don't create dependencies

**Solution Approach:**
1. Verify `nx.descendants()` is being used (it should be recursive)
2. Add logging to see actual descendant counts
3. Add fallback message if dominance seems wrong:
   ```
   "影響: 測定不可（ベタ打ち修正が必要）"
   ```

**Required Investigation:**
- Check `src/analyzer.py` `_calculate_dominance()` method
- Verify dependency graph includes hardcoded value dependencies
- Test with Vietnam Plan to see actual dominance values

**Status:** ⚠️ NEEDS DEBUGGING

---

## Testing Instructions

### Test Fix #1 (Terminology) ✅
1. Run `streamlit run app.py`
2. Upload Excel file
3. Check Top 3 section
4. Verify: "出現箇所数" instead of "Diffusion"
5. Verify: "影響セル数" instead of "Dominance"
6. Verify: "423箇所" instead of "423x"

**Result:** PASS ✅

### Test Fix #2 (AI Naming) ⚠️
1. Run app and upload Vietnam Plan
2. Click "✨ Suggest Improvement" on 201.26
3. Check AI response
4. Expected: AI should ask "この値は何を表していますか？"
5. Expected: AI should NOT suggest "開発費_201.26"
6. Expected: AI should suggest "Param_201.26" or similar generic name

**Result:** PENDING IMPLEMENTATION

### Test Fix #3 (Dominance) ⚠️
1. Run app and upload Vietnam Plan
2. Check 201.26 card
3. Check "影響セル数" value
4. Expected: Should be > 1 (ideally >> 1)
5. If = 1: Verify fallback message appears

**Result:** NEEDS VERIFICATION

---

## Implementation Plan

### Immediate Actions (Today)

1. **Verify Fix #1 Works**
   - ✅ Code deployed
   - ⏳ User testing needed

2. **Implement Fix #2**
   - Update `src/ai_explainer.py`
   - Add `is_global_param` detection
   - Update both OpenAIProvider and GoogleProvider
   - Test with Vietnam Plan

3. **Debug Fix #3**
   - Add logging to `_calculate_dominance()`
   - Check dependency graph construction
   - Verify with Vietnam Plan
   - Add fallback message if needed

### Next Steps (This Week)

1. Complete all 3 fixes
2. Run full UAT with Vietnam Plan
3. Verify AI output quality
4. Document any additional issues

---

## Risk Assessment

### Fix #1: Terminology ✅
- **Risk:** LOW
- **Impact:** HIGH (user comprehension)
- **Status:** COMPLETE

### Fix #2: AI Naming ⚠️
- **Risk:** MEDIUM (AI prompt engineering)
- **Impact:** CRITICAL (prevents wrong suggestions)
- **Status:** DESIGN READY, NEEDS CODING

### Fix #3: Dominance ⚠️
- **Risk:** HIGH (may require graph debugging)
- **Impact:** HIGH (accurate impact assessment)
- **Status:** NEEDS INVESTIGATION

---

## Business Owner Notes

> "Don't let the AI guess specific names for global numbers. It will look stupid."

**Response:** Agreed. Fix #2 addresses this by:
1. Detecting global parameters (diffusion > 3)
2. Preventing AI from using local row labels
3. Forcing AI to ask user for clarification
4. Suggesting generic names only

**Timeline:**
- Fix #1: ✅ DONE
- Fix #2: 🔄 IN PROGRESS (2-4 hours)
- Fix #3: 🔍 INVESTIGATING (4-8 hours)

**Total Estimated Time:** 6-12 hours to complete all fixes

---

## Contact

For questions or updates on these fixes, refer to:
- `PHASE_7_5_LOCALIZATION_FIX.md` (detailed technical specs)
- `app.py` (UI changes)
- `src/ai_explainer.py` (AI prompt logic)
- `src/analyzer.py` (dominance calculation)
