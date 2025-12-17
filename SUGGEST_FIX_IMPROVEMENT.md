# Suggest Fix 機能改善 - Rule-Based Approach

## 実装日
2025-12-10

## 問題点

**Before（修正前）**：
- 全てのリスクタイプに対して定型文を表示
- AI機能のON/OFF関係なく同じ内容
- 実用性が低い

```
提案: この固定値を変数に分解してください
1. セルA1に成長率を入力
2. この数式から参照
3. ラベル「成長率」を追加
```

## 解決策

### 設計方針

| リスクタイプ | アプローチ | 理由 |
|------------|-----------|------|
| **Hidden Hardcode** | ✅ ルールベースのSuggest Fix | 修正方法は定型的、AI不要 |
| **Inconsistent Formula** | ✅ 説明文強化 | Logic Translatorで詳細確認可能 |
| **その他のリスク** | ❌ Suggest Fix非表示 | シンプルな警告で十分 |

### 実装内容

#### 1. Hidden Hardcode専用のSuggest Fix（ルールベース）

**ファイル**: `src/master_detail_ui.py`

**変更点**：
- AI不要のルールベース実装
- Hidden Hardcode専用（他のリスクでは非表示）
- コンテキスト（項目名、期間）を活用した具体的な提案

**新しい提案内容**：
```
推奨される修正手順：

1. 固定値を変数化
   - 空いているセル（例：A1）に値 `12` を入力
   - セルに名前を付ける（例：「売上成長率_係数」）

2. 数式を修正
   - セル `E5` の数式から固定値 `12` を削除
   - 代わりに上記のセルを参照

3. ラベルを追加
   - 変数セルの左側に説明ラベルを追加（例：「売上成長率の係数」）

メリット：
- 値の変更が1箇所で済む
- 計算ロジックが明確になる
- メンテナンス性が向上
```

**特徴**：
- ✅ 即座に表示（API呼び出し不要）
- ✅ コスト削減（無料）
- ✅ 一貫した品質
- ✅ 具体的な手順（コンテキストを活用）

#### 2. Inconsistent Formulaの説明文強化

**ファイル**: `src/analyzer.py`

**変更点**：
```python
# Before
description = f"Formula pattern differs from {max_count} other cells in this row. {likelihood}."

# After
description = f"Formula pattern differs from {max_count} other cells in this row. {likelihood}. ⚠️ 同一行の他のセルと数式パターンが異なります。意図的な違いか確認してください。"
```

**効果**：
- ユーザーに明確な行動を促す
- Logic Translatorでの詳細確認を誘導
- Suggest Fixボタンは非表示（重複を避ける）

## メリット

### 1. コスト削減
- **Before**: 全リスクでAI呼び出し → 高コスト
- **After**: Hidden Hardcodeのみルールベース → 無料

### 2. パフォーマンス向上
- **Before**: AI応答待ち（2-5秒）
- **After**: 即座に表示（0秒）

### 3. 品質の一貫性
- **Before**: AIが時々変な提案
- **After**: 常に正確なルールベース提案

### 4. 役割分担の明確化

| 機能 | 役割 | AI使用 |
|------|------|--------|
| **Master-Detail Suggest Fix** | シンプルな修正手順 | ❌ 不要 |
| **Driver X-Ray AI提案** | 複雑な戦略分析 | ✅ 必要 |
| **Logic Translator** | 数式の意味論的翻訳 | ✅ 必要 |

## テスト方法

### 1. Hidden Hardcode のSuggest Fix

```bash
streamlit run app.py
```

1. Hidden Hardcodeリスクを選択
2. 「修正案」セクションが表示されることを確認
3. 具体的な手順が表示されることを確認
4. コンテキスト（項目名）が含まれることを確認

### 2. Inconsistent Formula の説明

1. Inconsistent Formulaリスクを選択
2. 「修正案」セクションが**非表示**であることを確認
3. 説明文に「⚠️ 同一行の他のセルと数式パターンが異なります。意図的な違いか確認してください。」が含まれることを確認

### 3. その他のリスク

1. External Link、Circular Referenceなどを選択
2. 「修正案」セクションが**非表示**であることを確認

## 今後の検討事項

### Driver X-Ray と Logic Translator の統合

**現状**：
- Driver X-Ray: AI提案（Dominance, Diffusion, Volatility分析）
- Logic Translator: 数式の意味論的翻訳

**検討ポイント**：
1. 機能の重複はないか？
2. ユーザーはどちらを使うべきか明確か？
3. 統合すべきか、分離すべきか？

→ **次のフェーズで検討**

## 変更ファイル

1. `src/master_detail_ui.py`:
   - `render_ai_cure()`: Hidden Hardcode専用のルールベース実装

2. `src/analyzer.py`:
   - `_detect_row_inconsistency()`: 説明文に確認指示を追加

## 破壊的変更

なし。既存の機能は全て動作します。

---

**Status**: ✅ 実装完了
**Phase**: Suggest Fix Improvement - Rule-Based Approach
**Next**: Driver X-Ray と Logic Translator の統合検討
