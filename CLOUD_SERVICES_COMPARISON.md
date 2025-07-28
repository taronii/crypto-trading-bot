# クラウドサービス比較ガイド - 24時間ボット稼働

## 🚨 重要：サーバーレスは不適切

### なぜCloud Run/Lambda/Functionsが使えないか

```
通常のWebアプリ：
リクエスト → 処理（数秒） → レスポンス → 終了 ✅

トレーディングボット：
起動 → 無限ループ（24時間） → 5分ごとに処理 ❌
```

**制限事項**：
- Cloud Run: 最大60分
- AWS Lambda: 最大15分  
- Cloud Functions: 最大9分

## ✅ ボットに適したサービス

### 1. Google Compute Engine (GCE) 【Googleで最適】

**特徴**：
- 通常のVMインスタンス
- 24時間稼働可能
- 無料枠あり（条件付き）

**セットアップ**：
```bash
# 1. GCPコンソールでVMインスタンス作成
# - e2-micro（無料枠対象）
# - リージョン: us-central1など
# - Ubuntu 22.04

# 2. SSHで接続
gcloud compute ssh instance-name

# 3. ボットをインストール（VPSと同じ手順）
```

**コスト**：
- e2-micro: 月額$10程度
- 無料枠: 月間720時間（条件あり）

### 2. Google Kubernetes Engine (GKE) Autopilot

**特徴**：
- コンテナベース
- 自動スケーリング
- 高可用性

**Dockerfile作成**：
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "genius_multi_trading_v2_with_trading.py"]
```

**デプロイ**：
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crypto-bot
  template:
    metadata:
      labels:
        app: crypto-bot
    spec:
      containers:
      - name: bot
        image: gcr.io/YOUR_PROJECT/crypto-bot
        env:
        - name: BYBIT_API_KEY
          valueFrom:
            secretKeyRef:
              name: bybit-secrets
              key: api-key
```

**コスト**: 月額$30〜

### 3. その他のオプション

#### AWS EC2
```bash
# 無料枠: t2.micro（1年間）
# セットアップはGCEと同様
```

#### Azure VM
```bash
# $200クレジット（30日間）
# B1sインスタンス: 月額$15
```

#### DigitalOcean Droplet
```bash
# シンプルで使いやすい
# $4/月〜
# 初回$200クレジット
```

## 🎯 推奨構成

### 初心者向け: VPS（DigitalOcean/Vultr）
**理由**：
- シンプル
- 固定料金
- 豊富なチュートリアル

### 中級者向け: Google Compute Engine
**理由**：
- Googleエコシステム
- 無料枠の可能性
- 高い信頼性

### 上級者向け: Kubernetes（GKE/EKS）
**理由**：
- スケーラビリティ
- 自動復旧
- CI/CD統合

## 💰 コスト比較（月額）

| サービス | 最小構成 | 推奨構成 | 備考 |
|---------|---------|----------|------|
| VPS (Vultr) | $6 | $12 | シンプル |
| Google Compute Engine | $10 | $25 | 無料枠あり |
| AWS EC2 | $0（1年） | $20 | 初年度無料 |
| DigitalOcean | $4 | $12 | $200クレジット |
| Heroku | $7 | - | 制限あり |

## 🚀 Google Compute Engineでの実装例

### 1. インスタンス作成
```bash
gcloud compute instances create crypto-bot \
  --machine-type=e2-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=10GB \
  --zone=us-central1-a
```

### 2. 起動スクリプト
```bash
#!/bin/bash
# startup-script.sh

# 依存関係インストール
apt-get update
apt-get install -y python3-pip git

# ボットのクローン
git clone https://github.com/YOUR_REPO/crypto-bot.git
cd crypto-bot

# 環境設定
pip3 install -r requirements.txt

# systemdサービス作成
cat > /etc/systemd/system/crypto-bot.service << EOF
[Unit]
Description=Crypto Trading Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/crypto-bot
ExecStart=/usr/bin/python3 genius_multi_trading_v2_with_trading.py
Restart=always
Environment="BYBIT_API_KEY=${BYBIT_API_KEY}"
Environment="BYBIT_API_SECRET=${BYBIT_API_SECRET}"

[Install]
WantedBy=multi-user.target
EOF

# サービス開始
systemctl enable crypto-bot
systemctl start crypto-bot
```

### 3. 監視設定
```python
# Cloud Loggingへの出力
import google.cloud.logging

client = google.cloud.logging.Client()
client.setup_logging()

# これで自動的にCloud Loggingに記録される
```

## 📱 モバイルからの管理

### Google Cloud Consoleアプリ
- VM の開始/停止
- ログ確認
- リソース監視

### SSH接続
```bash
# Cloud Shell（ブラウザから）
gcloud compute ssh crypto-bot

# または Termius等のアプリから
ssh user@EXTERNAL_IP
```

## 🔒 セキュリティ

### 1. ファイアウォール設定
```bash
gcloud compute firewall-rules create allow-ssh \
  --allow tcp:22 \
  --source-ranges YOUR_IP/32
```

### 2. シークレット管理
```bash
# Secret Manager使用
gcloud secrets create bybit-api-key \
  --data-file=api-key.txt
```

### 3. 最小権限の原則
- 専用サービスアカウント作成
- 必要な権限のみ付与

## まとめ

**Cloud Runは不適切**ですが、以下が良い選択肢です：

1. **簡単さ重視** → VPS（Vultr/DigitalOcean）
2. **Google好き** → Compute Engine  
3. **無料枠狙い** → AWS EC2（1年）
4. **プロ仕様** → Kubernetes

どれを選んでも、月額$5-25で安定した24時間稼働が可能です！