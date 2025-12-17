# Phase 7.2: Impact Scoring & Prescription Templates - COMPLETE ✅

**Status**: ✅ IMPLEMENTATION COMPLETE  
**Date**: December 3, 2025  
**Priority**: CRITICAL LOGIC UPGRADE

---

## Executive Summary

Implemented data-driven "Impact Scoring" system that calculates three metrics (Diffusion, Dominance, Volatility) and automatically selects the appropriate prescription template. The AI no longer guesses - it receives calculated metrics and specific instructions.

---

## Implementation Complete

### ✅ Task 1: Impact Score Calculation (analyzer.py)

**Added Methods**:

1. **`calculate_impact_score(model, cell_address, hardcoded_value)`**
   - Orchestrates all three metric calculations
   - Returns dict with diffusion, dominance, volatility, prescription_mode

2. **`_calculate_diffusion(model, hardcoded_value)`**
   - Counts occurrences across entire workbook
   - Example: Value "0.3" appears 5 times → diffusion = 5

3. **`_calculate_dominance(model, cell_address)`**
   - Uses NetworkX to count all descendants
   - Example: Cell has 242 dependent cells → dominance = 242

4. **`_calculate_volatility(model, cell_address)`**
   - Checks if same row has 3+ different hardcoded values
   - Returns "High" or "Low"

5. **`_determine_prescription_mode(diffusion, dominance, volatility)`**
   - Priority: Volatility > Dominance > Diffusion
   - Returns: "Scenario Planning", "Driver Decomposition", "Centralization", or "Basic Refactoring"

---

### ✅ Task 2: Prescription Templates (ai_explainer.py)

**Updated System Prompt**:
```python
LEVEL_1_SYSTEM_PROMPT = """
あなたは「リファクタリング・アーキテクト」です。

**厳格なルール**:
❌ 禁止: ビジネス概念の説明、段落形式の説明
✅ 必須: データ駆動型の「レシピ」形式

**出力フォーマット（厳守）**:
【影響分析】
• 使用回数: {diffusion}箇所
• 影響範囲: {dominance}個の依存セル
• リスク: 更新漏れで{dominance}箇所に波及

【推奨レシピ: {prescription_mode}】
1. [具体的な手順1]
2. [具体的な手順2]
3. [具体的な手順3]

【効果】
• 修正箇所: {diffusion}箇所 → 1箇所
• 保守時間: 削減率80%
"""
```

**Prescription Modes**:

1. **Centralization** (Diffusion > 3):
   - Create Parameters sheet
   - Use Named Ranges
   - Link all instances to one cell

2. **Driver Decomposition** (Dominance > 50):
   - Split value into components
   - Example: Revenue = Price × Volume
   - Minimize impact on dependents

3. **Scenario Planning** (Volatility High):
   - Use CHOOSE/IF functions
   - Create scenario selector
   - Define values for each scenario

4. **Basic Refactoring** (Default):
   - Simple variable replacement
   - Cell reference substitution

---

### ✅ Task 3: Integration (app.py)

**Before AI Call**:
```python
# Calculate impact metrics
impact_score = analyzer.calculate_impact_score(
    model, cell_address, hardcoded_value
)

# Add to context
cell_labels['diffusion'] = impact_score['diffusion']
cell_labels['dominance'] = impact_score['dominance']
cell_labels['volatility'] = impact_score['volatility']
cell_labels['prescription_mode'] = impact_score['prescription_mode']
```

**Result**: AI receives calculated metrics and knows which template to use

---

## Decision Tree

```
Hardcoded Value Detected
    ↓
Calculate Impact Metrics
    ↓
┌─────────────────────────────────────┐
│ Volatility High? (3+ values in row) │
└─────────────────────────────────────┘
    ↓ YES                    ↓ NO
Scenario Planning    ┌──────────────────────┐
                     │ Dominance > 50?      │
                     └──────────────────────┘
                         ↓ YES        ↓ NO
                   Driver         ┌─────────────┐
                   Decomposition  │ Diffusion>3?│
                                  └─────────────┘
                                   ↓YES    ↓NO
                              Centralization  Basic
```

---

## Example Output (Expected)

### Input Data:
- Value: 0.3
- Diffusion: 5 occurrences
- Dominance: 242 dependent cells
- Volatility: Low
- Prescription Mode: "Driver Decomposition" (dominance > 50)

### Expected AI Output:
```
【影響分析】
• 使用回数: 5箇所
• 影響範囲: 242個の依存セル
• リスク: 更新漏れで242箇所に波及

【推奨レシピ: Driver Decomposition】
1. 新規シート「計算ロジック」を作成
2. この値を構成要素に分解:
   - A1: "税引前利益"
   - A2: "法人税率" = 0.3
   - A3: "法人税額" = A1 * A2
3. 名前付き範囲を定義: "Tax_Rate" = A2
4. 全5箇所を =Tax_Rate に置換

【効果】
• 修正箇所: 5箇所 → 1箇所
• 影響範囲の可視化: 242セルへの波及が明確に
• 保守時間: 削減率80%
```

---

## Key Improvements

### Before (Generic)
- AI guesses the problem
- Vague suggestions
- No metrics
- Paragraph format

### After (Data-Driven)
- Python calculates the problem
- Specific prescription template
- Exact metrics (5 occurrences, 242 dependents)
- Recipe format with bullet points

---

## Testing Checklist

**Test Case 1: High Diffusion (Centralization)**
- [ ] Value appears 10 times
- [ ] Dominance < 50
- [ ] Volatility Low
- [ ] Expected Mode: "Centralization"
- [ ] Verify AI suggests Parameters sheet

**Test Case 2: High Dominance (Driver Decomposition)**
- [ ] Value appears 5 times
- [ ] Dominance > 50 (e.g., 242 dependents)
- [ ] Volatility Low
- [ ] Expected Mode: "Driver Decomposition"
- [ ] Verify AI suggests splitting into components

**Test Case 3: High Volatility (Scenario Planning)**
- [ ] Row has 3+ different hardcoded values
- [ ] Expected Mode: "Scenario Planning"
- [ ] Verify AI suggests CHOOSE/IF functions

---

## Files Modified

1. **src/analyzer.py** (+120 lines):
   - `calculate_impact_score()`
   - `_calculate_diffusion()`
   - `_calculate_dominance()`
   - `_calculate_volatility()`
   - `_determine_prescription_mode()`

2. **src/ai_explainer.py** (+50 lines):
   - Updated LEVEL_1_SYSTEM_PROMPT with recipe format
   - Added `_get_prescription_instruction()`
   - Updated `_build_breakdown_prompt()` with metrics

3. **app.py** (+15 lines):
   - Call `analyzer.calculate_impact_score()`
   - Pass metrics to AI via cell_labels

---

## Business Impact

**Sellability**: 
- ✅ Data-driven (not guessing)
- ✅ Specific metrics persuade users
- ✅ Recipe format is actionable
- ✅ Prescription templates ensure quality

**User Experience**:
- Sees exact impact (242 dependents!)
- Gets specific template for their problem
- Receives step-by-step recipe
- Understands the "why" (metrics) and "how" (steps)

---

**Status**: ✅ READY FOR TESTING  
**Next Action**: Upload Excel file and verify AI output format  
**Expected**: Recipe-style output with metrics and specific prescription
