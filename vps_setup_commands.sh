#!/bin/bash
# VPS上で実行するセットアップコマンド集

# 1. システムアップデート
echo "📦 システムアップデート中..."
apt update && apt upgrade -y

# 2. 必要なパッケージインストール
echo "🔧 必要なパッケージをインストール中..."
apt install -y python3 python3-pip python3-venv git curl wget

# 3. タイムゾーン設定
echo "🕐 タイムゾーンを日本時間に設定..."
timedatectl set-timezone Asia/Tokyo

# 4. 作業ディレクトリ作成
echo "📁 作業ディレクトリを作成..."
mkdir -p /opt/crypto-bot/genius-trading-clean
cd /opt/crypto-bot/genius-trading-clean

# 5. Python仮想環境の作成
echo "🐍 Python仮想環境を作成..."
python3 -m venv venv
source venv/bin/activate

echo "✅ VPS初期セットアップ完了！"
echo "次は、ローカルマシンからファイルを転送してください。"