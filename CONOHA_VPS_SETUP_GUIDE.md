# 🇯🇵 ConoHa VPS 完全設定ガイド（トレーディングボット用）

## 📋 必要なもの
- メールアドレス
- クレジットカード（デビットカードも可）
- 電話番号（SMS認証用）

## 🎯 ステップ1: ConoHaアカウント作成（5分）

### 1-1. 公式サイトにアクセス
1. https://www.conoha.jp/ にアクセス
2. 右上の「お申し込み」をクリック

### 1-2. アカウント情報入力
```
必須項目：
- メールアドレス
- パスワード（英数字記号8文字以上）
- 氏名
- 生年月日
- 住所
- 電話番号
```

### 1-3. SMS認証
1. 携帯電話番号を入力
2. SMSで届いた認証コードを入力

### 1-4. 支払い方法登録
```
選択肢：
1. クレジットカード（推奨）
2. ConoHaチャージ（前払い）
3. ConoHaカード
```

**💡 ヒント**: 初回登録で800円分のクレジットがもらえます！

## 🖥️ ステップ2: VPSサーバー作成（10分）

### 2-1. コントロールパネルにログイン
1. https://manage.conoha.jp/ にアクセス
2. メールアドレスとパスワードでログイン

### 2-2. VPS作成
1. 左メニューから「サーバー」→「サーバー追加」をクリック
2. 以下を選択：

```
サービス: VPS
プラン: 2GB（月額1,331円）※推奨
イメージタイプ: OS
OS: Ubuntu 22.04 (64bit)
rootパスワード: 任意（必ずメモ！）Eitaro@0510
ネームタグ: crypto-bot（任意）
```

### 2-3. オプション設定
```
自動バックアップ: OFF（月額料金節約）
追加ディスク: なし
接続許可ポート: 全て許可
SSH Key: 使用しない（初心者向け）
スタートアップスクリプト: 使用しない
```

3. 「追加」ボタンをクリック

### 2-4. サーバー情報の確認
作成完了後、以下をメモ：
```
IPアドレス: xxx.xxx.xxx.xxx
ユーザー名: root
パスワード: 設定したもの
```

## 🔌 ステップ3: サーバーへの接続（5分）

### 3-1. Windowsの場合
1. スタートメニューで「cmd」と入力
2. コマンドプロンプトを開く
3. 以下を入力：
```bash
ssh root@IPアドレス
```

### 3-2. Macの場合
1. ターミナルを開く（Launchpad→その他→ターミナル）
2. 以下を入力：
```bash
ssh root@IPアドレス
```

### 3-3. 初回接続
```
The authenticity of host 'xxx.xxx.xxx.xxx' can't be established.
Are you sure you want to continue connecting (yes/no/[fingerprint])? 
→ yes と入力してEnter

root@xxx.xxx.xxx.xxx's password: 
→ 設定したパスワードを入力（表示されません）
```

## 🛠️ ステップ4: サーバー初期設定（15分）

### 4-1. システム更新
```bash
# パッケージリスト更新
apt update

# システム更新（5分程度）
apt upgrade -y
```

### 4-2. 必要なソフトウェアインストール
```bash
# Python関連パッケージ
apt install python3 python3-pip python3-venv -y

# その他必要なツール
apt install git nano htop -y

# 日本語環境（オプション）
apt install language-pack-ja -y
update-locale LANG=ja_JP.UTF-8
```

### 4-3. タイムゾーン設定
```bash
# 日本時間に設定
timedatectl set-timezone Asia/Tokyo

# 確認
date
```

### 4-4. 作業用ユーザー作成
```bash
# ユーザー追加
adduser trader

# パスワード設定（2回入力）
# その他の項目は空でEnter

# sudo権限付与
usermod -aG sudo trader

# ユーザー切り替え
su - trader
```

## 📦 ステップ5: トレーディングボット設置（20分）

### 5-1. 作業ディレクトリ作成
```bash
# ホームディレクトリに移動
cd ~

# ボット用ディレクトリ作成
mkdir -p crypto-bot/genius-trading-clean
cd crypto-bot/genius-trading-clean
```

### 5-2. ファイルのアップロード

**方法A: ConoHaコンソールを使う方法（簡単）**

1. ConoHa管理画面でサーバーを選択
2. 「コンソール」タブをクリック
3. 画面左上の「ファイル送信」アイコンをクリック
4. ローカルPCからファイルを選択してアップロード

**方法B: SCPコマンドを使う方法**

