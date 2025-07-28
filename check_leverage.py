#!/usr/bin/env python3
"""
現在のレバレッジ設定を確認
"""

import os
from dotenv import load_dotenv
from services.bybit_service import BybitService

def check_leverage():
    load_dotenv()
    
    bybit = BybitService(
        api_key=os.getenv('BYBIT_API_KEY'),
        api_secret=os.getenv('BYBIT_API_SECRET'),
        testnet=False
    )
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    
    print("=" * 50)
    print("レバレッジ設定確認")
    print("=" * 50)
    
    for symbol in symbols:
        try:
            # ポジション情報を取得（レバレッジ含む）
            response = bybit.client.get_positions(
                category="linear",
                symbol=symbol
            )
            
            if response["retCode"] == 0:
                positions = response["result"]["list"]
                if positions:
                    for pos in positions:
                        print(f"\n{symbol}:")
                        print(f"  レバレッジ: {pos.get('leverage', 'N/A')}x")
                        print(f"  サイズ: {pos.get('size', 0)}")
                        print(f"  サイド: {pos.get('side', 'N/A')}")
                else:
                    # ポジションがない場合、デフォルトレバレッジを確認
                    print(f"\n{symbol}: ポジションなし（デフォルトレバレッジ使用）")
        except Exception as e:
            print(f"Error checking {symbol}: {e}")

if __name__ == "__main__":
    check_leverage()