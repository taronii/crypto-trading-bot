# 📖 暗号通貨自動売買ボット 完全取扱説明書

## 📋 目次
1. [基本情報](#基本情報)
2. [日常的な確認方法](#日常的な確認方法)
3. [よく使うコマンド一覧](#よく使うコマンド一覧)
4. [スマホからの操作](#スマホからの操作)
5. [トラブルシューティング](#トラブルシューティング)
6. [緊急停止方法](#緊急停止方法)
7. [設定変更方法](#設定変更方法)
8. [メンテナンス](#メンテナンス)
9. [よくある質問](#よくある質問)

---

## 🔧 基本情報

### サーバー情報
```
種類: Xserver VPS（2GBプラン）
IPアドレス: 162.43.24.224
OS: Ubuntu 22.04 LTS
月額料金: 1,900円
```

### ボット設置場所
```
ディレクトリ: /opt/crypto-bot/genius-trading-clean
サービス名: crypto-bot
実行ファイル: genius_multi_trading_v2_with_trading.py
```

### 取引設定
```
取引所: Bybit（現物/先物）
レバレッジ: 10倍
ポジションサイズ: 15-30%（信頼度による）
監視通貨: 10種類（BTC, ETH, SOL等）
```

---

## 📱 日常的な確認方法

### 方法1: Xserver管理画面から（推奨）

1. **ログイン**
   - URL: https://secure.xserver.ne.jp/xapanel/login/xvps/
   - メールアドレスとパスワードでログイン

2. **コンソールを開く**
   - VPSパネルで「コンソール」をクリック
   - `root`でログイン

3. **状態確認コマンド**
   ```bash
   systemctl status crypto-bot
   ```

4. **リアルタイムログ確認**
   ```bash
   journalctl -u crypto-bot -f
   ```
   （Ctrl+Cで終了）

### 方法2: ターミナル/コマンドプロンプトから

**Mac/Linux:**
```bash
ssh root@162.43.24.224
```

**Windows:**
```cmd
ssh root@162.43.24.224
```

パスワード入力後、上記の確認コマンドを実行

### 方法3: スマホアプリから

1. **Termius**（iPhone）または **JuiceSSH**（Android）をインストール
2. 接続情報を設定
3. ログイン後、確認コマンドを実行

---

## 💻 よく使うコマンド一覧

### 基本操作

| 目的 | コマンド |
|------|----------|
| 状態確認 | `systemctl status crypto-bot` |
| ログ確認（リアルタイム） | `journalctl -u crypto-bot -f` |
| ログ確認（最新50行） | `journalctl -u crypto-bot -n 50` |
| ボット停止 | `systemctl stop crypto-bot` |
| ボット開始 | `systemctl start crypto-bot` |
| ボット再起動 | `systemctl restart crypto-bot` |

### ログ検索

```bash
# 今日のログを見る
journalctl -u crypto-bot --since today

# 過去1時間のログを見る
journalctl -u crypto-bot --since "1 hour ago"

# エラーログのみ表示
journalctl -u crypto-bot -p err

# 特定の通貨ペアのログを検索
journalctl -u crypto-bot | grep "BTCUSDT"
```

### ポジション確認

```bash
# 作業ディレクトリに移動
cd /opt/crypto-bot/genius-trading-clean

# 仮想環境を有効化
source venv/bin/activate

# 現在のポジションを確認
python check_current_positions.py
```

---

## 📲 スマホからの操作

### 初期設定（初回のみ）

**iOS - Termius:**
1. App Storeから「Termius」をダウンロード
2. 「New Host」をタップ
3. 以下を入力：
   ```
   Label: Xserver VPS
   Address: 162.43.24.224
   Port: 22
   Username: root
   Password: [設定したパスワード]
   ```
4. 「Save」→「Connect」

**Android - JuiceSSH:**
1. Google Playから「JuiceSSH」をダウンロード
2. 「接続」→「新規」
3. 同様の情報を入力

### よく使う操作

**ログを見る:**
```bash
journalctl -u crypto-bot -f
```

**一時停止:**
```bash
systemctl stop crypto-bot
```

**再開:**
```bash
systemctl start crypto-bot
```

---

## 🔧 トラブルシューティング

### ボットが動いていない場合

1. **状態確認**
   ```bash
   systemctl status crypto-bot
   ```

2. **エラーログ確認**
   ```bash
   journalctl -u crypto-bot -n 100 | grep -i error
   ```

3. **手動実行でテスト**
   ```bash
   cd /opt/crypto-bot/genius-trading-clean
   source venv/bin/activate
   python test_setup.py
   ```

### よくあるエラーと対処法

**"API key invalid"**
- 原因: APIキーの期限切れまたは無効
- 対処: 
  ```bash
  nano /opt/crypto-bot/genius-trading-clean/.env
  # APIキーを更新して保存
  systemctl restart crypto-bot
  ```

**"Insufficient balance"**
- 原因: 残高不足
- 対処: Bybitに入金するか、ポジションサイズを調整

**"Connection timeout"**
- 原因: ネットワーク接続の問題
- 対処: 
  ```bash
  systemctl restart crypto-bot
  # 5分待って再確認
  ```

---

## 🚨 緊急停止方法

### 即座に全て停止
```bash
systemctl stop crypto-bot
```

### 全ポジションを手動決済
1. Bybitにログイン
2. ポジション画面で全決済
3. またはアプリから操作

### サーバー自体を停止（最終手段）
Xserver管理画面から：
1. VPSパネル
2. 「電源操作」→「シャットダウン」

---

## ⚙️ 設定変更方法

### APIキーの更新

```bash
# ファイルを編集
nano /opt/crypto-bot/genius-trading-clean/.env

# 新しいキーに書き換え
BYBIT_API_KEY=新しいAPIキー
BYBIT_API_SECRET=新しいシークレット

# 保存（Ctrl+X → Y → Enter）

# ボット再起動
systemctl restart crypto-bot
```

### レバレッジの変更

```bash
cd /opt/crypto-bot/genius-trading-clean
nano services/bybit_service.py

# leverageの値を検索して変更
# 例: leverage=10 → leverage=5

systemctl restart crypto-bot
```

### 監視通貨の変更

```bash
cd /opt/crypto-bot/genius-trading-clean
nano genius_multi_trading_v2_with_trading.py

# SYMBOLS_TO_TRADEを検索
# 不要な通貨を削除または追加

systemctl restart crypto-bot
```

---

## 🛠️ メンテナンス

### 週次メンテナンス（推奨）

1. **ログの確認**
   ```bash
   # 過去1週間のサマリー
   journalctl -u crypto-bot --since "1 week ago" | grep -E "(ERROR|WARNING|ポジション|決済)"
   ```

2. **ディスク容量確認**
   ```bash
   df -h
   ```

3. **システム更新**
   ```bash
   apt update && apt upgrade -y
   ```

### 月次メンテナンス

1. **ログファイルのクリーンアップ**
   ```bash
   journalctl --vacuum-time=30d
   ```

2. **パフォーマンス確認**
   ```bash
   htop
   ```

3. **バックアップ**
   ```bash
   cd /opt/crypto-bot
   tar -czf backup-$(date +%Y%m%d).tar.gz genius-trading-clean/.env
   ```

---

## ❓ よくある質問

### Q: 電気代はかかりますか？
A: いいえ。VPSはクラウドサービスなので、月額料金（1,900円）のみです。

### Q: 複数の取引所で使えますか？
A: 現在はBybitのみ対応です。他の取引所は要カスタマイズ。

### Q: 損失が出た場合、自動で止まりますか？
A: Dynamic Exit Matrixにより段階的に損切りされますが、完全停止はしません。

### Q: VPSが停止した場合は？
A: Xserverは99.99%の稼働率ですが、万一の場合は自動復旧します。

### Q: ログはどのくらい保存されますか？
A: 約30日間。それ以前は自動削除されます。

### Q: 税金の計算は？
A: Bybitの取引履歴をダウンロードして、税理士に相談してください。

---

## 📞 サポート連絡先

### Xserverサポート（VPS関連）
- 電話: 06-6147-2580（平日10-18時）
- メール: support@xserver.ne.jp

### Bybitサポート（取引関連）
- 24時間チャットサポート（アプリ内）
- ヘルプセンター: https://www.bybit.com/ja-JP/help-center

### ボット関連の質問
- このマニュアルを参照
- エラーログを確認して対処

---

## 🎯 運用のコツ

1. **毎日1回はログを確認**
   - 朝または夜の決まった時間に
   - 異常がないかチェック

2. **週1回はポジション整理**
   - 長期保有ポジションの見直し
   - 利益確定の判断

3. **月1回は収支確認**
   - Bybitの資産推移を確認
   - 必要に応じて出金

4. **相場急変時は手動介入**
   - 重要ニュース時は一時停止も検討
   - 大きな損失を防ぐ

---

**最終更新日**: 2025年7月28日

このマニュアルは定期的に更新してください。