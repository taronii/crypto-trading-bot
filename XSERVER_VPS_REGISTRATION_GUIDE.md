# 📘 X Server VPS 登録・設定完全ガイド

## 📋 目次
1. [Xserver VPSの登録](#1-xserver-vpsの登録)
2. [VPSプランの選択](#2-vpsプランの選択)
3. [初期設定](#3-初期設定)
4. [SSH接続の準備](#4-ssh接続の準備)
5. [トレーディングボットのデプロイ](#5-トレーディングボットのデプロイ)

---

## 1. Xserver VPSの登録

### 1.1 公式サイトにアクセス
1. **URL**: https://vps.xserver.ne.jp/
2. 「お申し込み」ボタンをクリック

### 1.2 新規お申し込み
1. **「新規お申し込み」**を選択
2. メールアドレスを入力
3. 確認コードを受信・入力

### 1.3 会員情報の入力
必要な情報：
- **お名前**（漢字・カナ）
- **郵便番号・住所**
- **電話番号**
- **メールアドレス**（既に入力済み）
- **パスワード**（8文字以上、英数字混合推奨）

### 1.4 SMS・電話認証
1. 電話番号を入力
2. SMS認証または自動音声認証を選択
3. 認証コードを入力

---

## 2. VPSプランの選択

### 2.1 推奨プラン
トレーディングボット用の推奨スペック：

| プラン | メモリ | CPU | SSD | 月額料金 | 推奨度 |
|-------|-------|-----|-----|---------|--------|
| 2GB | 2GB | 3コア | 50GB | 1,900円 | ⭐⭐⭐⭐⭐ |
| 4GB | 4GB | 4コア | 100GB | 3,800円 | ⭐⭐⭐⭐ |
| 8GB | 8GB | 6コア | 100GB | 7,800円 | ⭐⭐⭐ |

**💡 2GBプランで十分です**（マニュアルでも使用中）

### 2.2 OS選択
- **Ubuntu 22.04 LTS**を選択（推奨）
- その他のOSも可能ですが、このガイドはUbuntuベース

### 2.3 rootパスワード設定
- **強力なパスワードを設定**
- 例: `Tr@d1ng#B0t2024!`（実際は独自のものを）
- **必ずメモして安全に保管**

### 2.4 支払い方法
1. **クレジットカード**（推奨）
2. 銀行振込
3. コンビニ払い

---

## 3. 初期設定

### 3.1 VPSパネルへログイン
1. **URL**: https://secure.xserver.ne.jp/xapanel/login/xvps/
2. 登録時のメールアドレスとパスワードでログイン

### 3.2 VPS情報の確認
VPSパネルで確認できる重要情報：
- **IPアドレス**（例: 162.43.24.224）
- **OS**: Ubuntu 22.04
- **状態**: 稼働中

### 3.3 コンソール接続（初回）
1. VPSパネルで「**コンソール**」をクリック
2. 新しいウィンドウでコンソールが開く
3. ログイン:
   ```
   login: root
   Password: [設定したrootパスワード]
   ```

---

## 4. SSH接続の準備

### 4.1 Mac/Linuxの場合
ターミナルを開いて：
```bash
# 接続テスト
ssh root@[あなたのVPSのIPアドレス]

# 初回接続時の警告
The authenticity of host 'xxx.xxx.xxx.xxx' can't be established.
Are you sure you want to continue connecting (yes/no)? yes

# パスワード入力
root@xxx.xxx.xxx.xxx's password: [rootパスワード]
```

### 4.2 Windowsの場合

#### 方法1: Windows Terminal（Windows 10/11）
```cmd
ssh root@[あなたのVPSのIPアドレス]
```

#### 方法2: PuTTYを使用
1. PuTTYをダウンロード: https://www.putty.org/
2. Host Name: `[VPSのIPアドレス]`
3. Port: `22`
4. Connection type: `SSH`
5. 「Open」をクリック

### 4.3 SSH鍵認証の設定（推奨）

#### ローカルマシンで鍵生成
```bash
# 鍵ペアの生成
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 公開鍵をVPSにコピー
ssh-copy-id root@[VPSのIPアドレス]
```

---

## 5. トレーディングボットのデプロイ

### 5.1 VPS初期セットアップ

SSH接続後、以下を実行：

```bash
# 1. システムアップデート
apt update && apt upgrade -y

# 2. 必要なパッケージをインストール
apt install -y python3 python3-pip python3-venv git curl wget

# 3. タイムゾーンを日本時間に設定
timedatectl set-timezone Asia/Tokyo

# 4. 作業ディレクトリ作成
mkdir -p /opt/crypto-bot/genius-trading-clean
cd /opt/crypto-bot/genius-trading-clean
```

### 5.2 ボットのファイル転送

**ローカルマシン（Mac）で実行：**

```bash
# プロジェクトディレクトリに移動
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean

# 自動デプロイスクリプトを実行
./deploy_to_vps.sh
```

VPSのIPアドレスを聞かれたら入力してください。

### 5.3 手動でファイル転送する場合

```bash
# ローカルマシンで実行
scp genius_multi_trading_v2_with_trading.py root@[VPS_IP]:/opt/crypto-bot/genius-trading-clean/
scp genius_dynamic_exit_strategy.py root@[VPS_IP]:/opt/crypto-bot/genius-trading-clean/
scp genius_exit_strategy.py root@[VPS_IP]:/opt/crypto-bot/genius-trading-clean/
scp requirements.txt root@[VPS_IP]:/opt/crypto-bot/genius-trading-clean/

# servicesディレクトリ
ssh root@[VPS_IP] "mkdir -p /opt/crypto-bot/genius-trading-clean/services"
scp services/*.py root@[VPS_IP]:/opt/crypto-bot/genius-trading-clean/services/

# .envファイル（APIキー含む）
scp .env root@[VPS_IP]:/opt/crypto-bot/genius-trading-clean/
```

### 5.4 VPS上でのセットアップ

VPSにSSH接続して：

```bash
cd /opt/crypto-bot/genius-trading-clean

# Python仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# 権限設定
chmod 600 .env
chmod +x genius_multi_trading_v2_with_trading.py
```

### 5.5 systemdサービス設定

```bash
# サービスファイル作成
nano /etc/systemd/system/crypto-bot.service
```

以下を貼り付け：
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

保存して終了（Ctrl+X → Y → Enter）

```bash
# サービス有効化と起動
systemctl daemon-reload
systemctl enable crypto-bot
systemctl start crypto-bot

# 状態確認
systemctl status crypto-bot
```

---

## 🎉 完了！

### 動作確認コマンド
```bash
# リアルタイムログ
journalctl -u crypto-bot -f

# サービス状態
systemctl status crypto-bot

# 最新50行のログ
journalctl -u crypto-bot -n 50
```

### 日常管理
```bash
# 停止
systemctl stop crypto-bot

# 再起動
systemctl restart crypto-bot

# ログ確認
journalctl -u crypto-bot --since today
```

---

## 💰 料金まとめ

### 2GBプラン（推奨）
- **月額**: 1,900円（税込）
- **初期費用**: 無料
- **最低利用期間**: なし（1ヶ月単位）

### 支払いサイクル
- 1ヶ月
- 12ヶ月（10%割引）
- 24ヶ月（20%割引）
- 36ヶ月（30%割引）

---

## 🆘 サポート

### Xserverサポート
- **電話**: 06-6147-2580（平日10-18時）
- **メール**: support@xserver.ne.jp
- **チャット**: 管理パネル内

### よくある質問

**Q: IPアドレスは固定ですか？**
A: はい、固定IPアドレスが割り当てられます。

**Q: バックアップは？**
A: 手動でバックアップが必要です。自動バックアップはオプション。

**Q: スペック変更は可能？**
A: はい、プラン変更で対応可能（上位プランへの変更は即時、下位への変更は翌月から）。

---

準備ができたら、まずXserver VPSの公式サイトから登録を開始してください！