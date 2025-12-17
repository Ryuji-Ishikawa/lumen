# Suggest Fix 最終調整 - メリット表示とフォーミュラ例

## 実装日
2025-12-10

## 修正内容

### 1. メリット表示の改善

#### Before（修正前）
```
修正することのメリット：
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します
```
- タイトル: 「修正することのメリット」（長い）
- フォントサイズ: 通常サイズ

#### After（修正後）
```
メリット：
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します
```
- タイトル: 「メリット」（短縮）
- フォントサイズ: 小さめ（0.9em、グレー色）

### 2. 数式の例を追加

#### Before（修正前）
```
2. 数式を修正
- セル AB13 の数式から固定値 80 を削除し、代わりに上記のセル名を入れる
```
- 抽象的な説明のみ

#### After（修正後）
```
2. 数式を修正
- セル AB13 の数式から固定値 80 を削除し、代わりに上記のセル名を入れる

例：
- 修正前: =B13*80
- 修正後: =B13*売上成長率_係数
```
- 具体的な数式の例を表示
- 実際の数式から自動生成

## 実装詳細

### メリット表示の改善

**ファイル**: `src/master_detail_ui.py`

```python
# Benefits section with smaller font
benefits = """
<div style="font-size: 0.9em; color: #666;">

**メリット：**
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します

</div>
"""
```

### 数式例の自動生成

**ファイル**: `src/master_detail_ui.py`

```python
# Get formula for example
formula = risk.details.get("formula", "")

# Generate example variable name
example_var_name = "変数名"
if row_label and row_label != "この項目":
    # Use row label for variable name suggestion
    example_var_name = f"{row_label}_係数"

# Create before/after formula example
formula_before = ""
formula_after = ""
if formula:
    # Show original formula
    formula_before = f"={formula}" if not formula.startswith('=') else formula
    # Create example with variable name replacing hardcoded value
    formula_after = formula_before.replace(str(hardcoded_value), example_var_name, 1)

# Add formula example if available
if formula_before and formula_after:
    suggestion += f"""

**例：**
- 修正前: `{formula_before}`
- 修正後: `{formula_after}`
"""
```

## 表示例

### 例1: 売上成長率の係数

```
メリット：
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します

推奨される修正手順：

1. 直接書き込んでいる固定値を変数に変える
- 空いているセルもしくは新規シート（例：変数シート）に、固定値（80）を入力
- エクセル数式バー左横に表示されているセル番号をクリック
- セル番号を適切な名前に書き換える（例：mil_百万、為替、売上成長率_係数など）

2. 数式を修正
- セル AB13 の数式から固定値 80 を削除し、代わりに上記のセル名を入れる

例：
- 修正前: =B13*80
- 修正後: =B13*売上成長率_係数
```

### 例2: 税率

```
メリット：
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します

推奨される修正手順：

1. 直接書き込んでいる固定値を変数に変える
- 空いているセルもしくは新規シート（例：変数シート）に、固定値（0.3）を入力
- エクセル数式バー左横に表示されているセル番号をクリック
- セル番号を適切な名前に書き換える（例：mil_百万、為替、税率_係数など）

2. 数式を修正
- セル E5 の数式から固定値 0.3 を削除し、代わりに上記のセル名を入れる

例：
- 修正前: =D5*0.3
- 修正後: =D5*税率_係数
```

## 改善効果

### 1. メリット表示

**Before**:
- タイトルが長い（「修正することのメリット」）
- 通常サイズで目立ちすぎ

**After**:
- ✅ タイトルが短い（「メリット」）
- ✅ 小さめフォント（0.9em）
- ✅ グレー色で控えめ
- ✅ 手順に集中できる

### 2. 数式例

**Before**:
- 抽象的な説明のみ
- ユーザーが想像する必要がある

**After**:
- ✅ 具体的な数式例を表示
- ✅ 修正前/修正後を並べて表示
- ✅ 実際の数式から自動生成
- ✅ 変数名も具体的（項目名を活用）

## テスト方法

```bash
streamlit run app.py
```

1. Hidden Hardcodeリスクを選択
2. 「修正案」セクションを確認:
   - ✅ 「メリット」が小さめフォント（グレー色）
   - ✅ 数式の例が表示される
   - ✅ 修正前/修正後が並んでいる
   - ✅ 変数名が具体的（項目名を活用）

## 変更ファイル

1. `src/master_detail_ui.py`:
   - `render_ai_cure()`: メリット表示改善、数式例追加

## 破壊的変更

なし。既存の機能は全て動作します。

---

**Status**: ✅ 実装完了
**Phase**: Suggest Fix Final Polish
**Next**: Driver X-Ray と Logic Translator の統合検討
