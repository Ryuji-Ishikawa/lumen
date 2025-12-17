# 🎬 Lumen Demo Recording Guide

プロフェッショナルなデモGIF/動画を自動生成するガイド

## 📋 必要な準備

### 1. 依存パッケージのインストール

```bash
# Playwright (ブラウザ自動操作)
pip install playwright
playwright install chromium

# Pillow (GIF処理 - オプション)
pip install Pillow

# ffmpeg (高品質変換 - 推奨)
brew install ffmpeg  # macOS
```

### 2. アプリケーションの準備

- `Sample_Business Plan.xlsx` がプロジェクトルートにあることを確認
- Streamlitアプリが正常に動作することを確認

## 🎥 録画の実行

### 基本的な使い方

```bash
python record_demo.py
```

### 実行フロー

1. **Streamlitアプリ起動** (自動)
2. **ブラウザ起動** (1280x720 HD)
3. **デモシナリオ実行** (~27秒)
   - ファイルアップロード
   - リスク分析待機
   - 結果表示
   - リスク詳細確認
   - スクロール操作
4. **動画保存** (WebM形式)
5. **形式変換** (GIF + 最適化WebM)
6. **Streamlitアプリ停止** (自動)

## 📦 出力ファイル

### lumen_demo.webm
- **用途**: Webサイト埋め込み (推奨)
- **特徴**: 高品質、小サイズ、モダンブラウザ対応
- **サイズ**: ~2-5 MB

### lumen_demo.gif
- **用途**: 最大互換性 (メール、ドキュメント等)
- **特徴**: どこでも表示可能
- **サイズ**: ~10-20 MB

## 🎨 カスタマイズ

### シナリオの調整

`record_demo.py` の `record_demo()` 関数内で調整可能：

```python
# 待機時間の調整
await asyncio.sleep(2)  # 秒数を変更

# スクロール位置の調整
await page.evaluate("window.scrollTo({ top: 400, behavior: 'smooth' })")

# マウス移動速度の調整
await smooth_click(page, x, y, duration_ms=800)  # ミリ秒
```

### 画面サイズの変更

```python
viewport={'width': 1280, 'height': 720}  # お好みのサイズに変更
```

## 🔧 トラブルシューティング

### Streamlitが起動しない

```bash
# ポート8501が使用中の場合
lsof -ti:8501 | xargs kill -9
```

### ffmpegがない場合

- WebMファイルは生成されます
- GIF変換がスキップされます
- 必要に応じて `brew install ffmpeg` でインストール

### 録画が真っ黒になる場合

- Streamlitの起動待機時間を延長:
  ```python
  await asyncio.sleep(10)  # 8秒 → 10秒に変更
  ```

### ファイルアップロードが動作しない

- サンプルファイルのパスを確認
- Streamlitのfile_uploaderセレクタを確認

## 💡 ベストプラクティス

### 高品質な録画のために

1. **録画前にアプリをテスト実行**
   ```bash
   streamlit run app.py
   ```

2. **不要なプロセスを終了**
   - CPUリソースを確保

3. **複数回録画して最良のものを選択**
   - 自動化されているので簡単に再実行可能

### Web掲載時の推奨

```html
<!-- WebM (推奨) -->
<video autoplay loop muted playsinline width="1280">
  <source src="lumen_demo.webm" type="video/webm">
  <img src="lumen_demo.gif" alt="Lumen Demo">
</video>

<!-- GIF (フォールバック) -->
<img src="lumen_demo.gif" alt="Lumen Demo" width="1280">
```

## 🎯 デモシナリオ詳細

| 時間 | シーン | 内容 |
|------|--------|------|
| 0-3s | イントロ | アプリ表示 |
| 3-8s | アップロード | Excelファイル選択 |
| 8-12s | 分析 | リスク分析実行 |
| 12-16s | 結果表示 | スクロールして結果確認 |
| 16-20s | 詳細確認 | リスク項目をクリック |
| 20-24s | 詳細閲覧 | 詳細情報をスクロール |
| 24-27s | 完了 | トップに戻る |

## 🚀 高度な使い方

### AI機能を含めたデモ

将来的にAI機能を追加する場合：

```python
# AI説明ボタンをクリック
ai_button = await page.query_selector('button:has-text("AI")')
if ai_button:
    box = await ai_button.bounding_box()
    await smooth_click(page, box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    await asyncio.sleep(3)
```

### 複数言語版の作成

```python
# 言語切り替え
lang_selector = await page.query_selector('select')
await lang_selector.select_option('en')  # 英語版
```

## 📞 サポート

問題が発生した場合：

1. `demo_recordings/` フォルダの内容を確認
2. Streamlitログを確認
3. Playwrightのスクリーンショット機能でデバッグ

---

**作成日**: 2024-12-09  
**対象バージョン**: Lumen MVP  
**録画時間**: ~30秒以内  
**出力形式**: WebM + GIF
