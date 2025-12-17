# Phase 7.5: Japanese Localization & Logic Fixes

## Status: PARTIALLY COMPLETE

### Completed Fixes ✅

#### 1. UI Terminology (Japanese Localization)

**File: `app.py` (lines ~765-800)**

**Changes:**
- "Top 3 Most Dangerous Hardcodes" → "最も危険なベタ打ち数値 Top 3"
- "Diffusion" → "出現箇所数"
- "Dominance" → "影響セル数"
- "423x" → "423箇所"
- "locations affected" → "箇所で使用"
- "Show all locations" → "すべての場所を表示"
- "KPI Impact: YES" → "KPI影響: あり"
- "KPI Impact: No" → "KPI影響: なし"

**Before:**
```
Diffusion: 423x
Dominance: 150
```

**After:**
```
出現箇所数: 423箇所
影響セル数: 150
```

### Remaining Fixes ⚠️

#### 2. AI Naming Logic (Labeling Fallacy Prevention)

**Problem:** AI suggests naming 201.26 as "Total Development Cost" because it first appears in that row, but it's actually an FX rate appearing 423 times.

**Required Fix in `src/ai_explainer.py`:**

```python
def _build_breakdown_prompt(self, context: MaskedContext, driver_cells: List[str]) -> str:
    labels = context.cell_labels
    row_label = labels.get('row_label', '不明')
    
    # Extract metrics
    diffusion = labels.get('diffusion', 0)
    affected_locations = labels.get('affected_locations', 1)
    
    # CRITICAL: Detect global parameters
    is_global_param = diffusion > 3
    
    if is_global_param:
        prompt = f"""
【グローバルパラメータ検出】
⚠️ この値は{diffusion}箇所で使用されています。
これはグローバルパラメータ（為替レート、税率など）の可能性が高いです。

❌ 禁止: 最初の行ラベル「{row_label}」をパラメータ名として使用しないこと

✅ 推奨:
1. ユーザーに確認: 「この値は何を表していますか？」
2. 汎用名を提案: 「Param_{actual_value}」
3. 具体的な名前は避ける
"""
    else:
        # Local parameter - can use row label
        prompt = f"""
【ローカルパラメータ】
- 行ラベル: {row_label}
（この値は局所的なので、行ラベルを使用可能）
"""
```

**Impact:**
- Prevents AI from suggesting "開発費_201.26" when it's actually an FX rate
- Forces AI to ask user what the value represents
- Suggests generic names like "Param_201.26" for global values

#### 3. Recursive Impact Calculation

**Problem:** Tool reports "1 dependent cell" for FX rate, which is impossible if it appears 423 times.

**Root Cause:** `get_dependents()` may not be calculating recursive blast radius correctly.

**Required Fix in `src/analyzer.py`:**

```python
def _calculate_dominance(self, model: ModelAnalysis, cell_address: str) -> int:
    """
    Count ALL dependent cells (children + grandchildren + ...).
    
    CRITICAL: This must be RECURSIVE, not just direct children.
    """
    if cell_address not in model.dependency_graph:
        return 0
    
    try:
        # Get ALL descendants (recursive)
        descendants = nx.descendants(model.dependency_graph, cell_address)
        return len(descendants)
    except:
        return 0
```

**Validation:**
- For 201.26 appearing 423 times, dominance should be >> 1
- If dominance is still 1, the dependency graph may be broken
- Add fallback message: "影響: 測定不可（ベタ打ち修正が必要）"

**Fallback Display Logic:**

```python
if dominance <= 1 and diffusion > 10:
    # Suspicious: high diffusion but low dominance
    st.warning("⚠️ 影響セル数が測定できません。モデルがLevel 1（静的）の可能性があります。")
    st.caption("ベタ打ち値を修正すると、正確な影響範囲が計算できます。")
```

## Implementation Priority

### High Priority (Immediate)
1. ✅ UI Terminology - DONE
2. ⚠️ AI Naming Logic - NEEDS IMPLEMENTATION
3. ⚠️ Dominance Validation - NEEDS VERIFICATION

### Medium Priority
- Add terminology glossary to UI
- Add help tooltips explaining metrics
- Validate dependency graph construction

## Testing Checklist

- [ ] Upload Vietnam Plan Excel file
- [ ] Verify 201.26 shows as "出現箇所数: 423箇所"
- [ ] Verify AI doesn't suggest "開発費" as parameter name
- [ ] Verify AI asks "この値は何を表していますか？"
- [ ] Verify dominance > 1 for widespread values
- [ ] If dominance = 1, verify fallback message appears

## Code Locations

### Files to Update
1. `app.py` (lines ~765-800) - ✅ DONE
2. `src/ai_explainer.py` (lines ~262-290, ~382-410) - ⚠️ NEEDS UPDATE
3. `src/analyzer.py` (lines ~1270-1290) - ⚠️ NEEDS VERIFICATION

### Search Patterns
```bash
# Find AI prompt sections
grep -n "グローバルコンテキスト" src/ai_explainer.py

# Find dominance calculation
grep -n "def _calculate_dominance" src/analyzer.py

# Find UI metric displays
grep -n "st.metric.*Diffusion" app.py
```

## Business Impact

### Before Fixes
- ❌ "Diffusion" confuses Japanese users
- ❌ AI suggests wrong names (e.g., "開発費" for FX rate)
- ❌ Impact shows "1 cell" when it should be hundreds

### After Fixes
- ✅ "出現箇所数" is clear to Japanese users
- ✅ AI asks user to clarify global parameters
- ✅ Impact shows realistic numbers or explains why it can't

## Next Steps

1. **Complete AI Naming Logic Fix**
   - Update both OpenAIProvider and GoogleProvider
   - Add `is_global_param` detection
   - Add constraint prompts

2. **Verify Dominance Calculation**
   - Check if `nx.descendants()` is working correctly
   - Add logging to see actual descendant counts
   - Add fallback for broken dependency graphs

3. **Add Validation Tests**
   - Test with Vietnam Plan (201.26 case)
   - Verify AI output doesn't use local labels
   - Verify dominance matches expected values

## Notes

- The UI terminology fix is complete and working
- The AI naming logic requires careful prompt engineering
- The dominance calculation may need dependency graph debugging
- All fixes target the same goal: accurate, understandable risk assessment for Japanese business users
