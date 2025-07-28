# 🚀 GitHub経由でVPSにファイルをアップロードする方法

## 📝 ステップ1: GitHubアカウント作成（3分）

### 1-1. GitHubにアクセス
https://github.com/

### 1-2. Sign up（サインアップ）をクリック
```
Username: 好きなユーザー名（例：cryptobot2025）
Email: メールアドレス
Password: パスワード（15文字以上推奨）
```

### 1-3. メール認証
- 届いたメールの認証コードを入力
- アカウント作成完了！

## 📦 ステップ2: リポジトリ作成（2分）

### 2-1. 新規リポジトリ作成
1. 右上の「+」→「New repository」をクリック
2. 以下を設定：
```
Repository name: crypto-trading-bot
Description: Bybit trading bot（任意）
Public/Private: Private（プライベート推奨）
Initialize: チェックを外す
```
3. 「Create repository」をクリック

## 📤 ステップ3: ファイルをアップロード（5分）

### 方法A: ブラウザで直接アップロード（簡単！）

1. 作成したリポジトリページで「uploading an existing file」をクリック
2. 以下のフォルダの中身をドラッグ＆ドロップ：
   ```
   /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean/
   ```
3. 「Commit changes」をクリック

### 方法B: コマンドラインでアップロード

**Macのターミナルで**：
```bash
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean

# Gitの初期設定（初回のみ）
git init
git add .
git commit -m "Initial commit"

# GitHubに接続
git remote add origin https://github.com/あなたのユーザー名/crypto-trading-bot.git
git branch -M main
git push -u origin main
```

ユーザー名とパスワードを聞かれたら：
- Username: GitHubのユーザー名
- Password: GitHubのパスワード

## 🔐 ステップ4: アクセストークン作成（プライベートリポジトリの場合）

### 4-1. Personal Access Token作成
1. GitHub右上のプロフィール→「Settings」
2. 左メニューの一番下「Developer settings」
3. 「Personal access tokens」→「Tokens (classic)」
4. 「Generate new token」→「Generate new token (classic)」
5. 以下を設定：
```
Note: VPS Access
Expiration: 30 days
Scopes: ☑ repo（全部にチェック）
```
6. 「Generate token」をクリック
7. **表示されたトークンをコピー**（一度しか表示されません！）

## 💻 ステップ5: VPSからダウンロード（3分）

### 5-1. Xserverのコンソールに戻る

### 5-2. GitHubからクローン

**パブリックリポジトリの場合**：
```bash
cd /opt/crypto-bot
git clone https://github.com/あなたのユーザー名/crypto-trading-bot.git genius-trading-clean
```

**プライベートリポジトリの場合**：
```bash
cd /opt/crypto-bot
git clone https://ユーザー名:トークン@github.com/ユーザー名/crypto-trading-bot.git genius-trading-clean
```

例：
```bash
git clone https://cryptobot2025:ghp_abcdef123456@github.com/cryptobot2025/crypto-trading-bot.git genius-trading-clean
```

### 5-3. 確認
```bash
cd genius-trading-clean
ls -la
```

ファイルが表示されれば成功！

## 🚨 セキュリティ注意事項

### やってはいけないこと
- ❌ APIキーをGitHubにアップロードしない
- ❌ .envファイルはアップロードしない
- ❌ パスワードを含むファイルは除外

### .gitignoreファイル作成
アップロード前に以下のファイルを作成：
```bash
nano .gitignore
```

内容：
```
.env
*.log
__pycache__/
*.pyc
.DS_Store
```

## ✅ 完了後の流れ

1. VPSでファイルを確認
2. Python環境構築に進む
3. 使い終わったらGitHubリポジトリは削除してもOK

## 🆘 トラブルシューティング

### git cloneでエラーが出る場合
```bash
# HTTPSの代わりにSSHを試す
git clone git@github.com:ユーザー名/crypto-trading-bot.git genius-trading-clean
```

### トークンが無効と言われる場合
- トークンの権限（repo）を確認
- 新しいトークンを作成し直す

---

これで確実にファイルをVPSに転送できます！🎉