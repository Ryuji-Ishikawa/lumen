# Phase 7.1: AI Tuning - From "Teacher" to "Refactoring Architect"

**Status**: ✅ COMPLETE  
**Date**: December 3, 2025  
**Priority**: CRITICAL UX IMPROVEMENT

---

## Executive Summary

The Business Owner reviewed AI suggestions and found them "Generic and Useless." The AI was explaining business concepts (e.g., "What is Corporate Tax?") instead of providing actionable refactoring steps.

**The Pivot**: Transform AI from a "Teacher" to a "Refactoring Architect" that provides concrete Excel implementation steps.

---

## Changes Implemented

### 1. Global Context Injection (app.py)

**Added Frequency Analysis**:
```python
# Count occurrences of this value across the model
occurrence_count = sum(1 for r in model.risks 
                      if r.risk_type == "Hidden Hardcode" 
                      and r.details.get('hardcoded_value') == hardcoded_value)

# Predict value type
try:
    val = float(hardcoded_value)
    if 0 <= val <= 1:
        value_type = "比率 (Rate: 0.0-1.0)"
    elif val == int(val):
        value_type = "整数 (Integer)"
    else:
        value_type = "小数 (Decimal)"
except:
    value_type = "不明"

# Add to context
cell_labels['occurrence_count'] = f"{occurrence_count}"
cell_labels['value_type'] = value_type
cell_labels['actual_value'] = hardcoded_value
```

**✅ Result**: AI now knows:
- How many times the value appears (e.g., "5 times")
- What type of value it is (Rate, Integer, Decimal)
- The actual value being analyzed

---

### 2. Revised System Prompts (src/ai_explainer.py)

**Level 1: "Refactoring Architect" (was "Coach")**

**OLD** (Generic Teaching):
```
あなたは「コーチ」として、死んだExcelモデルを復活させる専門家です。
- ハードコードされた値を特定し、それらを意味のある変数に分解する
- 「このモデルは復活できます」というメッセージを伝える
```

**NEW** (Actionable Architecture):
```
あなたは「リファクタリング・アーキテクト」です。

**厳格なルール**:
❌ 禁止: ビジネス概念の説明（例：「課税所得とは収益から費用を引いたもの...」）
✅ 必須: 具体的なリファクタリング手順

**提案フォーマット**:
1. **問題**: この値が{occurrence_count}箇所に散在しています
2. **リスク**: 値が変更された時、更新漏れが発生します
3. **解決策**:
   - 「前提条件」シートを作成
   - セルA1に変数名を定義（例：法人税率）
   - セルB1に値を入力
   - 名前付き範囲を設定（例：Tax_Rate）
   - 全{occurrence_count}箇所を =Tax_Rate に置換
```

**✅ Result**: AI now provides:
- Specific Excel steps (create sheet, define name, replace references)
- No business concept explanations
- Concrete implementation guidance

---

### 3. Updated Prompt Builder (src/ai_explainer.py)

**OLD Prompt**:
```
以下のハードコードされた値を分析してください：
数式構造: {formula}
行ラベル: {row_label}

このハードコードされた値を、より保守性の高い構造に分解する方法を提案してください。
```

**NEW Prompt with Global Context**:
```
【グローバルコンテキスト】
- ハードコード値: {actual_value}
- 値のタイプ: {value_type}
- 出現回数: {occurrence_count}箇所
- 行ラベル: {row_label}
- 影響を受けるドライバー: {len(driver_cells)}個のセル

【タスク】
この値の一元管理方法を、具体的な手順で提案してください。
「前提条件シート」「名前付き範囲」「セル参照の置換」などの実装手順を含めてください。

❌ ビジネス概念の説明は不要です
✅ Excelでの具体的な操作手順を提示してください
```

**✅ Result**: AI receives rich context and clear instructions

---

## Example Output Comparison

### BEFORE (Generic Teaching)
```
法人税について説明します。

法人税とは、企業の課税所得に対して課される税金です。
課税所得は、収益から費用を差し引いて計算されます。

この値を変数化することで、モデルの保守性が向上します。
前提条件シートを作成することを検討してください。
```

**❌ Problems**:
- Explains what corporate tax is (user already knows)
- Vague suggestions ("consider creating...")
- No concrete steps

### AFTER (Actionable Architecture)
```
この値0.3は5箇所に散在しています。変更時に更新漏れのリスクがあります。

【推奨手順】
1. 新規シート「前提条件」を作成
2. A1: "法人税率", B1: 0.3
3. B1を選択 → 数式タブ → 名前の定義 → "Tax_Rate"
4. 5箇所全てを =Tax_Rate に置換

これにより、税率変更時は1箇所の修正で完了します。
```

