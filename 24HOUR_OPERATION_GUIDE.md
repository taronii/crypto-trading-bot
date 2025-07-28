# 24時間稼働ガイド

## 🎯 目標
トレーディングボットを24時間365日安定稼働させる

## 📋 稼働オプション比較

### 1. VPS（仮想専用サーバー）【推奨】

#### メリット
- ✅ 24時間安定稼働
- ✅ 電源・ネット接続の心配なし
- ✅ どこからでもアクセス可能
- ✅ 専用リソース

#### デメリット
- ❌ 月額費用（$5-20）
- ❌ 初期設定が必要

#### おすすめVPSサービス
1. **Vultr** - $6/月〜
   - 東京リージョンあり
   - SSD、高速
   
2. **DigitalOcean** - $4/月〜
   - シンプルな管理画面
   - 豊富なチュートリアル

3. **Linode** - $5/月〜
   - 安定性高い
   - 日本語サポート

### 2. クラウドサービス

#### AWS EC2
```bash
# 無料枠: t2.micro（1年間）
# セットアップ手順
1. AWSアカウント作成
2. EC2インスタンス起動（Ubuntu）
3. Pythonとボットをインストール
4. systemdでサービス化
```

#### Google Cloud Platform
```bash
# $300クレジット（90日間）
# f1-micro永久無料枠あり
```

### 3. 自宅PC + リモートアクセス

#### メリット
- ✅ 追加費用なし
- ✅ すぐに始められる
- ✅ 完全なコントロール

#### デメリット
- ❌ 電気代
- ❌ 停電・ネット障害のリスク
- ❌ PCの負荷

## 🚀 VPSセットアップ手順（推奨）

### 1. VPS契約（Vultrの例）

```bash
# 1. Vultrでアカウント作成
# 2. Deploy New Serverを選択
# 3. 以下を選択:
#    - Cloud Compute
#    - Tokyo
#    - Ubuntu 22.04
#    - $6/月プラン
# 4. Deploy Now
```

### 2. 初期設定

```bash
# SSHでログイン
ssh root@your-vps-ip

# システム更新
apt update && apt upgrade -y

# Python環境構築
apt install python3 python3-pip python3-venv git -y

# ユーザー作成
adduser trader
usermod -aG sudo trader
su - trader
```

### 3. ボットのインストール

```bash
# リポジトリをクローン
git clone [your-repo-url] crypto-bot
cd crypto-bot/genius-trading-clean

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# .envファイル作成
nano .env
# APIキーを入力
```

### 4. 自動起動設定（systemd）

```bash
# サービスファイル作成
sudo nano /etc/systemd/system/crypto-bot.service
```

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

[Install]
WantedBy=multi-user.target
```

```bash
# サービス有効化
sudo systemctl enable crypto-bot
sudo systemctl start crypto-bot

# ステータス確認
sudo systemctl status crypto-bot

# ログ確認
sudo journalctl -u crypto-bot -f
```

## 📱 タブレットからの監視

### 1. SSH接続アプリ
- **Termius**（iOS/Android）- 無料
- **Prompt 3**（iOS）- 有料
- **JuiceSSH**（Android）- 無料

### 2. Web監視パネル（オプション）

```python
# monitor_web.py - 簡易Webモニター
from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/status')
def status():
    # ポジション情報を読み込み
    # 現在の状態を返す
    return jsonify({
        'positions': get_current_positions(),
        'balance': get_balance(),
        'pnl': get_pnl()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### 3. プッシュ通知（オプション）

```python
# Telegram通知の例
import requests

def send_telegram_notification(message):
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    requests.post(url, data={
        'chat_id': chat_id,
        'text': message
    })

# 重要なイベントで通知
send_telegram_notification("🎯 新規ポジション: BTCUSDT LONG")
```

## 🛡️ セキュリティ対策

1. **SSH鍵認証を使用**
```bash
# パスワード認証を無効化
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
```

2. **ファイアウォール設定**
```bash
sudo ufw allow 22/tcp
sudo ufw enable
```

3. **定期バックアップ**
```bash
# 設定ファイルのバックアップ
tar -czf backup-$(date +%Y%m%d).tar.gz .env *.py
```

## 💰 コスト比較

| 方法 | 初期費用 | 月額費用 | 安定性 | 設定難易度 |
|------|---------|---------|--------|-----------|
| VPS | $0 | $5-20 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| AWS（無料枠） | $0 | $0（1年） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 自宅PC | $0 | 電気代 | ⭐⭐⭐ | ⭐ |

## 📊 監視チェックリスト

### 毎日確認
- [ ] ボットの稼働状態
- [ ] 現在のポジション
- [ ] 損益状況
- [ ] エラーログ

### 週次確認
- [ ] VPSのリソース使用率
- [ ] バックアップ
- [ ] システムアップデート

## 🚨 トラブルシューティング

### ボットが停止した場合
```bash
# 再起動
sudo systemctl restart crypto-bot

# ログ確認
sudo journalctl -u crypto-bot -n 100
```

### メモリ不足
```bash
# スワップ追加
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## まとめ

**おすすめ構成**：
1. Vultr東京リージョン（$6/月）
2. systemdで自動起動
3. Termiusでタブレット監視
4. Telegram通知で重要イベント把握

これで、どこにいても24時間365日、安定した自動売買が可能になります！