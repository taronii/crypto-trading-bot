# 🚀 Xserver VPS 超簡単設定ガイド

## ✨ Xserverが簡単な理由
- アプリイメージで**Python環境が自動設定済み**
- SSHが**最初から使える**（設定不要）
- 管理画面が**完全日本語**
- **電話サポート**あり（平日10-18時）

## 📝 ステップ1: アカウント作成（5分）

### 1-1. 公式サイトにアクセス
https://vps.xserver.ne.jp/

### 1-2. 「お申し込み」をクリック
1. 「10日間無料お試し 新規お申込み」を選択
2. メールアドレスを入力
3. 確認コードを入力

### 1-3. 申込みフォーム入力
```
サーバーID: 好きな名前（例：cryptobot）
プラン: 2GBプラン（月額1,900円）
契約期間: 1ヶ月
OS: Ubuntu 22.04
rootパスワード: 任意（例：MyBot2025!）
```

**⚠️ 重要**: rootパスワードは必ずメモ！

### 1-4. お客様情報入力
- 名前、住所、電話番号など
- 支払い方法（クレジットカード推奨）

## 🖥️ ステップ2: VPS初期設定（3分）

### 2-1. 管理画面にログイン
1. https://secure.xserver.ne.jp/xapanel/login/xvps/
2. メールアドレスとパスワードでログイン

### 2-2. VPS管理画面
1. 「VPS管理」をクリック
2. IPアドレスをメモ（例：123.456.789.0）

### 2-3. SSH接続情報の確認
```
IPアドレス: 表示されているIP
ポート: 22（デフォルト）
ユーザー: root
パスワード: 設定したもの
```

## 💻 ステップ3: MacからSSH接続（1分）

### 3-1. ターミナルを開く
- Cmd + Space → 「ターミナル」

### 3-2. 接続コマンド
```bash
ssh root@あなたのIPアドレス
```

例：
```bash
ssh root@123.456.789.0
```

### 3-3. 初回接続
```
Are you sure you want to continue connecting? → yes
Password: → 設定したパスワード
```

✅ 接続成功！

## 📦 ステップ4: ボット環境構築（10分）

### 4-1. システム更新（Xserverは最新なので速い）
```bash
apt update && apt upgrade -y
```

### 4-2. 必要パッケージインストール（一部は設定済み）
```bash
apt install python3-pip python3-venv git nano -y
```

### 4-3. 作業ディレクトリ作成
```bash
mkdir -p /opt/crypto-bot
cd /opt/crypto-bot
```

### 4-4. ボットファイルをアップロード

**新しいターミナルウィンドウ**を開いて（Cmd+N）：
```bash
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/

scp -r genius-trading-clean root@あなたのIP:/opt/crypto-bot/
```

## 🔧 ステップ5: ボット設定（5分）

### 5-1. VPSに戻って設定
```bash
cd /opt/crypto-bot/genius-trading-clean
```

### 5-2. Python仮想環境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 5-3. パッケージインストール
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5-4. APIキー設定
```bash
nano .env
```

以下を入力：
```
BYBIT_API_KEY=あなたのAPIキー
BYBIT_API_SECRET=あなたのAPIシークレット
```

保存：Ctrl+X → Y → Enter

### 5-5. テスト実行
```bash
python test_setup.py
```

## 🤖 ステップ6: 24時間自動実行（5分）

### 6-1. systemdサービス作成
```bash
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
ExecStart=/opt/crypto-bot/genius-trading-clean/venv/bin/python genius_multi_trading_v2_with_trading.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

保存：Ctrl+X → Y → Enter

### 6-2. サービス起動
```bash
systemctl enable crypto-bot
systemctl start crypto-bot
systemctl status crypto-bot
```

✅ **active (running)**と表示されれば完了！

## 📱 ステップ7: スマホから監視

### Termius（iPhone）やJuiceSSH（Android）で接続
```
Host: あなたのIP
Port: 22
User: root
Password: 設定したパスワード
```

### ログ確認コマンド
```bash
journalctl -u crypto-bot -f
```

## 🎯 Xserver VPSの便利機能

### 1. **コンソール機能**
管理画面から直接操作可能（SSHできない時の保険）

### 2. **スナップショット**
ワンクリックでバックアップ作成

### 3. **監視機能**
CPU/メモリ使用率をグラフで確認

## ✅ 完了チェックリスト

- [ ] Xserver VPS契約完了
- [ ] SSH接続成功  
- [ ] ボットファイルアップロード完了
- [ ] .env設定完了
- [ ] systemdサービス稼働中
- [ ] ログ出力確認

## 🆘 困った時は

### Xserverサポート
- **電話**: 06-6147-2580（平日10-18時）
- **メール**: support@xserver.ne.jp
- **チャット**: 管理画面内

### よくあるトラブル
1. **SSH接続できない**
   → 管理画面の「コンソール」から操作

2. **pip installでエラー**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --no-cache-dir
   ```

3. **サービスが起動しない**
   ```bash
   journalctl -u crypto-bot -n 50
   ```

---

🎉 これで完了です！Xserverなら初心者でも簡単に24時間稼働できます！