# 🎬 デモ録画 - 実行手順（日本語）

## 📋 準備（初回のみ）

### ステップ1: 新しいターミナルを開く

Streamlitが動いているターミナルとは**別の新しいターミナル**を開いてください。

### ステップ2: プロジェクトディレクトリに移動

```bash
cd /path/to/your/lumen/project
```

### ステップ3: 仮想環境をアクティベート（使用している場合）

```bash
# venvを使っている場合
source venv/bin/activate

# または
. venv/bin/activate
```

### ステップ4: 依存パッケージをインストール

```bash
pip install playwright Pillow
```

### ステップ5: Chromiumブラウザをインストール

```bash
playwright install chromium
```

### ステップ6: ffmpegをインストール（オプション - 高品質GIF用）

```bash
brew install ffmpeg
```

## 🎥 録画実行

### Streamlitが動いていることを確認

別のターミナルで `streamlit run app.py` が動いていることを確認してください。

### 録画スクリプトを実行

```bash
python record_demo.py
```

### 実行中の表示

```
🎬 Starting Lumen Demo Recording...
============================================================
🔍 Checking dependencies...
   ✅ Playwright installed
   ✅ Pillow installed

============================================================
📱 Starting Streamlit app...
⏳ Waiting for app to initialize...
🌐 Launching browser (1280x720)...
🎥 Recording started...

📤 Scene 1: File upload...
⚙️  Scene 2: Analysis in progress...
📊 Scene 3: Viewing results...
🔍 Scene 4: Examining risk details...
📋 Scene 5: Reviewing details...
⬆️  Scene 6: Return to overview...

✅ Recording complete!
💾 Saving video...
🛑 Stopping Streamlit app...

🔄 Converting to output formats...
============================================================
📹 Creating optimized WebM...
   ✅ Created: lumen_demo.webm
🎞️  Creating GIF (this may take a moment)...
   ✅ Created: lumen_demo.gif

📦 Output Files:
============================================================
   WebM: lumen_demo.webm (2.34 MB)
   GIF:  lumen_demo.gif (15.67 MB)

🎉 Demo recording complete!
```

## 📦 出力ファイル

録画が完了すると、プロジェクトルートに以下のファイルが生成されます：

- `lumen_demo.webm` - Web用（軽量・高品質）
- `lumen_demo.gif` - 汎用（最大互換性）

## ⚠️ 注意事項

### Streamlitについて

- `record_demo.py` は**自動的にStreamlitを起動・停止**します
- 既に動いているStreamlitがあっても問題ありません
- スクリプトは別のポート（8501）で一時的に起動します

### 録画中

- 録画中（約30秒）は他の作業をしても大丈夫です
- バックグラウンドで自動実行されます

## 🔧 トラブルシューティング

### エラー: "Port 8501 is already in use"

既存のStreamlitを停止してから実行：

```bash
# 既存のStreamlitを停止
lsof -ti:8501 | xargs kill -9

# 再実行
python record_demo.py
```

### エラー: "playwright not found"

```bash
pip install playwright
playwright install chromium
```

### GIFが生成されない

ffmpegがない場合、WebMのみ生成されます。GIFも必要な場合：

```bash
brew install ffmpeg
```

### 録画が真っ黒

Streamlitの起動待機時間を延長：

`record_demo.py` の58行目を編集：

```python
await asyncio.sleep(10)  # 8 → 10に変更
```

## 💡 ヒント

### 複数回録画する

自動化されているので、気に入るまで何度でも実行できます：

```bash
python record_demo.py
# 確認
# 気に入らなければ再実行
python record_demo.py
```

### カスタマイズ

シナリオを変更したい場合は `record_demo.py` を編集してください。
詳細は `DEMO_RECORDING_GUIDE.md` を参照。

---

**所要時間**: 初回 5-10分（インストール含む）、2回目以降 30秒
