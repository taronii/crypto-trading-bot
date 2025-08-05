#!/usr/bin/env python3
"""
トレーディングシステムのシミュレーションテスト
信頼度計算、エントリー、決済ロジックの検証
"""

import os
import sys
import time
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List

# 現在のディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genius_multi_trading_v2_with_trading import GeniusMultiTrader
from genius_dynamic_exit_strategy import DynamicExitMatrix, PositionManager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockBybitService:
    """Bybitサービスのモッククラス"""
    
    def __init__(self):
        self.mock_data = self._generate_mock_data()
        
    def _generate_mock_data(self):
        """テスト用のモックデータ生成"""
        return {
            'BTCUSDT': {
                'price': 45000,
                'change_24h': 0.02,  # +2%
                'volume_24h': 1500000000,
                'klines': {
                    '5': self._generate_klines(45000, 0.001, 60),    # 微小な動き
                    '15': self._generate_klines(45000, 0.002, 96),   # 小さな上昇
                    '60': self._generate_klines(45000, 0.003, 168),  # 中程度の上昇
                    '240': self._generate_klines(45000, 0.004, 180), # 明確な上昇トレンド
                    'D': self._generate_klines(45000, 0.005, 30)     # 日足
                }
            },
            'SOLUSDT': {
                'price': 120,
                'change_24h': 0.05,  # +5%
                'volume_24h': 800000000,
                'klines': {
                    '5': self._generate_klines(120, 0.002, 60),
                    '15': self._generate_klines(120, 0.003, 96),
                    '60': self._generate_klines(120, 0.004, 168),
                    '240': self._generate_klines(120, 0.005, 180),
                    'D': self._generate_klines(120, 0.006, 30)
                }
            },
            'ETHUSDT': {
                'price': 2500,
                'change_24h': -0.01,  # -1%
                'volume_24h': 1200000000,
                'klines': {
                    '5': self._generate_klines(2500, -0.001, 60),
                    '15': self._generate_klines(2500, -0.001, 96),
                    '60': self._generate_klines(2500, -0.002, 168),
                    '240': self._generate_klines(2500, -0.002, 180),
                    'D': self._generate_klines(2500, -0.003, 30)
                }
            }
        }
    
    def _generate_klines(self, base_price: float, trend: float, count: int) -> List[Dict]:
        """ローソク足データの生成"""
        klines = []
        for i in range(count):
            # トレンドに基づいて価格を変動
            price = base_price * (1 + trend * i / count + np.random.uniform(-0.001, 0.001))
            high = price * (1 + abs(np.random.uniform(0, 0.002)))
            low = price * (1 - abs(np.random.uniform(0, 0.002)))
            open_price = price * (1 + np.random.uniform(-0.001, 0.001))
            volume = 100000 * np.random.uniform(0.8, 1.2)
            
            klines.append({
                'timestamp': datetime.now().isoformat() + 'Z',
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': volume
            })
        return klines
    
    def get_klines(self, symbol: str, interval: str, limit: int) -> List[Dict]:
        """モックのklineデータを返す"""
        if symbol in self.mock_data and interval in self.mock_data[symbol]['klines']:
            return self.mock_data[symbol]['klines'][interval][-limit:]
        return []
    
    def get_ticker(self, symbol: str) -> Dict:
        """モックのtickerデータを返す"""
        if symbol in self.mock_data:
            data = self.mock_data[symbol]
            return {
                'lastPrice': str(data['price']),
                'volume24h': str(data['volume_24h']),
                'price24hPcnt': str(data['change_24h'])
            }
        return {}
    
    def get_balance(self) -> Dict:
        """モックの残高データを返す"""
        return {
            'USDT': {
                'available_balance': 10000  # $10,000のテスト残高
            }
        }
    
    def place_order(self, **kwargs) -> Dict:
        """モックの注文実行"""
        logger.info(f"🔸 Mock Order Placed: {kwargs}")
        return {
            'retCode': 0,
            'result': {
                'orderId': 'mock_order_' + str(int(time.time())),
                'orderLinkId': 'mock_link_' + str(int(time.time()))
            }
        }
    
    def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """モックのレバレッジ設定"""
        logger.info(f"🔸 Mock Leverage Set: {symbol} = {leverage}x")
        return {'success': True, 'leverage': leverage}


def test_confidence_calculation():
    """信頼度計算のテスト"""
    logger.info("\n" + "="*60)
    logger.info("📊 信頼度計算テスト開始")
    logger.info("="*60)
    
    mock_bybit = MockBybitService()
    trader = GeniusMultiTrader(mock_bybit)
    
    # BTCトレンドの設定
    trader.btc_trend = 'up'
    
    symbols_to_test = ['BTCUSDT', 'SOLUSDT', 'ETHUSDT']
    results = []
    
    for symbol in symbols_to_test:
        logger.info(f"\n🔍 {symbol}の分析開始...")
        result = trader.analyze_genius(symbol)
        
        if result:
            logger.info(f"  ✅ 分析成功")
            logger.info(f"  💰 価格: ${result['price']:,.2f}")
            logger.info(f"  📈 方向: {result['direction']}")
            logger.info(f"  🎯 信頼度: {result['confidence']:.1%}")
            logger.info(f"  📊 24h変動: {result['change_24h']:+.2%}")
            logger.info(f"  📢 理由: {', '.join(result['reasons'])}")
            
            if result.get('atr'):
                logger.info(f"  📏 ATR: ${result['atr']:,.2f}")
            
            results.append(result)
        else:
            logger.error(f"  ❌ 分析失敗")
    
    return results


