#!/bin/bash
# 手動デプロイスクリプト（パスワード認証用）

VPS_IP="162.43.33.141"
VPS_USER="root"
REMOTE_DIR="/opt/crypto-bot/genius-trading-clean"

echo "📦 VPSにディレクトリを作成..."
ssh ${VPS_USER}@${VPS_IP} "mkdir -p ${REMOTE_DIR}/services"

echo "📤 ファイルを転送中..."
echo "各ファイルでパスワードの入力が必要です"

# メインファイル
echo "1/7: genius_multi_trading_v2_with_trading.py"
scp genius_multi_trading_v2_with_trading.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/

echo "2/7: genius_dynamic_exit_strategy.py"
scp genius_dynamic_exit_strategy.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/

echo "3/7: genius_exit_strategy.py"
scp genius_exit_strategy.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/

echo "4/7: requirements.txt"
scp requirements.txt ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/

echo "5/7: services/__init__.py"
scp services/__init__.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/services/

echo "6/7: services/bybit_service.py"
scp services/bybit_service.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/services/

echo "7/7: .env (APIキー含む)"
scp .env ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/

echo "🔒 .envファイルの権限を設定..."
ssh ${VPS_USER}@${VPS_IP} "chmod 600 ${REMOTE_DIR}/.env"

echo "✅ ファイル転送完了！"
echo ""
echo "次のステップ："
echo "1. VPSに接続: ssh ${VPS_USER}@${VPS_IP}"
echo "2. セットアップを続行"