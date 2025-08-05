# 📚 X Server VPS デプロイメント完全ガイド

## 📋 前提条件

- **VPS情報**（マニュアルより）
  - IPアドレス: 162.43.24.224
  - OS: Ubuntu 22.04 LTS
  - プラン: 2GB
  - ユーザー: root

## 🚀 デプロイメント手順

### ステップ1: ローカルでの準備

#### 1.1 必要ファイルの確認
```bash
# 現在のディレクトリで実行
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean

# 必要なファイルがあるか確認
ls -la
```

必須ファイル:
- `genius_multi_trading_v2_with_trading.py` （メインスクリプト）
- `genius_dynamic_exit_strategy.py` （決済戦略）
- `genius_exit_strategy.py` （決済戦略）
- `services/bybit_service.py` （API連携）
- `requirements.txt` （依存関係）
- `.env` （API設定）

#### 1.2 .envファイルの安全な準備
```bash
# .envファイルの内容を確認（APIキーが含まれているため注意）
cat .env

# バックアップを作成
cp .env .env.backup
```

### ステップ2: VPSへの接続

#### 2.1 SSH接続
```bash
# ターミナルから接続
ssh root@162.43.24.224

# パスワードを入力（Xserverで設定したもの）
```

#### 2.2 作業ディレクトリの作成
```bash
# VPS上で実行
mkdir -p /opt/crypto-bot/genius-trading-clean
cd /opt/crypto-bot/genius-trading-clean
```

### ステップ3: VPS環境のセットアップ

#### 3.1 システムの更新
```bash
# VPS上で実行
apt update && apt upgrade -y
```

#### 3.2 Python環境の準備
```bash
# Python3とpipのインストール（既にインストール済みの可能性あり）
apt install -y python3 python3-pip python3-venv

# バージョン確認
python3 --version  # Python 3.10以上が必要
```

#### 3.3 仮想環境の作成
```bash
# VPS上で実行
cd /opt/crypto-bot/genius-trading-clean
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate
```

### ステップ4: ファイルのアップロード

#### 4.1 ローカルからVPSへファイル転送

**新しいターミナルウィンドウを開いて**、ローカルマシンで実行:

```bash
# ローカルのプロジェクトディレクトリに移動
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean

# 必要なファイルをVPSに転送
# メインファイル
scp genius_multi_trading_v2_with_trading.py root@162.43.24.224:/opt/crypto-bot/genius-trading-clean/
scp genius_dynamic_exit_strategy.py root@162.43.24.224:/opt/crypto-bot/genius-trading-clean/
scp genius_exit_strategy.py root@162.43.24.224:/opt/crypto-bot/genius-trading-clean/
scp requirements.txt root@162.43.24.224:/opt/crypto-bot/genius-trading-clean/

# servicesディレクトリを作成してファイルを転送
ssh root@162.43.24.224 "mkdir -p /opt/crypto-bot/genius-trading-clean/services"
scp services/__init__.py root@162.43.24.224:/opt/crypto-bot/genius-trading-clean/services/
scp services/bybit_service.py root@162.43.24.224:/opt/crypto-bot/genius-trading-clean/services/

# .envファイルを転送（重要：APIキーが含まれる）
scp .env root@162.43.24.224:/opt/crypto-bot/genius-trading-clean/
```

### ステップ5: 依存関係のインストール

VPSのターミナルに戻って実行:

```bash
# 仮想環境が有効化されていることを確認
cd /opt/crypto-bot/genius-trading-clean
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### ステップ6: 動作テスト

#### 6.1 手動実行テスト
```bash
# VPS上で実行
cd /opt/crypto-bot/genius-trading-clean
source venv/bin/activate

# テスト実行（Ctrl+Cで停止）
python3 genius_multi_trading_v2_with_trading.py
```

#### 6.2 権限の設定
```bash
# 実行権限を付与
chmod +x genius_multi_trading_v2_with_trading.py

