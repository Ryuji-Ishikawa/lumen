# Lumen 実装機能レポート（厳密版）

**作成日**: 2025年12月17日  
**目的**: マーケティングランディングページの誤解を修正するため、実際のコードベースに基づいた正確な機能仕様を提供

---

## 1. リスク検知ロジック（エンジン）

### 実装済みリスクタイプ（9種類）

#### 1.1 Hidden Hardcode（ベタ打ち値）
- **実装状況**: ✅ 完全実装
- **検知方法**: openpyxl tokenizer を使用して数式内の数値リテラルを検出
- **重要度**: Low（一般的な定数: 0, 1, 12）/ High（その他の値）
- **ファイル**: `src/analyzer.py` - `_detect_hidden_hardcodes()` (98-182行目)
- **特徴**:
  - 許可定数リスト（ユーザー設定可能）
  - 一般的な定数（0, 1, 12）は Low severity
  - 未知の値は High severity

#### 1.2 Circular Reference（循環参照）
- **実装状況**: ✅ 完全実装
- **検知方法**: NetworkX の `simple_cycles()` を使用
- **重要度**: Critical
- **ファイル**: `src/analyzer.py` - `_detect_circular_references()` (183-242行目)
- **特徴**: 最大100サイクルまで報告（パフォーマンス保護）

#### 1.3 Inconsistent Formula（数式の不整合）
- **実装状況**: ✅ 完全実装
- **検知方法**: 行内の数式パターンを比較（横方向チェック）
- **重要度**: High / Low（尤度評価に基づく）
- **ファイル**: `src/analyzer.py` - `_detect_row_inconsistency()` (1668-1832行目)
- **特徴**:
  - パターン抽出（セル参照を正規化）
  - 尤度評価（Likely error / Uncertain / Possibly intentional / Likely intentional）
  - デスマス調の日本語説明

#### 1.4 Inconsistent Value（値の不整合）
- **実装状況**: ✅ 完全実装
- **検知方法**: 同じ行ラベルで異なるベタ打ち値を検出
- **重要度**: High
- **ファイル**: `src/analyzer.py` - `_detect_value_conflicts()` (1833-1906行目)
- **目的**: 更新漏れの検出

#### 1.5 External Link（外部リンク）
- **実装状況**: ✅ 完全実装
- **検知方法**: 数式内の `[` 文字を検出（外部ファイル参照）
- **重要度**: Critical
- **ファイル**: `src/analyzer.py` - `_detect_external_links()` (1907-1963行目)
- **別名**: Phantom Link

#### 1.6 Formula Error（数式エラー）
- **実装状況**: ✅ 完全実装
- **検知方法**: セル値が Excel エラー文字列かチェック
- **重要度**: Critical
- **ファイル**: `src/analyzer.py` - `_detect_formula_errors()` (1964-2050行目)
- **検出エラー**: `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#N/A`, `#NUM!`, `#NULL!`

#### 1.7 Merged Cell Risk（結合セルリスク）
- **実装状況**: ✅ 実装済み（簡易版）
- **検知方法**: 数式が結合セル範囲を参照しているかチェック
- **重要度**: Medium
- **ファイル**: `src/analyzer.py` - `_detect_merged_cell_risks()` (243-310行目)

#### 1.8 Cross-Sheet Spaghetti（クロスシート複雑性）
- **実装状況**: ✅ 実装済み
- **検知方法**: 3枚以上の外部シートを参照する数式を検出
- **重要度**: Low
- **ファイル**: `src/analyzer.py` - `_detect_cross_sheet_spaghetti()` (311-352行目)

#### 1.9 Timeline Gaps（タイムラインギャップ）
- **実装状況**: ❌ 未実装（スキップ）
- **ファイル**: `src/analyzer.py` - `_detect_timeline_gaps()` (353-365行目)
- **理由**: MVP では複雑すぎるため省略

### 実装されていない機能

#### ❌ "Semantic Translation"（意味的翻訳）
- **マーケティングの誤解**: 変数名を自動的にリネームする機能
- **実際**: この機能は存在しません
- **代わりに存在するもの**: 
  - **Context Labeling**（コンテキストラベリング）: 各リスクに行ラベル・列ラベルを付与
  - **Logic Translator**（ロジック翻訳機）: 数式をセマンティックラベルに翻訳（表示のみ、変更なし）

---

## 2. Logic X-Ray（ロジックX線）

### 実装状況: ✅ 完全実装

**ファイル**: `src/master_detail_ui.py` - `render_logic_xray()` (409-550行目)

### 表示内容

#### 【参照元】(Precedents)
- このセルの値を決めている要素
- 上流の依存関係
- セマンティックラベル付き（例: `H13 (広告宣伝費)`）

#### 【分析対象】(Target Cell)
- 選択されたリスクセル
- ハイライト表示

#### 【影響先】(Dependents)
- このセルを使って計算している箇所
- 下流の依存関係
- 最大10件表示（パフォーマンス保護）
- 影響範囲サマリ付き

