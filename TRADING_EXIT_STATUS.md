# 📊 決済設定の現状と改善案

## 現在の決済設定

### ✅ 実装済み
1. **ストップロス（損切り）**
   - ATRの2倍で自動設定
   - 注文時に設定される
   - 例: 価格$100、ATR$2の場合 → ストップ$96

### ❌ 未実装
1. **テイクプロフィット（利確）**
   - 計算はされているが使われていない
   - 3段階: 1.5%、3%、5%

2. **トレーリングストップ**
   - 利益を守る機能なし

3. **部分決済**
   - 段階的な利確なし

## 現在のリスク

**利確が設定されていないため**:
- 利益を逃す可能性
- 相場反転で含み益が損失に
- 手動監視が必要

## 改善オプション

### オプション1: シンプルな利確追加（推奨）
```python
# 最初の利確ポイント（1.5%）だけ設定
take_profit = opportunity['take_profits'][0]
```

### オプション2: 手動で部分決済
- 50%を1.5%で利確
- 残り50%をトレンドに乗せる

### オプション3: 現状維持
- ストップロスのみ
- 手動で利確判断

## どうしますか？

1. **利確を追加する**（オプション1）
2. **現状のまま手動管理**
3. **その他のカスタマイズ**