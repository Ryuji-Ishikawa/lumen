# Suggest Fix UI改善 - 文言とUI微修正

## 実装日
2025-12-10

## 修正内容

### 1. Inconsistent Formulaの説明文改善

#### 修正ポイント
1. ✅ デスマス調で統一
2. ✅ 単一列の場合と複数列の場合で文言を分ける
3. ✅ 具体的な数値（セル数、パーセンテージ）を表示

#### Before（修正前）
```
説明: この行の他の48個のセルとは数式パターンが異なります。意図的な可能性が高い（単一列の違い）。
説明: 数式パターンの不整合（17箇所）
```

#### After（修正後）

**単一列の場合（1箇所だけ異なる）**：
```
説明: この行の他の48個のセルとは1箇所だけ数式パターンが異なります。意図的な変更の可能性が高いですが、念のため確認してください。
```
- 重要度: Low（意図的な可能性が高い）

**複数列の場合（2箇所以上異なる）**：
```
説明: この行の他の51個のセルと、17セル（25%）数式パターンが異なります。確認してください。
```
- 重要度: High（エラーの可能性が高い）

#### 実装詳細

**ファイル**: `src/analyzer.py`

```python
# Calculate percentage of inconsistent cells
inconsistent_percentage = (minority_count / total_cells) * 100

# Assess likelihood of intentional vs error
if minority_count == 1:
    # Single cell difference - likely intentional
    severity = "Low"
    description = f"この行の他の{max_count}個のセルとは1箇所だけ数式パターンが異なります。意図的な変更の可能性が高いですが、念のため確認してください。"
else:
    # Multiple cells different - likely error
    severity = "High"
    description = f"この行の他の{max_count}個のセルと、{minority_count}セル（{inconsistent_percentage:.0f}%）数式パターンが異なります。確認してください。"
```

### 2. Hidden Hardcode Suggest Fix UI改善

#### 修正ポイント
1. ✅ 背景色の青を削除（`st.info` → `st.markdown`）
2. ✅ メリットを一番上に配置
3. ✅ 手順を具体的に改善（エクセル操作の詳細）

#### Before（修正前）
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
- 背景色: 青（`st.info`）

#### After（修正後）
```
修正することのメリット：
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します

推奨される修正手順：

1. 直接書き込んでいる固定値を変数に変える
- 空いているセルもしくは新規シート（例：変数シート）に、固定値（`12`）を入力
- エクセル数式バー左横に表示されているセル番号をクリック
- セル番号を適切な名前に書き換える（例：mil_百万、為替、売上成長率_係数など）

2. 数式を修正
- セル `E5` の数式から固定値 `12` を削除し、代わりに上記のセル名を入れる
```
- 背景色: なし（`st.markdown`）

#### 実装詳細

**ファイル**: `src/master_detail_ui.py`

```python
if lang == 'ja':
    suggestion = f"""
**修正することのメリット：**
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します

**推奨される修正手順：**

**1. 直接書き込んでいる固定値を変数に変える**
- 空いているセルもしくは新規シート（例：変数シート）に、固定値（`{hardcoded_value}`）を入力
- エクセル数式バー左横に表示されているセル番号をクリック
- セル番号を適切な名前に書き換える（例：mil_百万、為替、{row_label}_係数など）

**2. 数式を修正**
- セル `{risk.cell}` の数式から固定値 `{hardcoded_value}` を削除し、代わりに上記のセル名を入れる
"""

# Use markdown instead of st.info to avoid blue background
st.markdown(suggestion)
```

## 改善効果

### 1. Inconsistent Formulaの説明

**Before**:
- 英語と日本語が混在
- 単一列と複数列で同じ文言
- 具体的な数値が不足

**After**:
- ✅ 完全に日本語（デスマス調）
- ✅ 単一列と複数列で文言を分離
- ✅ 具体的な数値（セル数、パーセンテージ）を表示
- ✅ 重要度が適切（単一列=Low、複数列=High）

### 2. Hidden Hardcode Suggest Fix

**Before**:
- 青い背景色（目立ちすぎ）
- メリットが最後
- 手順が抽象的

**After**:
- ✅ 背景色なし（シンプル）
- ✅ メリットが最初（ユーザーの動機付け）
- ✅ 手順が具体的（エクセル操作の詳細）
- ✅ 実用的な例（mil_百万、為替など）

## テスト方法

### 1. Inconsistent Formulaの説明

```bash
streamlit run app.py
```

1. Inconsistent Formulaリスクを選択
2. **単一列の場合**:
   - 説明: "この行の他の◯個のセルとは1箇所だけ数式パターンが異なります。意図的な変更の可能性が高いですが、念のため確認してください。"
   - 重要度: Low

3. **複数列の場合**:
   - 説明: "この行の他の◯個のセルと、◯セル（◯%）数式パターンが異なります。確認してください。"
   - 重要度: High

### 2. Hidden Hardcode Suggest Fix

1. Hidden Hardcodeリスクを選択
2. 「修正案」セクションを確認:
   - ✅ 背景色がない（白背景）
   - ✅ メリットが最初に表示
   - ✅ 手順が具体的（エクセル操作の詳細）

## 変更ファイル

1. `src/analyzer.py`:
   - `_detect_row_inconsistency()`: 説明文を単一列/複数列で分離、デスマス調統一

2. `src/master_detail_ui.py`:
   - `render_ai_cure()`: UI改善（背景色削除、メリット優先、手順詳細化）

## 破壊的変更

なし。既存の機能は全て動作します。

---

**Status**: ✅ 実装完了
**Phase**: Suggest Fix UI Refinement
**Next**: Driver X-Ray と Logic Translator の統合検討
