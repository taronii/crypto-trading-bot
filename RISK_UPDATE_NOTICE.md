# ⚡ リスク設定更新完了！

## 更新内容（2025年7月27日）

### ポジションサイズを2倍に増加しました！

**変更前**:
- 基本: 5%
- 高信頼度: 10%
- 中信頼度: 7.5%
- 低信頼度: 5%

**変更後**:
- 基本: 10% ⚡
- 高信頼度: 20% ⚡
- 中信頼度: 15% ⚡
- 低信頼度: 10% ⚡

### レバレッジは安全な5倍を維持

## 新しいリスクプロファイル

**$2,500の残高で**:
- 1ポジション最大: $500（20%）
- 3ポジション合計最大: $1,500（60%）
- 実効エクスポージャー: 最大$7,500（レバレッジ込み）

## Dynamic Exit Matrixによる保護

リスクが増えても、以下の機能で保護されています：

1. **5段階利確**
   - 0.5%で20%決済（$100の利益で$20確保）
   - 段階的に利益を確保

2. **3段階損切り**
   - -0.5%で25%損切り（早期ダメージ軽減）
   - 最大損失を限定

3. **トレーリングストップ**
   - 利益が出たら自動的に保護

## 起動方法

```bash
# そのまま起動するだけでOK！
python3 genius_multi_trading_v2_with_trading.py
```

## 注意事項

⚠️ **リスクが2倍になりました**
- より大きな利益機会
- より大きな損失リスク
- 初回は必ず監視してください

## 結果の見方

**良好な場合**:
- 1日で残高が5-10%増加
- 勝率が維持される

**要注意な場合**:
- 1日で残高が10%以上減少
- 連続して損切りが発生

## さらなる調整

もし結果を見て調整したい場合：
- **もっとリスクを上げる**: レバレッジを8倍に
- **リスクを下げる**: ポジションサイズを7.5-15%に

`RISK_ADJUSTMENT_OPTIONS.md`に詳細な調整方法があります。

---

**準備ができたら起動してください！より大きな利益を狙いましょう 🚀**