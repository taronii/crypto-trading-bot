# リスク調整ガイド

## 現在の設定（2025年7月27日）

### 基本設定
- レバレッジ: 5倍
- 基本ポジションサイズ: 5%
- 最大ポジションサイズ: 10%（高信頼度時）
- 最大同時ポジション: 3
- 最大リスクエクスポージャー: 30%（3ポジション × 10%）

## リスク調整オプション

### 🔵 オプション1: レバレッジ調整（5倍→10倍）

**変更箇所**: 
```python
# services/bybit_service.py の place_order メソッド
leverage: int = 10  # 変更前: 5
```

**効果**:
- 同じ証拠金で2倍のポジションサイズ
- 利益も損失も2倍に
- 清算価格が近くなる（リスク高）

**試算**（$2,500の残高で）:
- 現在: 1ポジション最大$250（10%） × 5倍 = $1,250相当
- 変更後: 1ポジション最大$250（10%） × 10倍 = $2,500相当

### 🟢 オプション2: ポジションサイズ調整（推奨）

**変更箇所**:
```python
# genius_multi_trading_v2_with_trading.py の _calculate_position_size メソッド
def _calculate_position_size(self, confidence: float, risk_adj: float) -> float:
    """ポジションサイズ計算（積極的設定）"""
    base_size = 0.10  # 基本10%（変更前: 5%）
    
    # 信頼度による調整
    if confidence > 0.7:
        size_multiplier = 2.0   # 20%（変更前: 10%）
    elif confidence > 0.5:
        size_multiplier = 1.5   # 15%（変更前: 7.5%）
    else:
        size_multiplier = 1.0   # 10%（変更前: 5%）
        
    return base_size * size_multiplier * risk_adj
```

**効果**:
- より大きな利益機会
- レバレッジは安全な5倍を維持
- Dynamic Exit Matrixで段階的にリスク管理

**試算**（$2,500の残高で）:
- 現在: 1ポジション最大$250（10%）
- 変更後: 1ポジション最大$500（20%）
- 最大エクスポージャー: $1,500（60%）

### 🟠 オプション3: バランス型調整

**変更内容**:
- レバレッジ: 8倍（中間値）
- ポジションサイズ: 7.5-15%

**変更箇所**:
```python
# services/bybit_service.py
leverage: int = 8

# genius_multi_trading_v2_with_trading.py
base_size = 0.075  # 基本7.5%
if confidence > 0.7:
    size_multiplier = 2.0   # 15%
elif confidence > 0.5:
    size_multiplier = 1.33  # 10%
else:
    size_multiplier = 1.0   # 7.5%
```

### 🔴 オプション4: アグレッシブ設定（高リスク）

**変更内容**:
- レバレッジ: 10倍
- ポジションサイズ: 10-20%
- 最大同時ポジション: 5（変更前: 3）

**注意**: 非常に高リスク。経験豊富なトレーダー向け。

## 実装方法

### ポジションサイズ変更の場合:

1. ファイルを編集:
```bash
nano genius_multi_trading_v2_with_trading.py
```

2. `_calculate_position_size`メソッドを探す（554行目付近）

3. `base_size`の値を変更

4. 保存して再起動

### レバレッジ変更の場合:

1. ファイルを編集:
```bash
nano services/bybit_service.py
```

2. `place_order`メソッドのデフォルト値を変更（363行目付近）

3. 保存して再起動

## リスク管理の重要性

### Dynamic Exit Matrixによる保護
- 5段階利確で利益を段階的に確保
- 3段階損切りで大損失を回避
- トレーリングストップで利益を守る

### 推奨事項
1. まずは小さな変更から始める
2. 1週間程度結果を観察
3. 必要に応じて追加調整

### 緊急時の対応
- すぐにCtrl+Cで停止
- 手動ですべてのポジションを確認
- 必要に応じて手動決済

## まとめ

私のおすすめは**オプション2（ポジションサイズ調整）**です：
- レバレッジ5倍は維持（安全性）
- ポジションサイズを2倍に（10-20%）
- Dynamic Exit Matrixがリスクを管理

これにより、適度にリスクを上げながら、管理可能な範囲に収めることができます。