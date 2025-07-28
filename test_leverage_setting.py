#!/usr/bin/env python3
"""
レバレッジ設定のテスト
"""

import os
from dotenv import load_dotenv
from services.bybit_service import BybitService

def test_leverage():
    load_dotenv()
    
    bybit = BybitService(
        api_key=os.getenv('BYBIT_API_KEY'),
        api_secret=os.getenv('BYBIT_API_SECRET'),
        testnet=False
    )
    
    print("=" * 50)
    print("レバレッジ設定テスト")
    print("=" * 50)
    
    # BTCUSDTのレバレッジを5倍に設定
    symbol = 'BTCUSDT'
    print(f"\n{symbol}のレバレッジを5倍に設定中...")
    
    result = bybit.set_leverage(symbol, leverage=5)
    
    if result.get('success'):
        print(f"✅ 成功: レバレッジが5倍に設定されました")
    else:
        print(f"❌ 失敗: {result.get('error')}")
    
    # 確認
    print("\n現在のレバレッジを確認中...")
    response = bybit.client.get_positions(
        category="linear",
        symbol=symbol
    )
    
    if response["retCode"] == 0 and response["result"]["list"]:
        pos = response["result"]["list"][0]
        print(f"現在のレバレッジ: {pos.get('leverage', 'N/A')}x")
    
    print("\n" + "=" * 50)
    print("注意: 実際の取引では、注文時に自動的に5倍に設定されます")

if __name__ == "__main__":
    test_leverage()