def test_entry_conditions(results: List[Dict]):
    """エントリー条件のテスト"""
    logger.info("\n" + "="*60)
    logger.info("🚀 エントリー条件テスト")
    logger.info("="*60)
    
    thresholds = {
        'BTCUSDT': 0.60,
        'ETHUSDT': 0.58,
        'SOLUSDT': 0.55,
        'default': 0.50
    }
    
    mock_bybit = MockBybitService()
    trader = GeniusMultiTrader(mock_bybit)
    usdt_balance = 10000
    
    opportunities = []
    
    for result in results:
        symbol = result['symbol']
        threshold = thresholds.get(symbol, thresholds['default'])
        
        logger.info(f"\n📋 {symbol}のエントリー判定:")
        logger.info(f"  信頼度: {result['confidence']:.1%} (閾値: {threshold:.0%})")
        
        if result['confidence'] >= threshold:
            logger.info(f"  ✅ エントリー条件満たす！")
            logger.info(f"  💵 ポジションサイズ: ${usdt_balance * result['position_size']:,.2f} ({result['position_size']:.1%})")
            
            # 模擬的な取引実行
            if len(trader.active_positions) < trader.max_positions:
                success = trader.execute_trade(result, usdt_balance)
                if success:
                    opportunities.append(result)
                    logger.info(f"  🎯 取引実行成功!")
                else:
                    logger.info(f"  ⚠️ 取引実行失敗")
            else:
                logger.info(f"  ⏭️ 最大ポジション数到達")
        else:
            logger.info(f"  ❌ エントリー条件満たさず")
    
    return opportunities


def test_exit_strategy(opportunities: List[Dict]):
    """Dynamic Exit Matrix決済戦略のテスト"""
    logger.info("\n" + "="*60)
    logger.info("🎯 Dynamic Exit Matrix決済戦略テスト")
    logger.info("="*60)
    
    exit_matrix = DynamicExitMatrix()
    position_manager = PositionManager(exit_matrix)
    
    for opp in opportunities:
        logger.info(f"\n📊 {opp['symbol']}の決済プラン:")
        
        exit_plan = opp.get('exit_plan')
        if not exit_plan:
            continue
            
        # 利確レベルの表示
        logger.info("\n  📈 段階的利確レベル:")
        for tp in exit_plan['take_profits']:
            logger.info(f"    レベル{tp['level']}: ${tp['target_price']:,.2f} "
                       f"({tp['percentage_gain']:+.1f}%) - {tp['exit_ratio']*100:.0f}%決済 "
                       f"[{tp['reason']}]")
        
        # 損切りレベルの表示
        logger.info("\n  🛡️ 段階的損切りレベル:")
        for sl in exit_plan['stop_losses']:
            logger.info(f"    レベル{sl['level']}: ${sl['trigger_price']:,.2f} "
                       f"({sl['percentage_loss']:.1f}%) - {sl['exit_ratio']*100:.0f}%決済 "
                       f"[{sl['reason']}]")
        
        # トレーリング設定の表示
        trailing = exit_plan['trailing_config']
        logger.info(f"\n  📈 トレーリングストップ:")
        logger.info(f"    発動: +{trailing['activation_profit']*100:.1f}%")
        logger.info(f"    コールバック: {trailing['callback_rate']*100:.1f}%")
        logger.info(f"    積極モード: {'有効' if trailing['aggressive_mode'] else '無効'}")
        
        # 価格変動シミュレーション
        logger.info(f"\n  🔄 価格変動シミュレーション:")
        entry_price = exit_plan['entry_price']
        
        # シナリオ1: 価格が上昇
        test_prices = [
            entry_price * 1.005,  # +0.5%
            entry_price * 1.015,  # +1.5%
            entry_price * 1.03,   # +3%
            entry_price * 1.05    # +5%
        ]
        
        position_manager.active_positions[opp['symbol']] = {
            'exit_plan': exit_plan,
            'order_id': 'test_order',
            'entry_time': datetime.now(),
            'highest_price': entry_price
        }
        
        for price in test_prices:
            actions = position_manager.check_exits(opp['symbol'], price)
            if actions:
                for action in actions:
                    logger.info(f"    価格 ${price:,.2f} ({(price/entry_price-1)*100:+.1f}%): "
                               f"{action['type']} - {action['reason']}")
        
        # シナリオ2: 価格が下落
        test_prices_down = [
            entry_price * 0.995,  # -0.5%
            entry_price * 0.985,  # -1.5%
            entry_price * 0.98    # -2%
        ]
        
        for price in test_prices_down:
            actions = position_manager.check_exits(opp['symbol'], price)
            if actions:
                for action in actions:
                    logger.info(f"    価格 ${price:,.2f} ({(price/entry_price-1)*100:.1f}%): "
                               f"{action['type']} - {action['reason']}")


def main():
    """メインテスト実行"""
    try:
        logger.info("🧠 Genius Trading System シミュレーションテスト開始")
        logger.info(f"📅 実行時刻: {datetime.now()}")
        
        # 1. 信頼度計算テスト
        results = test_confidence_calculation()
        
        # 2. エントリー条件テスト
        opportunities = test_entry_conditions(results)
        
        # 3. 決済戦略テスト
        test_exit_strategy(opportunities)
        
        # サマリー
        logger.info("\n" + "="*60)
        logger.info("📊 テスト結果サマリー")
        logger.info("="*60)
        logger.info(f"  分析通貨数: {len(results)}")
        logger.info(f"  エントリー機会: {len(opportunities)}")
        logger.info(f"  最高信頼度: {max(r['confidence'] for r in results):.1%}")
        logger.info(f"  平均信頼度: {np.mean([r['confidence'] for r in results]):.1%}")
        
        logger.info("\n✅ すべてのテストが完了しました！")
        
    except Exception as e:
        logger.error(f"❌ テスト中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()