ローカルPC（別ターミナル）で実行：
```bash
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean

# 全ファイルをアップロード
scp -r * trader@ConoHaのIP:~/crypto-bot/genius-trading-clean/
```

### 5-3. Python環境構築
```bash
# VPSで実行
cd ~/crypto-bot/genius-trading-clean

# 仮想環境作成
python3 -m venv venv

# 仮想環境有効化
source venv/bin/activate

# pip更新
pip install --upgrade pip

# 必要なパッケージインストール
pip install -r requirements.txt
```

### 5-4. 環境変数設定（.env）
```bash
# .envファイル作成
nano .env
```

以下を入力：
```
BYBIT_API_KEY=あなたのAPIキー
BYBIT_API_SECRET=あなたのAPIシークレット
```

保存方法：
1. Ctrl + X を押す
2. Y を押す
3. Enter を押す

### 5-5. 動作テスト
```bash
# APIキー確認スクリプト
python test_setup.py

# 問題なければ本番実行（テスト）
python genius_multi_trading_v2_with_trading.py

# 正常動作を確認したらCtrl+Cで停止
```

## 🚀 ステップ6: 24時間自動実行設定（15分）

### 6-1. systemdサービス作成
```bash
# rootユーザーに切り替え
sudo su -

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

保存：Ctrl+X → Y → Enter

### 6-2. サービス有効化
```bash
# サービスリロード
systemctl daemon-reload

# 自動起動有効化
systemctl enable crypto-bot

# サービス開始
systemctl start crypto-bot

# 状態確認
systemctl status crypto-bot
```

✅ 「Active: active (running)」と緑色で表示されれば成功！

### 6-3. ログ確認方法
```bash
# リアルタイムログ
journalctl -u crypto-bot -f

# 過去1時間のログ
journalctl -u crypto-bot --since "1 hour ago"

# 今日のログ
journalctl -u crypto-bot --since today
```

## 📱 ステップ7: スマホ/タブレットからの監視

### 7-1. アプリインストール
- **iPhone/iPad**: 「Termius」（無料）
- **Android**: 「JuiceSSH」（無料）

### 7-2. 接続設定
```
新規接続作成：
ホスト: ConoHaのIPアドレス
ポート: 22
ユーザー名: trader
パスワード: 設定したパスワード
```

### 7-3. よく使うコマンド
```bash
# ログ確認
sudo journalctl -u crypto-bot -f

# サービス再起動
sudo systemctl restart crypto-bot

# サービス停止
sudo systemctl stop crypto-bot

# サービス開始  
sudo systemctl start crypto-bot

# 状態確認
sudo systemctl status crypto-bot
```

## 🛡️ ステップ8: セキュリティ設定（オプション）

### 8-1. ファイアウォール設定
```bash
# UFW有効化
sudo ufw allow 22/tcp
sudo ufw --force enable
```

### 8-2. 自動セキュリティアップデート
```bash
# 自動更新設定
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## ✅ 完了チェックリスト

- [ ] ConoHaアカウント作成完了
- [ ] VPSサーバー作成完了
- [ ] SSHで接続成功
- [ ] トレーディングボット設置完了
- [ ] .envファイル設定完了
- [ ] systemdサービス稼働中
- [ ] ログが正常に出力されている
- [ ] スマホからアクセス可能

## 🆘 トラブルシューティング

### 接続できない場合
```bash
# ConoHa管理画面で確認
1. サーバーが「起動中」になっているか
2. IPアドレスが正しいか
3. セキュリティグループで22番ポートが開いているか
```

### ボットが起動しない場合
```bash
# エラー詳細確認
sudo journalctl -u crypto-bot -n 100

# 手動実行でエラー確認
cd ~/crypto-bot/genius-trading-clean
source venv/bin/activate
python genius_multi_trading_v2_with_trading.py
```

### パッケージエラーの場合
```bash
# 仮想環境で再インストール
cd ~/crypto-bot/genius-trading-clean
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 💰 料金について

### 月額料金
- 2GBプラン: 1,331円/月
- 初回800円クレジット適用で実質531円

### 支払い方法
- クレジットカード（自動引き落とし）
- ConoHaチャージ（前払い、コンビニ払い可）

## 📞 サポート

### ConoHaサポート
- チャット: 平日10:00-18:00
- メール: 24時間受付
- 電話: 平日10:00-18:00
- FAQ: https://support.conoha.jp/

---

これで24時間365日、安定してトレーディングボットが稼働します！🚀

設定で分からないことがあれば、遠慮なくお聞きください。