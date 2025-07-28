# クイックスタートガイド

## 🚀 30秒で開始

```bash
# 1. ディレクトリに移動
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot-main/genius-trading-clean

# 2. セットアップ確認（初回のみ）
python3 test_setup.py

# 3. 実際の取引を開始
python3 genius_multi_trading_v2_with_trading.py
```

## ⚠️ 重要事項

- **実際の資金**を使用します（現在: $2,512.55）
- **自動売買**が有効です（手動確認なし）
- **最大3ポジション**まで同時保有
- **5分ごと**に10通貨を分析

## 📊 現在の設定

### 信頼度の閾値:
- BTCUSDT: 60%以上でエントリー
- ETHUSDT: 58%以上でエントリー
- SOLUSDT: 55%以上でエントリー
- その他: 50%以上でエントリー

### リスク管理（積極的設定）:
- 1ポジション: 残高の5-10%
- ストップロス: ATRの2倍（自動設定）
- 最大損失: 残高の50%（5ポジション合計）
- ⚠️ **高リスク設定に変更済み**

## 🛑 停止方法

```bash
# 即座に停止
Ctrl+C

# 強制終了（別ターミナルから）
pkill -f genius_multi_trading_v2_with_trading.py
```

## 📝 ログ例

```
🧠 Genius Analysis Started...
📊 BTC Trend: neutral (+0.66%)

SOLUSDT:
  Price: $187.67
  Direction: LONG
  Confidence: 72.0% (Need: 55%)
  ✅ OPPORTUNITY FOUND!
  
🎯 取引実行: SOLUSDT
   方向: LONG
   数量: 0.134000
   価格: $187.67
   ストップロス: $174.76
✅ SOLUSDT: 注文成功!
```

## ❓ 問題が発生したら

1. まず`Ctrl+C`で停止
2. `CLAUDE_CODE_HANDOVER.md`を確認
3. Bybitで手動でポジションを確認

---

**準備ができたら上記のコマンドを実行してください**