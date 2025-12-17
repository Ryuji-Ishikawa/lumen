# GitHub連携セットアップガイド

## ✅ ローカルGit初期化完了

初回コミット完了：
- コミットID: `e34e158`
- 202ファイル、49,829行追加
- Phase 1完了状態を保存

---

## 次のステップ：GitHubリポジトリ作成

### オプション1：GitHub Web UIで作成（推奨）

1. **GitHubにログイン**
   - https://github.com にアクセス

2. **新規リポジトリ作成**
   - 右上の「+」→「New repository」
   - Repository name: `lumen-mvp`
   - Description: `Excel Model Audit & Diagnostic System - Risk Review + Explanation Mode`
   - Visibility: **Private**（推奨）
   - ✅ **DO NOT** initialize with README, .gitignore, or license（既にローカルにあるため）

3. **リモート接続**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/lumen-mvp.git
   git branch -M main
   git push -u origin main
   ```

---

### オプション2：GitHub CLIで作成（高速）

```bash
# GitHub CLIインストール（まだの場合）
brew install gh

# GitHub認証
gh auth login

# リポジトリ作成 & プッシュ（1コマンド）
gh repo create lumen-mvp --private --source=. --remote=origin --push
```

---

## 今後の開発フロー

### Phase 2の各タスク実装時：

```bash
# Task 6開始前
git checkout -b feature/task-6-target-selection

# 実装 & テスト
# ... コード変更 ...

# コミット
git add .
git commit -m "Task 6: Implement Target Selection UI

- Add KPI candidate dropdown
- Filter: 売上 or Revenue
- Limit to top 10
- Handle no candidates case
- Tests passing"

# GitHubにプッシュ
git push origin feature/task-6-target-selection

# 完了後、mainにマージ
git checkout main
git merge feature/task-6-target-selection
git push origin main
```

---

## ブランチ戦略（推奨）

```
main (本番安定版)
  ├── feature/task-6-target-selection
  ├── feature/task-7-basic-tree-display
  ├── feature/task-8-aggrid-tree
  └── ...
```

**ルール**:
- `main`: 常に動作する状態を保つ
- `feature/*`: 各タスクごとに作成
- タスク完了後に `main` にマージ

---

## .gitignoreの確認

既に作成済み：
- ✅ `venv/` - 仮想環境除外
- ✅ `__pycache__/` - Pythonキャッシュ除外
- ✅ `.DS_Store` - macOSファイル除外
- ✅ `*.webm` - デモ録画除外
- ✅ `.streamlit/secrets.toml` - APIキー除外

---

## バックアップ戦略

### 毎日の作業終了時：

```bash
# 変更をコミット
git add .
git commit -m "Daily checkpoint: [作業内容]"

# GitHubにプッシュ（バックアップ）
git push origin main
```

### 重要なマイルストーン時：

```bash
# タグ付け
git tag -a v1.0-phase1-complete -m "Phase 1: Foundation Complete"
git push origin v1.0-phase1-complete
```

---

## トラブル時のロールバック

### 最新コミットに戻す：

```bash
# 変更を破棄
git reset --hard HEAD

# GitHubから最新を取得
git pull origin main
```

### 特定のコミットに戻す：

```bash
# コミット履歴確認
git log --oneline

# 特定のコミットに戻す
git reset --hard e34e158  # Phase 1完了時点

# GitHubに強制プッシュ（注意！）
git push origin main --force
```

---

## 現在の状態

```
✅ ローカルGit初期化完了
✅ 初回コミット完了（Phase 1完了状態）
⏳ GitHubリポジトリ作成待ち
⏳ リモート接続待ち
```

---

## 推奨アクション

1. **今すぐ**: GitHubリポジトリ作成 & プッシュ
2. **Phase 2開始前**: ブランチ作成（`feature/task-6-target-selection`）
3. **各タスク完了後**: コミット & プッシュ
4. **毎日終了時**: バックアッププッシュ

---

**メリット**:
- ✅ いつでも過去の状態に戻れる
- ✅ 変更履歴が明確
- ✅ 複数デバイスで作業可能
- ✅ コードレビューが容易
- ✅ パイロットユーザーへの安心感

**デメリット**:
- ❌ なし（Privateリポジトリなので安全）