# .envファイルの権限を制限（セキュリティ対策）
chmod 600 .env
```

### ステップ7: Systemdサービスの設定

#### 7.1 サービスファイルの作成
```bash
# VPS上で実行
nano /etc/systemd/system/crypto-bot.service
```

以下の内容を貼り付け:
```ini
[Unit]
Description=Crypto Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/crypto-bot/genius-trading-clean
Environment="PATH=/opt/crypto-bot/genius-trading-clean/venv/bin"
ExecStart=/opt/crypto-bot/genius-trading-clean/venv/bin/python /opt/crypto-bot/genius-trading-clean/genius_multi_trading_v2_with_trading.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

保存: `Ctrl+X` → `Y` → `Enter`

#### 7.2 サービスの有効化と起動
```bash
# systemdをリロード
systemctl daemon-reload

# サービスを有効化（自動起動）
systemctl enable crypto-bot

# サービスを開始
systemctl start crypto-bot

# 状態確認
systemctl status crypto-bot
```

### ステップ8: ログの確認

```bash
# リアルタイムログを確認
journalctl -u crypto-bot -f

# 最新50行を確認
journalctl -u crypto-bot -n 50

# 今日のログを確認
journalctl -u crypto-bot --since today
```

### ステップ9: セキュリティ設定

#### 9.1 ファイアウォール設定（必要に応じて）
```bash
# UFWが有効な場合
ufw allow 22/tcp  # SSH接続を許可
ufw enable
```

#### 9.2 定期バックアップの設定
```bash
# バックアップスクリプトを作成
nano /opt/crypto-bot/backup.sh
```

内容:
```bash
#!/bin/bash
cd /opt/crypto-bot
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz genius-trading-clean/.env
find . -name "backup-*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /opt/crypto-bot/backup.sh

# cronで毎日実行
crontab -e
# 以下を追加
0 2 * * * /opt/crypto-bot/backup.sh
```

## 🔧 トラブルシューティング

### 問題1: ModuleNotFoundError
```bash
# 依存関係を再インストール
cd /opt/crypto-bot/genius-trading-clean
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### 問題2: Permission denied
```bash
# 権限を確認
ls -la /opt/crypto-bot/genius-trading-clean/
# 必要に応じて権限を修正
chmod -R 755 /opt/crypto-bot/genius-trading-clean/
```

### 問題3: サービスが起動しない
```bash
# エラーログを確認
journalctl -u crypto-bot -n 100 | grep -i error

# 手動で実行してエラーを確認
cd /opt/crypto-bot/genius-trading-clean
source venv/bin/activate
python3 genius_multi_trading_v2_with_trading.py
```

## 📱 運用開始後の確認

### 日常的な監視コマンド
```bash
# サービス状態
systemctl status crypto-bot

# ログ確認（リアルタイム）
journalctl -u crypto-bot -f

# ポジション確認スクリプトがある場合
cd /opt/crypto-bot/genius-trading-clean
source venv/bin/activate
python3 check_current_positions.py
```

### 停止・再起動
```bash
# 一時停止
systemctl stop crypto-bot

# 再起動
systemctl restart crypto-bot

# 完全停止（自動起動も無効化）
systemctl stop crypto-bot
systemctl disable crypto-bot
```

## ⚠️ 重要な注意事項

1. **APIキーのセキュリティ**
   - `.env`ファイルの権限は必ず600に設定
   - 定期的にAPIキーを更新

2. **資金管理**
   - 初回は少額でテスト運用
   - ログを毎日確認

3. **緊急時の対応**
   - `systemctl stop crypto-bot`で即座に停止
   - Bybitアプリからも手動決済可能

4. **アップデート時**
   - 必ずサービスを停止してから更新
   - バックアップを取ってから実施

---

デプロイ完了後は、`systemctl status crypto-bot`で正常に動作していることを確認してください。