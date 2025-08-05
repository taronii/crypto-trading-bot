#!/bin/bash
# X Server VPS デプロイメントスクリプト
# 使用方法: ./deploy_to_vps.sh

# 色付き出力の設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# VPS情報
VPS_IP="162.43.33.141"
VPS_USER="root"
REMOTE_DIR="/opt/crypto-bot/genius-trading-clean"

echo -e "${GREEN}🚀 X Server VPS デプロイメント開始${NC}"
echo -e "${YELLOW}VPS: ${VPS_IP}${NC}"
echo ""

# 1. ファイルの存在確認
echo -e "${GREEN}1. ファイルの確認...${NC}"
required_files=(
    "genius_multi_trading_v2_with_trading.py"
    "genius_dynamic_exit_strategy.py"
    "genius_exit_strategy.py"
    "requirements.txt"
    ".env"
    "services/__init__.py"
    "services/bybit_service.py"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ✅ $file"
    else
        echo -e "  ${RED}❌ $file が見つかりません${NC}"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo -e "${RED}必要なファイルが不足しています。終了します。${NC}"
    exit 1
fi

# 2. VPSへの接続テスト
echo -e "\n${GREEN}2. VPSへの接続テスト...${NC}"
ssh -o ConnectTimeout=5 -o BatchMode=yes ${VPS_USER}@${VPS_IP} exit 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "  ✅ SSH接続OK"
else
    echo -e "  ${RED}❌ SSH接続に失敗しました${NC}"
    echo -e "  ${YELLOW}手動でSSH接続を確認してください: ssh ${VPS_USER}@${VPS_IP}${NC}"
    exit 1
fi

# 3. VPS上のディレクトリ作成
echo -e "\n${GREEN}3. VPS上のディレクトリ準備...${NC}"
ssh ${VPS_USER}@${VPS_IP} "mkdir -p ${REMOTE_DIR}/services"
echo -e "  ✅ ディレクトリ作成完了"

# 4. ファイルのアップロード
echo -e "\n${GREEN}4. ファイルのアップロード...${NC}"

# メインファイル
echo -e "  📤 メインファイルをアップロード中..."
scp -q genius_multi_trading_v2_with_trading.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/
scp -q genius_dynamic_exit_strategy.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/
scp -q genius_exit_strategy.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/
scp -q requirements.txt ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/
echo -e "  ✅ メインファイル完了"

# servicesディレクトリ
echo -e "  📤 servicesディレクトリをアップロード中..."
scp -q services/__init__.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/services/
scp -q services/bybit_service.py ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/services/
echo -e "  ✅ servicesディレクトリ完了"

# .envファイル（セキュリティ警告付き）
echo -e "\n${YELLOW}⚠️  APIキーを含む.envファイルをアップロードします${NC}"
echo -e "${YELLOW}続行しますか？ (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    scp -q .env ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/
    ssh ${VPS_USER}@${VPS_IP} "chmod 600 ${REMOTE_DIR}/.env"
    echo -e "  ✅ .envファイルアップロード完了（権限: 600）"
else
    echo -e "  ${YELLOW}⚠️  .envファイルのアップロードをスキップしました${NC}"
    echo -e "  ${YELLOW}後で手動でアップロードしてください${NC}"
fi

# 5. VPS上でのセットアップ実行
echo -e "\n${GREEN}5. VPS上でのセットアップ...${NC}"

# セットアップスクリプトを作成して実行
cat << 'EOF' > /tmp/vps_setup.sh
#!/bin/bash
cd /opt/crypto-bot/genius-trading-clean

# Python仮想環境の作成
echo "  🔧 Python仮想環境を作成中..."
python3 -m venv venv

# 依存関係のインストール
echo "  📦 依存関係をインストール中..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 実行権限の設定
chmod +x genius_multi_trading_v2_with_trading.py

echo "  ✅ VPS上のセットアップ完了"
EOF

# スクリプトをVPSに転送して実行
scp -q /tmp/vps_setup.sh ${VPS_USER}@${VPS_IP}:/tmp/
ssh ${VPS_USER}@${VPS_IP} "bash /tmp/vps_setup.sh && rm /tmp/vps_setup.sh"
rm /tmp/vps_setup.sh

# 6. systemdサービスの設定
echo -e "\n${GREEN}6. systemdサービスの設定...${NC}"

# サービスファイルの作成
cat << 'EOF' > /tmp/crypto-bot.service
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
EOF

# サービスファイルをVPSに転送
scp -q /tmp/crypto-bot.service ${VPS_USER}@${VPS_IP}:/etc/systemd/system/
rm /tmp/crypto-bot.service

# サービスの有効化
ssh ${VPS_USER}@${VPS_IP} << 'ENDSSH'
systemctl daemon-reload
systemctl enable crypto-bot
echo "  ✅ systemdサービス設定完了"
ENDSSH

# 7. 最終確認
echo -e "\n${GREEN}7. デプロイメント完了！${NC}"
echo -e "\n${YELLOW}次のステップ:${NC}"
echo -e "1. VPSにSSH接続: ${GREEN}ssh ${VPS_USER}@${VPS_IP}${NC}"
echo -e "2. サービスを開始: ${GREEN}systemctl start crypto-bot${NC}"
echo -e "3. ログを確認: ${GREEN}journalctl -u crypto-bot -f${NC}"
echo -e "\n${YELLOW}便利なコマンド:${NC}"
echo -e "  状態確認: ${GREEN}systemctl status crypto-bot${NC}"
echo -e "  停止: ${GREEN}systemctl stop crypto-bot${NC}"
echo -e "  再起動: ${GREEN}systemctl restart crypto-bot${NC}"
echo -e "  ログ確認: ${GREEN}journalctl -u crypto-bot -n 50${NC}"

echo -e "\n${GREEN}✨ デプロイメント成功！${NC}"