### 特徴
- **範囲リスク対応**: 圧縮リスク（例: `H22:K22`）の場合、最初のセルを代表として使用
- **エラーセル対応**: `#REF!` などのエラーセルでも `cell.formula` から数式を取得
- **範囲参照展開**: `SUM(H10:H19)` → 個別セル `H10`, `H11`, ..., `H19` に展開（最大1000セル）
- **間接依存関係**: 直接・間接の両方を追跡

---

## 3. Logic Translator（ロジック翻訳機）

### 実装状況: ✅ 完全実装

**ファイル**: 
- UI: `src/master_detail_ui.py` - `render_logic_translator()` (552-620行目)
- ロジック: `src/analyzer.py` - `translate_formula_to_labels()` (2050-2150行目)

### 機能

#### 目的
Excel の理解（可読性向上）のみ。エラー検出や自動修正は行わない。

#### 翻訳例
```
元の数式: =F12*F13
翻訳後:   =[Unit Price] * [Quantity]

元の数式: ='P&L 2020-2021'!D5
翻訳後:   =[P&L 2020-2021:Revenue]
```

#### 対応パターン
1. **クロスシート参照（引用符付き）**: `'Sheet Name'!A1` → `[SheetName:Label]`
2. **クロスシート参照（引用符なし）**: `Sheet1!A1` → `[Sheet1:Label]`
3. **同一シート参照**: `A1` → `[Label]`

#### 特徴
- シート間ジャンプ不要で数式の意味を理解可能
- 表示のみ（Excel ファイルは変更しない）
- コンテキストラベリングと統合

---

## 4. Suggest Fix（修正案）

### 実装状況: ✅ Hidden Hardcode のみ実装

**ファイル**: `src/master_detail_ui.py` - `render_ai_cure()` (622-750行目)

### 対象リスクタイプ
- ✅ **Hidden Hardcode**: ルールベース提案（AI不要）
- ❌ **Inconsistent Formula**: 提案なし（Logic Translator を使用）
- ❌ **その他**: 提案なし（警告のみで十分）

### 表示内容

#### メリット（小さいフォント、グレー）
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します

#### 推奨される修正手順
1. 固定値を変数に変える
2. 数式を修正

#### 数式例
```
修正前: =F12*3
修正後: =F12*変数名
```

### 特徴
- **ルールベースのみ**（AI不要）
- **圧縮リスク対応**: `model.cells` から数式を取得
- **コピーボタンなし**（ユーザー要望により削除）

---

## 5. AI 統合

### 実装状況: ✅ Smart Context Recovery（AI フォールバック）

**ファイル**: `src/smart_context.py`

### 使用タイミング
- **ルールベース**: 80%の精度（高速、無料）
- **AI リカバリ**: 20%のフォールバック（正確、API コスト）

### AI が呼ばれる条件
1. ルールベースでコンテキストラベルが見つからない
2. ラベルが低品質（数式の残骸、セルアドレスなど）
3. 重要なリスクタイプ（Hidden Hardcode, Inconsistent Formula など）

### AI プロバイダー
- OpenAI（GPT-3.5-turbo）
- Google（Gemini-pro）

### データマスキング
- **重要**: 生の財務データは LLM に送信しない
- 数値は `[NUM]` にマスク
- 数式は `[FORMULA]` にマスク
- テキストラベルのみ送信

---

## 6. UI 要素

### 実装済みタブ

#### Tab 0: File Information（ファイル情報）
- シート数、セル数、数式数
- シート名リスト
- 結合セル範囲
- 依存関係グラフ統計

#### Tab 1: Fatal Errors（最優先項目）
- Circular Reference
- External Link
- Formula Error
- **カウント表示**: タブラベルに件数

#### Tab 2: Integrity Risks（整合性リスク）
- Inconsistent Formula
- Inconsistent Value
- **カウント表示**: タブラベルに件数

#### Tab 3: Structural Debt（構造的負債）
- Hidden Hardcode
- Merged Cell Risk
- **カウント表示**: タブラベルに件数

#### ❌ Driver X-Ray タブ
- **実装状況**: コードは存在するが UI から非表示
- **理由**: ユーザー要望により隠蔽（将来の使用のためコード保存）
- **ファイル**: `app.py` (1085-1303行目) - コメントアウト

### Master-Detail レイアウト

**ファイル**: `src/master_detail_ui.py`

#### Master（リスク一覧）
- リスクタイプごとにグループ化
- 場所、項目名、値、重要度、影響数を表示
- 単一行選択（最後に選択されたリスクが詳細パネルに表示）

#### Detail（詳細パネル）
- スクロール可能コンテナ（高さ700px）
- Logic X-Ray
- Logic Translator
- Suggest Fix（Hidden Hardcode のみ）

---

## 7. Maturity Level（成熟度レベル）

### 実装状況: ✅ 実装済み・表示中

**ファイル**: `src/analyzer.py` - `calculate_maturity_level_heuristic()` (1400-1500行目)

