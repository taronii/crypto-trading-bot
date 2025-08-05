#!/bin/bash
# VPS上で直接実行するセットアップスクリプト

echo "📦 VPS直接セットアップ開始..."

# 1. 作業ディレクトリ作成
mkdir -p /opt/crypto-bot/genius-trading-clean
cd /opt/crypto-bot/genius-trading-clean

# 2. 必要なパッケージのインストール
echo "🔧 パッケージインストール中..."
apt update
apt install -y python3 python3-pip python3-venv curl wget

# 3. ファイルを作成（直接貼り付け用）
echo "📝 ファイル作成の準備完了"
echo "次の手順："
echo "1. 各ファイルの内容をコピーして貼り付け"
echo "2. requirements.txtから開始"

# requirements.txt作成
cat > requirements.txt << 'EOF'
pybit==5.6.2
python-dotenv==1.0.0
numpy==1.24.3
requests==2.31.0
urllib3==2.0.7
certifi==2023.7.22
charset-normalizer==3.3.2
idna==3.4
pycryptodome==3.19.0
websocket-client==1.6.4
EOF

echo "✅ requirements.txt作成完了"

# 4. Python環境セットアップ
echo "🐍 Python仮想環境作成中..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "✅ 基本セットアップ完了！"
echo "次は、Pythonファイルを手動で作成してください。"