**✅ Improvements**:
- States the problem (5 occurrences, update risk)
- Provides step-by-step Excel instructions
- Explains the benefit (1-place update)
- No concept explanations

---

## Technical Implementation

### Frequency Analysis Algorithm

```python
# Count occurrences across all risks
occurrence_count = sum(1 for r in model.risks 
                      if r.risk_type == "Hidden Hardcode" 
                      and r.details.get('hardcoded_value') == hardcoded_value)
```

**Performance**: O(n) where n = number of risks (typically < 100)

### Value Type Prediction

```python
try:
    val = float(hardcoded_value)
    if 0 <= val <= 1:
        value_type = "比率 (Rate: 0.0-1.0)"
    elif val == int(val):
        value_type = "整数 (Integer)"
    else:
        value_type = "小数 (Decimal)"
except:
    value_type = "不明"
```

**Logic**:
- 0.0-1.0 → Rate (likely percentage or ratio)
- Integer → Count or ID
- Decimal → Amount or measurement
- Non-numeric → Unknown

---

## All Three Personas Updated

### Level 1: Refactoring Architect
- **Focus**: Centralize scattered values
- **Tools**: Assumption sheets, Named Ranges
- **Tone**: Concrete, step-by-step

### Level 2: Structural Engineer
- **Focus**: Stabilize complex dependencies
- **Tools**: Calculation sheets, Intermediate cells
- **Tone**: Technical, systematic

### Level 3: Optimization Architect
- **Focus**: Enable strategic features
- **Tools**: Data Tables, Scenario Manager, Goal Seek
- **Tone**: Strategic, forward-looking

---

## Testing Checklist

### Manual Testing Required

**Test Case 1: Tax Rate (0.3)**
- [ ] Upload file with 0.3 appearing 5 times
- [ ] Click "Suggest Improvement"
- [ ] Verify AI mentions "5箇所" (5 occurrences)
- [ ] Verify AI identifies it as "比率" (Rate)
- [ ] Verify AI provides step-by-step instructions
- [ ] Verify NO business concept explanations

**Test Case 2: Integer (12)**
- [ ] Upload file with 12 appearing 3 times
- [ ] Verify AI identifies it as "整数" (Integer)
- [ ] Verify occurrence count is correct

**Test Case 3: Large Amount (1000000)**
- [ ] Upload file with large number
- [ ] Verify AI identifies it as "小数" (Decimal)
- [ ] Verify refactoring steps are appropriate

---

## Business Impact

### Before
- **User Reaction**: "Generic and Useless"
- **Problem**: AI teaches concepts user already knows
- **Result**: User ignores AI suggestions

### After
- **User Reaction**: (To be tested)
- **Improvement**: AI provides actionable Excel steps
- **Expected Result**: User can immediately implement suggestions

---

## Key Improvements

1. **Global Context**: AI knows frequency and value type
2. **No Teaching**: Strict prohibition on concept explanations
3. **Concrete Steps**: Specific Excel operations (create sheet, define name, replace)
4. **Risk Communication**: Clear statement of update risks
5. **Benefit Explanation**: Why the refactoring helps

---

## Files Modified

1. **src/ai_explainer.py**:
   - Updated all 3 system prompts (LEVEL_1, LEVEL_2, LEVEL_3)
   - Updated `_build_breakdown_prompt()` in OpenAIProvider
   - Updated `_build_breakdown_prompt()` in GoogleProvider

2. **app.py**:
   - Added frequency analysis before AI call
   - Added value type prediction
   - Injected global context into cell_labels

---

## Next Steps

1. **User Testing**: Get Business Owner feedback on new suggestions
2. **Iteration**: Refine prompts based on real-world usage
3. **Expansion**: Add more value type predictions (dates, currencies)
4. **Localization**: Ensure Japanese instructions are clear and natural

---

## Success Metrics

- **Actionability**: Can user implement suggestion in < 5 minutes?
- **Clarity**: Are Excel steps specific enough?
- **Relevance**: Does AI avoid teaching known concepts?
- **Completeness**: Does suggestion include all necessary steps?

---

**Status**: ✅ READY FOR BUSINESS OWNER TESTING  
**Next Action**: Upload Excel file and test AI suggestions  
**Expected Outcome**: Concrete, actionable refactoring guidance