### 計算方法
ヒューリスティックスコアリング（ルールベース）:
- リスク数
- リスクの重要度
- 依存関係の複雑性

### 表示場所
- ヘッダーメトリクスダッシュボード
- 健全性スコアと並んで表示

### レベル
- Level 1: 初級
- Level 2: 中級
- Level 3: 上級
- Level 4: エキスパート
- Level 5: マスター

---

## 8. その他の実装機能

### Context Labeling（コンテキストラベリング）
- **実装状況**: ✅ 完全実装
- **ファイル**: `src/analyzer.py` - `_add_context_labels()` (744-1000行目)
- **機能**: 各リスクに行ラベル・列ラベルを付与
- **スキャン範囲**: 対象セルから列Aまで全スキャン（最大30ラベル）
- **スコアリング**: 位置スコア + ペナルティ（括弧、注釈マーカー、短いテキスト、記号）
- **AI フォールバック**: 低品質ラベルの場合、AI リカバリを実行

### Risk Compression（リスク圧縮）
- **実装状況**: ✅ 完全実装
- **ファイル**: `src/analyzer.py` - `_compress_risks()` (366-550行目)
- **機能**: 重複リスクをグループ化
- **空間近接性チェック**: 行・列の両方で1セル以内のみグループ化
- **影響数の合計**: 圧縮されたリスクの影響数を合算

### Dependency Graph（依存関係グラフ）
- **実装状況**: ✅ 完全実装
- **ファイル**: `src/parser.py`
- **ライブラリ**: NetworkX DiGraph
- **範囲展開**: `SUM(H10:H19)` を個別セルに展開（最大1000セル）
- **エラーセル対応**: `cell.formula` から数式を取得

### Virtual Fill（仮想フィル）
- **実装状況**: ✅ 実装済み
- **ファイル**: `src/parser.py` - `_parse_sheet()` (150-250行目)
- **機能**: 結合セルの全セルに左上セルの値・数式をコピー

---

## 9. マーケティングとの相違点

### 誤解 vs 実際

| マーケティングの主張 | 実際の実装 |
|---------------------|-----------|
| "Semantic Translation" で変数名を自動リネーム | ❌ 存在しない。代わりに **Context Labeling**（ラベル付与）と **Logic Translator**（数式翻訳・表示のみ） |
| AI が全てを自動修正 | ❌ AI はフォールバックのみ（20%）。ルールベースが主力（80%） |
| Driver X-Ray タブで影響分析 | ❌ タブは非表示。Master-Detail の Logic X-Ray で実装 |
| Maturity Level は未実装 | ✅ 実装済み・表示中 |
| Consistency Check は存在しない | ✅ 存在する（Inconsistent Formula + Inconsistent Value） |

---

## 10. 技術スタック

### フロントエンド
- **Streamlit**: Web UI フレームワーク
- **Pandas**: データフレーム表示
- **streamlit-agraph**: 依存関係グラフ可視化（オプション）

### バックエンド
- **openpyxl**: Excel ファイル解析
- **NetworkX**: 依存関係グラフ構築・循環参照検出
- **OpenAI / Google AI**: Smart Context Recovery（オプション）

### 言語
- **Python 3.8+**
- **i18n サポート**: 日本語・英語

---

## 11. 制約事項

### MVP の制限
1. **Timeline Gaps**: 未実装（複雑すぎる）
2. **Merged Cell Risk**: 簡易版のみ（完全な重複チェックなし）
3. **パフォーマンス**: 
   - 最大10,000行
   - 最大100,000セル
   - 60秒タイムアウト
4. **AI**: フォールバックのみ（主力はルールベース）

### Excel の制約
- **読み取り専用**: Excel ファイルは変更しない
- **パスワード保護**: 非対応
- **マクロ**: 解析しない

---

## 12. まとめ

### 実装済み機能（コアエンジン）
1. ✅ 9種類のリスク検知（Timeline Gaps を除く）
2. ✅ Logic X-Ray（依存関係追跡）
3. ✅ Logic Translator（数式翻訳）
4. ✅ Suggest Fix（Hidden Hardcode のみ）
5. ✅ Context Labeling（AI フォールバック付き）
6. ✅ Maturity Level（ヒューリスティック）
7. ✅ 3-Tier Triage System（Fatal / Integrity / Structural）
8. ✅ Master-Detail UI（Bloomberg Terminal スタイル）

### 存在しない機能
1. ❌ "Semantic Translation"（変数名の自動リネーム）
2. ❌ Driver X-Ray タブ（コードは存在するが非表示）
3. ❌ Timeline Gaps 検出
4. ❌ 自動修正（全て手動修正のみ）

### 哲学
- **Excel は読み取り専用**: 変更しない
- **ルールベース優先**: AI はフォールバック（20%）
- **透明性**: ユーザーが全てを理解・制御可能
- **段階的改善**: 完璧を求めず、80%の精度で十分

---

**レポート終了**
