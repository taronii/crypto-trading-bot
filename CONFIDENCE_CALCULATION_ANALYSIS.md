# 信頼度計算ロジック分析レポート

## 現在の計算ロジック

### 1. スコア要素（加算方式）

#### マルチタイムフレーム分析（MTF）
```python
weight = {'5': 0.1, '15': 0.2, '60': 0.3, '240': 0.4}
```
- 各時間枠のトレンド強度（0.3-0.8）× 重み
- 理論最大: 100%（全時間枠で強いトレンド一致）
- 実際の最大: 約80%（strength最大0.8のため）

#### 追加スコア要素
- **ボリューム**: +10%（平均の1.5倍以上）
- **サポート/レジスタンス**: +15%（価格から2%以内）
- **RSI**: +10%（売られすぎ/買われすぎ）

**理論最大スコア**: 135%

### 2. 調整要素（乗算方式）

#### リスク調整
- `_calculate_risk_adjustment()`の詳細不明
- おそらく0.8-1.0の範囲

#### BTC相関フィルター
- BTCが-2%以下でアルトコインLONG: ×0.7

#### タイムゾーン調整
- アジア時間: ×1.2
- ロンドン時間: ×1.1
- NY時間: ×1.15
- ロンドン・NY重複: ×1.25
- その他: ×0.9

#### 最終キャップ
- 85%で上限設定

## 問題点

### 1. スコアの不均衡
- MTFが支配的（最大80%）
- 他の要素は補助的（各10-15%）
- 短期的な指標（RSI、ボリューム）の影響が小さい

### 2. 信頼度が出にくい構造
- 通常のトレンドでは50%程度が限界
- 閾値50%を超えるのが困難
- 特に横ばい相場では機会を逃す

### 3. 調整の重複問題
- 複数の乗算調整で信頼度が大幅に減少
- 例: 0.7 × 0.9 = 0.63（37%減）

## 実際の計算例

### ケース1: 強いトレンド
```
MTFスコア: 65%（強い上昇トレンド）
ボリューム: +10%
サポート: +15%
基本スコア: 90%
BTC調整: ×1.0（BTCも上昇）
時間調整: ×1.2（アジア時間）
最終: 90% × 1.2 = 108% → 85%（キャップ）
```

### ケース2: 通常のトレンド
```
MTFスコア: 35%（緩やかな上昇）
ボリューム: +0%
RSI: +10%（売られすぎ）
基本スコア: 45%
調整: ×1.0
最終: 45%（閾値50%未満）
```

## 改善案

### 1. スコアリングの再バランス
```python
# 現在
mtf_weight = 1.0  # 100%まで
other_weight = 0.1-0.15  # 各10-15%

# 改善案
mtf_weight = 0.6  # 60%まで
volume_weight = 0.15  # 15%
sr_weight = 0.15  # 15%
rsi_weight = 0.10  # 10%
```

### 2. 基本信頼度の引き上げ
```python
# ベーススコアを追加
base_confidence = 0.2  # 20%スタート
total_confidence = base_confidence + calculated_scores
```

### 3. 調整方式の改善
```python
# 現在: 乗算
confidence *= adjustment1 * adjustment2

# 改善案: 加重平均
adjustments = [btc_adj, timezone_adj, risk_adj]
avg_adjustment = sum(adjustments) / len(adjustments)
confidence *= avg_adjustment
```

### 4. 動的閾値
```python
# 市場状況に応じて閾値を調整
if market_volatility == 'high':
    threshold = 0.45  # 50% → 45%
elif market_volatility == 'low':
    threshold = 0.55  # 50% → 55%
```

## 推奨される即時対応

### オプション1: 閾値の引き下げ
```python
thresholds = {
    'BTCUSDT': 0.50,   # 60% → 50%
    'ETHUSDT': 0.48,   # 58% → 48%
    'SOLUSDT': 0.45,   # 55% → 45%
    'default': 0.40    # 50% → 40%
}
```

### オプション2: スコア計算の調整
```python
def analyze_genius(self, symbol: str) -> Optional[Dict]:
    # ... 既存のコード ...
    
    # 基本信頼度を追加
    base_confidence = 0.15  # 15%のベース
    
    # 最終判定
    confidence = base_confidence + max(long_score, short_score)
```

### オプション3: トレンド強度の調整
```python
def _analyze_timeframe(self, klines: List, timeframe: str) -> Dict:
    # EMAクロスオーバー
    if ema_short[-1] > ema_long[-1] and ema_short[-5] <= ema_long[-5]:
        strength = 1.0  # 0.8 → 1.0
    # 通常のトレンド
    elif ema_short[-1] > ema_long[-1]:
        strength = 0.7  # 0.5 → 0.7
```

## 結論

現在の信頼度計算は保守的すぎて、多くの取引機会を逃している可能性があります。特に：

1. **閾値が高すぎる**（50-60%）
2. **MTF分析が支配的すぎる**
3. **調整要素が信頼度を下げすぎる**

即座に効果が期待できるのは**閾値の引き下げ**です。これにより、より多くの取引機会を捉えることができます。