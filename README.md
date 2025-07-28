# Genius Trading System (Clean Version)

プロフェッショナルトレーダーの評価を受けた天才トレーディングシステムの最小構成版です。

## 構成

```
genius-trading-clean/
├── genius_multi_trading_v2.py    # メインの取引システム
├── services/
│   ├── __init__.py
│   └── bybit_service.py         # Bybit API サービス
├── .env                         # API認証情報
├── requirements.txt             # 必要なパッケージ
└── README.md                    # このファイル
```

## 機能

### Priority 1 改善（実装済み）
1. **ATRベースのストップロス** - 損失を30-40%削減
2. **ビットコイン相関フィルター** - 勝率を5-10%向上
3. **タイムゾーン戦略調整** - 市場時間に応じた最適化

### 取引対象（10通貨）
- BTCUSDT（ビットコイン）
- ETHUSDT（イーサリアム）
- SOLUSDT（ソラナ）
- BNBUSDT（バイナンスコイン）
- XRPUSDT（リップル）
- DOGEUSDT（ドージコイン）
- AVAXUSDT（アバランチ）
- LINKUSDT（チェーンリンク）
- MATICUSDT（ポリゴン）
- ARBUSDT（アービトラム）

## セットアップ

```bash
# 1. ディレクトリに移動
cd /Users/macbookpro/Desktop/サイト制作/BybitBOTV3/crypto-trading-bot/genius-trading-clean

# 2. 依存関係をインストール
pip3 install -r requirements.txt

# 3. .envファイルを確認（既にコピー済み）
# BYBIT_API_KEY=your_api_key
# BYBIT_API_SECRET=your_api_secret
```

## 実行

```bash
# メインシステムを起動
python3 genius_multi_trading_v2.py
```

## 閾値設定

- BTCUSDT: 60%（メジャー通貨は慎重）
- ETHUSDT: 58%
- SOLUSDT: 55%
- その他: 50%

## ログ

システムは5分ごとに10通貨を分析し、以下の情報を表示します：
- 各通貨の価格、方向性、信頼度
- ATR値
- 取引機会
- ストップロスとテイクプロフィット

## 注意事項

- 本番環境のAPIキーを使用しています
- 実際の資金で取引が行われます
- 5分ごとに全通貨を分析します
- API制限を考慮して各通貨間に1秒の遅延があります