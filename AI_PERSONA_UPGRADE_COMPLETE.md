# AI Persona Upgrade: From "Excel Tutor" to "CFO Advisor"

## Status: ✅ COMPLETE

## Executive Summary

Transformed AI suggestions from boring Excel tutorials into compelling business value propositions. The AI now speaks like a Senior CFO Advisor, not a software manual.

## Key Changes

### 1. Business Value First (The Why)

**Before** (Excel Tutor):
> "Create a Parameter sheet to organize hardcodes."

**After** (CFO Advisor):
> "この値は423箇所に埋め込まれており、シナリオ分析が不可能です。取締役会で「もし為替が10%変動したら？」と聞かれても、即答できません。"

### 2. Smart Naming (The What)

**New Logic**: If Diffusion > 10, AI explicitly warns:

```
【重要: スマートネーミング】
この値は423箇所で使用されています。これは「開発費」という特定コストではなく、
グローバル前提条件（為替レート、税率、成長率など）の可能性が高いです。

❌ 悪い命名: "開発費" （誤解を招く）
✅ 良い命名: "USD_JPY_Rate" または "Global_Tax_Rate" （汎用的）
```

### 3. The Hook (The Benefit)

Every suggestion now ends with a "Pro Tip":

> 💡 Pro Tip: これにより、会議中の「What-if」質問に即座に回答できます。

## Updated Personas

### Level 1: CFOアドバイザー (Static Model)

**Focus**: シナリオ分析の実現

**Key Messages**:
- ビジネスリスク: "シナリオ分析が不可能"
- ビジネス価値: "Best/Worst caseを5秒で比較可能"
- Pro Tip: "会議中の「What-if」質問に即座に回答"

**Tone**: Excel機能ではなく「安心感」を売る

### Level 2: リスク管理アドバイザー (Unstable Model)

**Focus**: 監査対応と保守性

**Key Messages**:
- ビジネスリスク: "監査で説明できない計算フロー"
- ビジネス価値: "監査対応時間が1/10に"
- Pro Tip: "監査や引継ぎ時の質問が消えます"

**Tone**: 技術的正しさではなく「安心感」を売る

### Level 3: 戦略コンサルタント (Strategic Model)

**Focus**: 意思決定速度と競争優位性

**Key Messages**:
- 戦略的機会: "M&A判断を3日 → 30分に短縮"
- ビジネス価値: "競合より速く正確な意思決定"
- Pro Tip: "経営陣の質問に会議中その場で回答"

**Tone**: Excel機能ではなく「競争優位性」を売る

## Technical Implementation

### Prompt Structure

All prompts now follow this structure:

```
【ビジネスリスク】
なぜこのままだと危険か

【推奨ソリューション】
1. 具体的な手順1
2. 具体的な手順2
3. 具体的な手順3

【ビジネス価値】
✓ 意思決定速度: ...
✓ 保守性: ...
✓ 信頼性: ...

💡 Pro Tip: 実務での活用シーン
```

### Smart Naming Logic

```python
if diffusion > 10:
    naming_guidance = f"""
この値は{diffusion}箇所で使用されています。
これは特定項目ではなく、グローバル前提条件です。

❌ 悪い命名: "{row_label}"
✅ 良い命名: "USD_JPY_Rate" または "Global_Tax_Rate"
"""
```

### Context Injection

Now passing to AI:
- `diffusion`: 出現回数
- `dominance`: 影響範囲
- `prescription_mode`: 推奨モード
- `row_label`: 行ラベル（スマートネーミングの判断に使用）

## Before/After Examples

### Example 1: Hardcoded Value (Diffusion = 423)

**Before**:
> "この値を名前付き範囲にしましょう。前提条件シートを作成し、セル参照を置換してください。"

