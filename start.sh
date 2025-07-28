#!/bin/bash
# Genius Trading System 起動スクリプト

echo "=========================================="
echo "🧠 Genius Trading System"
echo "=========================================="
echo ""
echo "⚠️  注意: 本番環境での実際の取引を行います"
echo ""
echo "設定:"
echo "- 10通貨の同時監視"
echo "- 5分ごとの分析"
echo "- Priority 1改善実装済み"
echo "  - ATRベースのストップロス"
echo "  - ビットコイン相関フィルター"
echo "  - タイムゾーン戦略"
echo ""
echo "取引を開始しますか？ (y/n)"
read answer

if [ "$answer" = "y" ]; then
    echo ""
    echo "取引を開始します..."
    python3 genius_multi_trading_v2.py
else
    echo "キャンセルしました"
fi