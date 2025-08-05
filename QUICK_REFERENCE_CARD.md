# 🚀 トレーディングボット クイックリファレンス

## 🔑 接続情報
```
サーバーIP: 162.43.24.224
ユーザー: root
パスワード: [設定したパスワード]
```

## 📱 毎日の確認（1分で完了）

### スマホから確認
1. Termius/JuiceSSHアプリを開く
2. 「Xserver VPS」をタップ
3. 以下を実行：
```bash
journalctl -u crypto-bot -n 20
```

### 正常な表示例
```
[INFO] シグナル分析完了
[INFO] BTCUSDT: シグナルなし
[INFO] ポジション: 3/3 (最大数到達)
```

## 🆘 緊急コマンド

### ボットを止める
```bash
systemctl stop crypto-bot
```

### ボットを再開
```bash
systemctl start crypto-bot
```

### エラーを見る
```bash
journalctl -u crypto-bot -p err -n 50
```

## 📊 便利なコマンド

| やりたいこと | コマンド |
|-------------|----------|
| 今の状態を見る | `systemctl status crypto-bot` |
| リアルタイムログ | `journalctl -u crypto-bot -f` |
| 今日の取引 | `journalctl -u crypto-bot --since today | grep "ポジション"` |
| 再起動 | `systemctl restart crypto-bot` |

## ⚠️ こんな時は

### 「Active: failed」と表示
```bash
systemctl restart crypto-bot
```

### APIエラーが出る
1. Bybitでメンテナンス中か確認
2. 5分待って再起動

### ポジションが増えない
- 正常です（相場にシグナルがない）
- 最大3ポジションまで

## 📞 困ったら

1. エラーログをコピー
2. 以下を確認：
   - Xserver管理画面でVPS稼働中か
   - Bybitでメンテナンスしていないか

---
**保存推奨** このカードをスマホに保存しておくと便利です！