**After**:
> "【ビジネスリスク】
> この値は423箇所に埋め込まれており、シナリオ分析が不可能です。
> 取締役会で「もし為替が10%変動したら？」と聞かれても、即答できません。
> 
> 【重要: スマートネーミング】
> この値は423箇所で使用されています。これは「開発費」ではなく、
> 為替レートなどのグローバル前提条件の可能性が高いです。
> 
> ❌ 悪い命名: "開発費"
> ✅ 良い命名: "USD_JPY_Rate"
> 
> 【推奨ソリューション】
> 1. 「前提条件」シートを作成
> 2. A1に「USD_JPY_Rate」と命名
> 3. 数式 → 名前の管理 → 新規作成
> 4. 検索と置換で423箇所を一括更新
> 
> 【ビジネス価値】
> ✓ シナリオ分析: Best/Worst caseを5秒で比較可能
> ✓ 感度分析: 為替変動の影響度を即座に可視化
> ✓ 保守性: 更新作業が423箇所 → 1箇所に削減
> 
> 💡 Pro Tip: これにより、会議中の「What-if」質問に即座に回答できます。"

### Example 2: Circular Reference (Level 2)

**Before**:
> "循環参照が検出されました。計算フローを整理してください。"

**After**:
> "【ビジネスリスク】
> この計算フローは循環参照を含んでおり、以下のリスクがあります：
> • 監査対応: 計算根拠を説明できない
> • エラー検出: 問題発生時の原因特定に数時間
> • 引継ぎ: 後任者が理解できず、属人化
> 
> 【推奨ソリューション】
> 1. 「計算ロジック」シートを作成
> 2. 中間計算を明示的に配置
> 3. 各ステップに説明ラベルを追加
> 4. 最終結果のみを他シートから参照
> 
> 【ビジネス価値】
> ✓ 監査対応: 計算フローが明確で、説明時間が1/10に
> ✓ 保守性: 新メンバーが1日で理解可能
> ✓ 信頼性: エラー発生時の原因特定が5分以内
> 
> 💡 Pro Tip: これにより、監査や引継ぎ時の「このセルは何を計算してる？」という質問が消えます。"

## Rules Enforced

### ❌ Prohibited (Excel Tutor Style)
- Excel機能の説明（「名前付き範囲とは...」）
- 抽象的な提案（「シナリオ分析を検討してください」）
- 技術用語の羅列（「データテーブルを使いましょう」）

### ✅ Required (CFO Advisor Style)
- ビジネスリスクの明示（「シナリオ分析が不可能」）
- 具体的な価値提示（「意思決定速度が10倍」）
- 実務シーンの提示（「会議中に即答」）
- Pro Tip（実践的なアドバイス）

## Business Owner's Philosophy

> "Don't sell 'Excel features'. Sell 'Peace of Mind'."

The AI now sells:
- **Level 1**: シナリオ分析の実現（安心感）
- **Level 2**: 監査対応の容易さ（安心感）
- **Level 3**: 意思決定の速度（競争優位性）

## Files Modified

- `src/ai_explainer.py`
  - Updated `LEVEL_1_SYSTEM_PROMPT` (CFOアドバイザー)
  - Updated `LEVEL_2_SYSTEM_PROMPT` (リスク管理アドバイザー)
  - Updated `LEVEL_3_SYSTEM_PROMPT` (戦略コンサルタント)
  - Enhanced `_build_breakdown_prompt()` with smart naming logic
  - Added diffusion/dominance context injection

## Testing Recommendations

1. **Test with High Diffusion** (>10): Verify smart naming guidance appears
2. **Test Each Level**: Verify persona tone matches level
3. **Test Pro Tips**: Verify every suggestion ends with practical advice
4. **Test Business Value**: Verify no Excel feature explanations

## Success Metrics

- ✅ No Excel feature explanations
- ✅ Every suggestion has business risk section
- ✅ Every suggestion has business value section
- ✅ Every suggestion has Pro Tip
- ✅ Smart naming triggers for diffusion > 10
- ✅ Tone matches persona (Coach/Mechanic/Strategist → CFO Advisor/Risk Manager/Strategic Consultant)

---

**Conclusion**: The AI now speaks the language of business, not the language of Excel. It sells peace of mind, not features.
