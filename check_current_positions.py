#!/usr/bin/env python3
"""
現在のポジションを確認して取引が正常か検証
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from services.bybit_service import BybitService
import json

def check_positions():
    """現在のポジションを詳細に確認"""
    load_dotenv()
    
    # Bybit接続
    bybit = BybitService(
        api_key=os.getenv('BYBIT_API_KEY'),
        api_secret=os.getenv('BYBIT_API_SECRET'),
        testnet=False
    )
    
    print("="*60)
    print("🔍 ポジション確認スクリプト")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. アカウント情報
    print("\n📊 アカウント情報:")
    balance = bybit.get_balance()
    if balance and 'USDT' in balance:
        usdt_info = balance['USDT']
        print(f"  💰 USDT残高: ${usdt_info.get('available_balance', 0):,.2f}")
        print(f"  💼 合計資産: ${usdt_info.get('equity', 0):,.2f}")
        print(f"  🔒 使用証拠金: ${usdt_info.get('used_margin', 0):,.2f}")
        
        # 証拠金使用率
        if usdt_info.get('equity', 0) > 0:
            margin_ratio = usdt_info.get('used_margin', 0) / usdt_info.get('equity', 0) * 100
            print(f"  📈 証拠金使用率: {margin_ratio:.1f}%")
    
    # 2. ポジション確認
    print("\n📋 現在のポジション:")
    positions = bybit.get_positions()
    
    if not positions:
        print("  ❌ ポジションなし")
        return
    
    total_positions = len(positions)
    total_pnl = 0
    
    for i, pos in enumerate(positions, 1):
        print(f"\n  ポジション {i}/{total_positions}:")
        print(f"  🪙 通貨: {pos['symbol']}")
        print(f"  📊 方向: {'ロング' if pos['side'] == 'Buy' else 'ショート'}")
        print(f"  💵 エントリー価格: ${pos['entry_price']:,.2f}")
        print(f"  📊 現在価格: ${pos['current_price']:,.2f}")
        print(f"  📏 数量: {pos['size']}")
        print(f"  💰 ポジション価値: ${pos['size'] * pos['current_price']:,.2f}")
        
        # レバレッジ確認
        print(f"  🔥 レバレッジ: {pos.get('leverage', 'N/A')}x")
        
        # PnL
        pnl_percentage = (pos['current_price'] / pos['entry_price'] - 1) * 100
        if pos['side'] == 'Sell':
            pnl_percentage *= -1
        
        print(f"  💹 未実現損益: ${pos['unrealized_pnl']:,.2f} ({pnl_percentage:+.2f}%)")
        total_pnl += pos['unrealized_pnl']
        
        # ポジションサイズの検証（残高に対する割合）
        if balance and 'USDT' in balance:
            position_value = pos['size'] * pos['entry_price']
            position_ratio = position_value / usdt_info.get('equity', 1) * 100
            print(f"  📊 ポジションサイズ: 残高の{position_ratio:.1f}%")
            
            # 設定との比較
            if position_ratio > 25:
                print(f"  ⚠️  警告: ポジションサイズが大きい（設定: 10-20%）")
            elif position_ratio > 20:
                print(f"  🔥 高信頼度ポジション（20%）")
            elif position_ratio > 15:
                print(f"  ✅ 中信頼度ポジション（15%）")
            else:
                print(f"  🟢 通常ポジション（10%）")
    
    # 3. サマリー
    print("\n📊 サマリー:")
    print(f"  📍 総ポジション数: {total_positions}")
    print(f"  💰 合計未実現損益: ${total_pnl:,.2f}")
    
    # 4. リスク評価
    print("\n⚠️  リスク評価:")
    
    # ポジション数チェック
    if total_positions > 3:
        print(f"  🚨 警告: ポジション数が多すぎます（{total_positions}/3）")
    else:
        print(f"  ✅ ポジション数: 正常（{total_positions}/3）")
    
    # 証拠金使用率チェック
    if margin_ratio > 60:
        print(f"  🚨 警告: 証拠金使用率が高い（{margin_ratio:.1f}%）")
    elif margin_ratio > 40:
        print(f"  ⚠️  注意: 証拠金使用率がやや高い（{margin_ratio:.1f}%）")
    else:
        print(f"  ✅ 証拠金使用率: 正常（{margin_ratio:.1f}%）")
    
    # 5. 推奨事項
    print("\n💡 推奨事項:")
    if total_pnl > 0:
        print("  ✅ 利益が出ています。Dynamic Exit Matrixが機能しているか確認してください。")
    else:
        print("  📉 現在損失中。ストップロスが適切に設定されているか確認してください。")
    
    if total_positions >= 3:
        print("  ⚠️  最大ポジション数に達しています。新規エントリーは控えめに。")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        check_positions()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()