# Final Fix Summary - Phase 7.5

## What Was Fixed ✅

### Issue: Dominance Showing "1" for Widespread Values

**Root Cause:** Hardcoded values (like `201.26`) don't create dependencies in the Excel graph. The parser only tracks formula references like `=F4`, not static values like `201.26`.

**Solution Implemented:**
- Detect when diffusion > 10 but dominance < 5 (hardcoded scattered values)
- Show "測定不可" (unmeasurable) instead of misleading "1"
- Display warning explaining why and how to fix it

### Changes in `app.py` (lines ~785-810)

**Before:**
```
影響セル数: 1  ❌ Misleading
```

**After:**
```
影響セル数: 測定不可  ✅ Honest

⚠️ 影響範囲を測定できません

この値は423箇所でベタ打ちされているため、
依存関係が追跡できていません。

推奨対策: この値を前提条件シートに移動し、
数式で参照してください。
```

## Why This Happens

### Dependency Graph Limitation

Excel dependency graphs only track **formula references**, not **values**:

| Cell | Content | Dependencies Tracked? |
|------|---------|----------------------|
| A1: `=B1+C1` | Formula | ✅ YES (B1, C1) |
| B1: `201.26` | Hardcoded | ❌ NO |
| C1: `201.26` | Hardcoded | ❌ NO |

**Result:** 423 cells with `201.26` have NO tracked dependencies between them.

### This Actually Validates the Maturity Model!

- **High Diffusion** (423) = Value is scattered
- **Low Dominance** (1) = No formula connections
- **Conclusion**: Model is **Level 1 (Static)** ✅

This proves the user needs to:
1. Centralize the value
2. Convert to formula references
3. Then dominance becomes measurable

## What Users Will See Now

### For Value 201.26

```
┌─────────────────────────────────────────────────┐
│ #1: 値 '201.26' (8箇所で使用)                    │
├─────────────────────────────────────────────────┤
│ 出現箇所数: 423箇所                              │
│ 影響セル数: 測定不可  ⚠️                         │
│ 深刻度: High                                     │
│ KPI影響: なし                                    │
├─────────────────────────────────────────────────┤
│ ⚠️ 影響範囲を測定できません                      │
│                                                  │
│ この値は423箇所でベタ打ちされているため、        │
│ 依存関係が追跡できていません。                   │
│                                                  │
│ 推奨対策: この値を前提条件シートに移動し、       │
│ 数式で参照してください。                         │
│ そうすることで、正確な影響範囲                   │
│ （推定423セル以上）が計算できます。              │
└─────────────────────────────────────────────────┘
```

## Remaining Issue: AI Naming

The AI still suggests "全体開発費" because `src/ai_explainer.py` hasn't been updated yet.

**Manual fix required:**
1. Open `src/ai_explainer.py`
2. Find lines 269 and 389
3. Add global parameter detection (see `CRITICAL_FIXES_APPLIED.md`)

## Testing

```bash
streamlit run app.py
# Upload Vietnam Plan
# Check value 201.26
# Should see: "影響セル数: 測定不可"
# Should see: Warning message explaining why
```

## Business Impact

### Before Fix
- ❌ Shows "1個の依存セル" (misleading)
- ❌ User thinks impact is small
- ❌ Doesn't understand the real problem

### After Fix
- ✅ Shows "測定不可" (honest)
- ✅ Explains why (hardcoded values)
- ✅ Recommends solution (centralize)
- ✅ Validates maturity model (Level 1)

## Summary

**Fixed:** Dominance display for hardcoded values
**Status:** ✅ COMPLETE
**Files:** `app.py` (lines ~785-810)
**Remaining:** AI naming logic in `src/ai_explainer.py` (manual update needed)

The fix turns a confusing "1" into an educational moment that explains the core problem and guides the user toward the solution.
