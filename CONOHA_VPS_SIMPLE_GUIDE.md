# 🎯 ConoHa VPS 超簡単設定ガイド

## 📱 まず最初に：ConoHa管理画面からやりましょう！

### ステップ1: ConoHa管理画面にログイン
1. https://manage.conoha.jp/ を開く
2. メールアドレスとパスワードでログイン

### ステップ2: コンソールを開く
1. サーバー一覧から「crypto-bot」をクリック
2. 上部の「**コンソール**」タブをクリック
3. 黒い画面（ターミナル）が表示される

### ステップ3: ログイン
黒い画面に以下が表示されたら：
```
Ubuntu 22.04 LTS サーバー名 tty1
サーバー名 login: 
```

1. `root` と入力してEnter
2. `Password:` と表示されたら `Eitaro@0510` を入力してEnter
   （パスワードは見えません）

---

## 🚀 ここから本番！コピペで進めましょう

### 📦 準備作業（1つずつコピペ）

#### 1. システムを最新にする
```bash
apt update
```
↑これをコピーして、黒い画面に貼り付けてEnter（2分待つ）

```bash
apt upgrade -y
```
↑これもコピペしてEnter（5分待つ）

#### 2. 必要なソフトをインストール
```bash
apt install python3 python3-pip python3-venv git nano -y
```
↑コピペしてEnter（2分待つ）

#### 3. 日本時間に設定
```bash
timedatectl set-timezone Asia/Tokyo
```
↑コピペしてEnter

#### 4. 作業用ユーザーを作る
```bash
adduser trader
```
↑コピペしてEnter

パスワードを聞かれるので：
- 好きなパスワードを2回入力（例：Trader123!）
- その他の質問は全部Enterで飛ばす

```bash
usermod -aG sudo trader
```
↑コピペしてEnter

```bash
su - trader
```
↑コピペしてEnter（ユーザーが切り替わる）

---

## 💾 ボットファイルをアップロード

### 方法A: ConoHa画面から（簡単！）

1. ConoHaコンソール画面の左上にある「📁」アイコンをクリック
2. アップロードしたいファイルを選択
3. アップロード先：`/home/trader/` を指定

### 方法B: 別ウィンドウから送る

**新しいターミナルウィンドウを開いて**（Macの場合）：

1. Cmd+N で新しいターミナルを開く
2. 以下を実行：

```bash
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/
```

```bash
scp -r genius-trading-clean trader@163.44.97.167:~/
```
パスワードを聞かれたら、さっき作った `Trader123!` を入力

---

## 🔧 ボットの設定

**元のConoHaコンソールに戻って**：

#### 1. フォルダに移動
```bash
cd ~/genius-trading-clean
```
↑コピペしてEnter

#### 2. Python環境を作る
```bash
python3 -m venv venv
```
↑コピペしてEnter（1分待つ）

```bash
source venv/bin/activate
```
↑コピペしてEnter（プロンプトに(venv)が付く）

#### 3. 必要なパッケージをインストール
```bash
pip install --upgrade pip
```
↑コピペしてEnter

```bash
pip install -r requirements.txt
```
↑コピペしてEnter（3-5分待つ）

#### 4. APIキーを設定
```bash
nano .env
```
↑コピペしてEnter

以下を入力（あなたのAPIキーに変更）：
```
BYBIT_API_KEY=ここにAPIキー
BYBIT_API_SECRET=ここにAPIシークレット
```

保存方法：
1. Ctrl+X を押す
2. Y を押す  
3. Enter を押す

#### 5. テスト実行
```bash
python test_setup.py
```
↑コピペしてEnter（接続成功と表示されればOK）

---

## 🤖 24時間自動実行の設定

#### 1. rootに戻る
```bash
exit
```
↑コピペしてEnter（rootに戻る）

#### 2. 自動起動ファイルを作る
```bash
nano /etc/systemd/system/crypto-bot.service
```
↑コピペしてEnter

以下を全部コピーして貼り付け：
```ini
[Unit]
Description=Crypto Trading Bot
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/home/trader/genius-trading-clean
Environment="PATH=/home/trader/genius-trading-clean/venv/bin"
ExecStart=/home/trader/genius-trading-clean/venv/bin/python genius_multi_trading_v2_with_trading.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

保存：Ctrl+X → Y → Enter

#### 3. 自動起動を有効にする
```bash
systemctl enable crypto-bot
```
↑コピペしてEnter

```bash
systemctl start crypto-bot
```
↑コピペしてEnter

#### 4. 動作確認
```bash
systemctl status crypto-bot
```
↑コピペしてEnter

**緑色で「active (running)」**と表示されれば成功！🎉

---

## 📱 スマホから確認する方法

### iPhoneの場合
1. App Storeで「Termius」をインストール
2. 新規接続を作成：
   - Host: 163.44.97.167
   - Username: trader
   - Password: Trader123!

### 接続後のコマンド
ログを見る：
```bash
sudo journalctl -u crypto-bot -f
```

---

## ❓ よくある質問

### Q: エラーが出た
A: 以下のコマンドでログを確認
```bash
sudo journalctl -u crypto-bot -n 50
```

### Q: 止めたい時
A: 以下のコマンド
```bash
sudo systemctl stop crypto-bot
```

### Q: 再開したい時
A: 以下のコマンド
```bash
sudo systemctl start crypto-bot
```

### Q: 設定を変更した後
A: 以下のコマンド
```bash
sudo systemctl restart crypto-bot
```

---

## 🆘 困ったら

1. エラーメッセージをコピー
2. 質問する時に貼り付け
3. どのステップで止まったか教えてください

これで完了です！24時間自動でトレードが動きます🚀