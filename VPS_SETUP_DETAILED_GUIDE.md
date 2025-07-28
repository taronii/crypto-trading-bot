# 🚀 VPS導入 完全ガイド（初心者向け）

## 📋 事前準備

### 必要なもの
- クレジットカード（月額支払い用）
- メールアドレス
- 現在のボットファイル一式
- APIキー情報（.envファイル）

## 🎯 ステップ1: VPSサービスの選択と契約

### おすすめ: Vultr（ヴァルチャー）

#### 1-1. アカウント作成
1. https://www.vultr.com/ にアクセス
2. 「Sign Up」をクリック
3. メールアドレスとパスワードを入力
4. メール認証を完了

#### 1-2. 支払い情報の登録
1. ダッシュボードで「Billing」をクリック
2. クレジットカード情報を入力
3. 初回は$10〜チャージ（余った分は翌月に繰り越し）

#### 1-3. サーバー作成
1. 「Deploy New Server」をクリック
2. 以下を選択：

```
Server Type: Cloud Compute
Location: Tokyo（東京）
Server Size: $12/月プラン（2GB RAM推奨）
Operating System: Ubuntu 22.04 LTS
```

3. 「Deploy Now」をクリック
4. 1-2分でサーバー準備完了

#### 1-4. 接続情報の確認
```
IP Address: xxx.xxx.xxx.xxx（メモする）
Username: root
Password: xxxxxxxxxxx（メモする）
```

## 🖥️ ステップ2: VPSへの接続

### Mac/Linuxの場合
```bash
# ターミナルを開いて
ssh root@あなたのIPアドレス
# パスワードを入力
```

### Windowsの場合
1. PowerShellを開く
2. 同じコマンドを実行

### 初回接続時
```
Are you sure you want to continue connecting? 
→ yes と入力
```

## 🔧 ステップ3: VPSの初期設定

### 3-1. システム更新
```bash
apt update && apt upgrade -y
# 5分程度かかります
```

### 3-2. 必要なソフトウェアのインストール
```bash
# Python関連
apt install python3 python3-pip python3-venv git nano -y

# 追加パッケージ
apt install htop tmux -y
```

### 3-3. 作業用ユーザー作成（セキュリティ向上）
```bash
# ユーザー作成
adduser trader
# パスワードを設定（メモする）
# その他の情報は空欄でEnter

# sudo権限付与
usermod -aG sudo trader

# ユーザー切り替え
su - trader
```

## 📦 ステップ4: ボットのインストール

### 4-1. ボットファイルのアップロード

#### 方法A: GitHubを使う場合（推奨）
```bash
# もしGitHubにアップロード済みなら
git clone https://github.com/あなたのユーザー名/リポジトリ名.git crypto-bot
```

#### 方法B: 直接アップロード
```bash
# VPS側で準備
mkdir -p crypto-bot/genius-trading-clean
cd crypto-bot/genius-trading-clean
```

**別のターミナル（ローカルMac）で**:
```bash
# ファイルをVPSにコピー
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean

# 全ファイルをアップロード
scp -r * trader@VPSのIP:~/crypto-bot/genius-trading-clean/
```

### 4-2. Python環境のセットアップ
```bash
# VPSで実行
cd ~/crypto-bot/genius-trading-clean

# 仮想環境作成
python3 -m venv venv

# 仮想環境有効化
source venv/bin/activate

# 依存関係インストール
pip install --upgrade pip
pip install -r requirements.txt
```

### 4-3. 環境設定（.env）
```bash
# .envファイル作成
nano .env
```

以下を入力（あなたのAPIキーに置き換え）:
```
BYBIT_API_KEY=あなたのAPIキー
BYBIT_API_SECRET=あなたのAPIシークレット
```

保存: Ctrl+X → Y → Enter

### 4-4. 動作テスト
```bash
# テストスクリプト実行
python test_setup.py

# 成功したら本番実行（一旦Ctrl+Cで止める）
python genius_multi_trading_v2_with_trading.py
```

## 🚀 ステップ5: 自動起動設定

### 5-1. systemdサービス作成
```bash
# rootユーザーに切り替え
sudo su -

# サービスファイル作成
nano /etc/systemd/system/crypto-bot.service
```

以下を貼り付け:
```ini
[Unit]
Description=Crypto Trading Bot
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/home/trader/crypto-bot/genius-trading-clean
Environment="PATH=/home/trader/crypto-bot/genius-trading-clean/venv/bin"
ExecStart=/home/trader/crypto-bot/genius-trading-clean/venv/bin/python genius_multi_trading_v2_with_trading.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

保存: Ctrl+X → Y → Enter

### 5-2. サービスの有効化と起動
```bash
# サービス有効化（自動起動）
systemctl enable crypto-bot

# サービス開始
systemctl start crypto-bot

# 状態確認
systemctl status crypto-bot
```

緑色で「active (running)」と表示されればOK！

### 5-3. ログの確認
```bash
# リアルタイムログ確認
journalctl -u crypto-bot -f

# 過去のログ確認
journalctl -u crypto-bot --since "1 hour ago"
```

## 📱 ステップ6: タブレット/スマホからの監視

### 6-1. SSHアプリのインストール

**iOS**: Termius（無料）
**Android**: JuiceSSH（無料）

### 6-2. 接続設定
```
Host: VPSのIPアドレス
Port: 22
Username: trader
Password: 設定したパスワード
```

### 6-3. よく使うコマンド
```bash
# ログ確認
sudo journalctl -u crypto-bot -f

# サービス再起動
sudo systemctl restart crypto-bot

# サービス停止
sudo systemctl stop crypto-bot

# サービス開始
sudo systemctl start crypto-bot
```

## 🛡️ ステップ7: セキュリティ設定

### 7-1. ファイアウォール設定
```bash
# UFW（ファイアウォール）設定
sudo ufw allow 22/tcp
sudo ufw --force enable
```

### 7-2. 定期的なバックアップ
```bash
# バックアップスクリプト作成
nano ~/backup.sh
```

内容:
```bash
#!/bin/bash
cd ~/crypto-bot/genius-trading-clean
tar -czf ~/backup-$(date +%Y%m%d).tar.gz .env *.py
```

実行権限付与:
```bash
chmod +x ~/backup.sh
```

## ✅ 完了チェックリスト

- [ ] VPSが起動している
- [ ] SSHで接続できる
- [ ] ボットがインストールされている
- [ ] systemdサービスが動作している
- [ ] タブレットから接続できる
- [ ] ログが正常に出力されている

## 🆘 トラブルシューティング

### ボットが起動しない
```bash
# エラーログ確認
sudo journalctl -u crypto-bot -n 50

# 手動で実行してエラー確認
cd ~/crypto-bot/genius-trading-clean
source venv/bin/activate
python genius_multi_trading_v2_with_trading.py
```

### 接続できない
- IPアドレスが正しいか確認
- ユーザー名とパスワードを確認
- VPSが起動しているか確認

### パッケージエラー
```bash
# 仮想環境で再インストール
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 📞 サポート

Vultrサポート: https://www.vultr.com/docs/
一般的なLinuxコマンド: 「Ubuntu コマンド」で検索

---

これで24時間365日、自動売買が動き続けます！🚀