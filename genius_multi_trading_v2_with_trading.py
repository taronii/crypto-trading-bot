#!/usr/bin/env python3
"""
天才トレーダー版マルチ通貨取引システム（実際の取引機能付き）
"""

import os
import time
import logging
from datetime import datetime
import numpy as np
from typing import Dict, List, Optional
import pytz

from dotenv import load_dotenv
from services.bybit_service import BybitService
from genius_exit_strategy import GeniusExitStrategy
from genius_dynamic_exit_strategy import DynamicExitMatrix, PositionManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeniusMultiTrader:
    """天才トレーダーの取引ロジック"""
    
    def __init__(self, bybit_client):
        self.bybit = bybit_client
        self.correlations = {
            # 高相関グループ
            'major': ['BTCUSDT', 'ETHUSDT'],
            'defi': ['LINKUSDT', 'AVAXUSDT'],
            'meme': ['DOGEUSDT'],
            'layer2': ['ARBUSDT', 'MATICUSDT'],
            'payments': ['XRPUSDT', 'BNBUSDT'],
            'smart_contract': ['SOLUSDT']
        }
        self.btc_trend = None  # ビットコインのトレンドを保持
        self.active_positions = {}  # アクティブなポジション
        self.max_positions = 3  # 最大同時ポジション数（リスク管理のため3に制限）
        self.exit_strategy = GeniusExitStrategy()  # 天才的な決済戦略
        self.dynamic_exit = DynamicExitMatrix()  # Dynamic Exit Matrix統合
        self.position_manager = PositionManager(self.dynamic_exit)  # ポジション管理
    
    def analyze_genius(self, symbol: str) -> Optional[Dict]:
        """天才レベルの分析"""
        try:
            # 1. マルチタイムフレーム分析
            timeframes = {
                '5': 60,    # 5分足60本 = 5時間
                '15': 96,   # 15分足96本 = 24時間
                '60': 168,  # 1時間足168本 = 1週間
                '240': 180  # 4時間足180本 = 1ヶ月
            }
            
            mtf_signals = {}
            for tf, limit in timeframes.items():
                klines = self.bybit.get_klines(symbol, tf, limit)
                if klines:
                    signal = self._analyze_timeframe(klines, tf)
                    mtf_signals[tf] = signal
                time.sleep(0.1)
            
            # 2. 現在価格とボリューム
            ticker = self.bybit.get_ticker(symbol)
            current_price = float(ticker.get('lastPrice', 0))
            volume_24h = float(ticker.get('volume24h', 0))
            change_24h = float(ticker.get('price24hPcnt', 0))
            
            # 3. サポート/レジスタンス
            klines_daily = self.bybit.get_klines(symbol, 'D', 30)  # 日足30本
            sr_levels = self._find_sr_levels(klines_daily)
            
            # ATR計算（Priority 1改善）
            atr_14 = self._calculate_atr(klines_daily, 14) if klines_daily else None
            
            # 4. 総合判定
            long_score = 0
            short_score = 0
            reasons = []
            
            # タイムフレーム分析
            for tf, signal in mtf_signals.items():
                if signal['trend'] == 'BULLISH':
                    weight = {'5': 0.1, '15': 0.2, '60': 0.3, '240': 0.4}.get(tf, 0.1)
                    long_score += signal['strength'] * weight
                    if tf in ['60', '240']:  # 上位時間足を重視
                        reasons.append(f"{tf}分足: 上昇トレンド")
                elif signal['trend'] == 'BEARISH':
                    weight = {'5': 0.1, '15': 0.2, '60': 0.3, '240': 0.4}.get(tf, 0.1)
                    short_score += signal['strength'] * weight
                    if tf in ['60', '240']:
                        reasons.append(f"{tf}分足: 下降トレンド")
            
            # ボリューム分析
            avg_volume = np.mean([float(k['volume']) for k in klines_daily[-20:]])
            if volume_24h > avg_volume * 1.5:
                reasons.append("高ボリューム")
                if change_24h > 0:
                    long_score += 0.1
                else:
                    short_score += 0.1
            
            # サポート/レジスタンス
            nearest_support = self._find_nearest_level(current_price, sr_levels['support'])
            nearest_resistance = self._find_nearest_level(current_price, sr_levels['resistance'])
            
            if nearest_support and abs(current_price - nearest_support) / current_price < 0.02:
                long_score += 0.15
                reasons.append(f"サポート付近 ${nearest_support:,.2f}")
            
            if nearest_resistance and abs(current_price - nearest_resistance) / current_price < 0.02:
                short_score += 0.15
                reasons.append(f"レジスタンス付近 ${nearest_resistance:,.2f}")
            
            # RSI計算
            rsi = self._calculate_rsi(klines_daily[-14:])
            if rsi < 30:
                long_score += 0.1
                reasons.append(f"売られすぎ (RSI: {rsi:.0f})")
            elif rsi > 70:
                short_score += 0.1
                reasons.append(f"買われすぎ (RSI: {rsi:.0f})")
            
            # 最終判定
            confidence = max(long_score, short_score)
            direction = "LONG" if long_score > short_score else "SHORT"
            
            # リスク調整
            risk_adjustment = self._calculate_risk_adjustment(symbol, direction)
            confidence *= risk_adjustment
            
            # ビットコイン相関フィルター（Priority 1改善）
            if symbol != 'BTCUSDT' and self.btc_trend == 'down' and direction == 'LONG':
                confidence *= 0.7
                reasons.append("BTC下降トレンドで調整")
            
            # タイムゾーン戦略調整（Priority 1改善）
            timezone_adjustment = self._get_timezone_adjustment()
            confidence *= timezone_adjustment['confidence_multiplier']
            if timezone_adjustment['reason']:
                reasons.append(timezone_adjustment['reason'])
            
            # 市場状況をまとめる
            market_conditions = {
                'trend_strength': max(long_score, short_score),
                'volatility': 'high' if atr_14 and atr_14 / current_price > 0.03 else 'normal',
                'volume_ratio': volume_24h / avg_volume if avg_volume > 0 else 1,
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance
            }
            
            # Dynamic Exit Matrixで決済戦略を計算
            position_size = self._calculate_position_size(confidence, risk_adjustment)
            exit_plan = self.dynamic_exit.create_exit_plan(
                entry_price=current_price,
                atr=atr_14 or current_price * 0.02,
                confidence=confidence,
                market_conditions=market_conditions,
                position_size=position_size,
                symbol=symbol
            )
            
            # 旧形式との互換性のため
            exit_levels = self.exit_strategy.calculate_dynamic_exit_levels(
                entry_price=current_price,
                atr=atr_14 or current_price * 0.02,
                confidence=confidence,
                market_conditions=market_conditions,
                symbol=symbol
            )
            
            return {
                'symbol': symbol,
                'price': current_price,
                'confidence': min(confidence, 0.85),  # 最大85%
                'direction': direction,
                'change_24h': change_24h,
                'volume_ratio': volume_24h / avg_volume if avg_volume > 0 else 1,
                'reasons': reasons,
                'stop_loss': exit_levels['stop_loss']['price'],
                'take_profits': [tp['price'] for tp in exit_levels['take_profits']],
                'exit_strategy': exit_levels,  # 詳細な決済戦略
                'exit_plan': exit_plan,  # Dynamic Exit Matrixプラン
                'position_size': position_size,
                'atr': atr_14,
                'market_conditions': market_conditions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def execute_trade(self, opportunity: Dict, usdt_balance: float) -> bool:
        """実際の取引を実行"""
        try:
            symbol = opportunity['symbol']
            
            # 既にポジションがある場合はスキップ
            if symbol in self.active_positions:
                logger.info(f"  ⏭️  {symbol}: 既にポジションあり")
                return False
            
            # 最大ポジション数チェック
            if len(self.active_positions) >= self.max_positions:
                logger.info(f"  ⏭️  最大ポジション数に到達 ({self.max_positions})")
                return False
            
            # ポジションサイズ計算
            position_value = usdt_balance * opportunity['position_size']
            quantity = position_value / opportunity['price']
            
            # 最小取引単位に調整
            quantity = self._adjust_quantity(symbol, quantity)
            
            if quantity <= 0:
                logger.info(f"  ⚠️  {symbol}: 取引数量が小さすぎます")
                return False
            
            # 注文実行
            logger.info(f"\n  🎯 取引実行: {symbol}")
            logger.info(f"     方向: {opportunity['direction']}")
            logger.info(f"     数量: {quantity:.6f}")
            logger.info(f"     価格: ${opportunity['price']:,.2f}")
            logger.info(f"     ストップロス: ${opportunity['stop_loss']:,.2f}")
            
            # Dynamic Exit Matrix情報を表示
            if opportunity.get('exit_plan'):
                exit_plan = opportunity['exit_plan']
                logger.info(f"     🎯 Dynamic Exit Matrix戦略:")
                logger.info(f"     📈 利確レベル: {len(exit_plan['take_profits'])}段階")
                for tp in exit_plan['take_profits']:
                    logger.info(f"       TP{tp['level']}: ${tp['target_price']:,.2f} ({tp['percentage_gain']:+.1f}%) - {tp['exit_ratio']*100:.0f}%決済")
                logger.info(f"     🛡️  損切りレベル: {len(exit_plan['stop_losses'])}段階")
                for sl in exit_plan['stop_losses']:
                    logger.info(f"       SL{sl['level']}: ${sl['trigger_price']:,.2f} ({sl['percentage_loss']:.1f}%) - {sl['exit_ratio']*100:.0f}%損切り")
                
                # トレーリング情報
                trailing = exit_plan['trailing_config']
                if trailing['enabled']:
                    logger.info(f"     📈 トレーリング: {trailing['activation_profit']*100:.1f}%で発動, {trailing['callback_rate']*100:.1f}%押し目で決済")
            
            # Dynamic Exit Matrixから最初の利確と最終損切りを取得
            if opportunity.get('exit_plan'):
                first_tp = opportunity['exit_plan']['take_profits'][0]['target_price']
                final_sl = opportunity['exit_plan']['stop_losses'][-1]['trigger_price']
            else:
                first_tp = opportunity['take_profits'][0] if opportunity.get('take_profits') else None
                final_sl = opportunity['stop_loss']
            
            # 実際の注文を実行
            order = self.bybit.place_order(
                symbol=symbol,
                side='Buy' if opportunity['direction'] == 'LONG' else 'Sell',
                qty=quantity,
                stop_loss=final_sl,
                take_profit=first_tp  # 最初の利確ポイントを設定
            )
            
            if order and order.get('retCode') == 0:
                # ポジション管理に登録（Dynamic Exit Matrix対応）
                if opportunity.get('exit_plan'):
                    self.position_manager.active_positions[symbol] = {
                        'exit_plan': opportunity['exit_plan'],
                        'order_id': order['result']['orderId'],
                        'entry_time': datetime.now(),
                        'highest_price': opportunity['price']
                    }
                
                self.active_positions[symbol] = {
                    'entry_price': opportunity['price'],
                    'quantity': quantity,
                    'direction': opportunity['direction'],
                    'stop_loss': final_sl,
                    'take_profits': opportunity['take_profits'],
                    'exit_strategy': opportunity.get('exit_strategy'),
                    'exit_plan': opportunity.get('exit_plan'),
                    'entry_time': datetime.now(),
                    'confidence': opportunity['confidence']
                }
                logger.info(f"  ✅ {symbol}: 注文成功!")
                return True
            else:
                logger.error(f"  ❌ {symbol}: 注文失敗 - {order}")
                return False
            
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return False
    
    def _adjust_quantity(self, symbol: str, quantity: float) -> float:
        """取引数量を最小単位に調整"""
        # 通貨ごとの最小取引単位（例）
        min_quantities = {
            'BTCUSDT': 0.001,
            'ETHUSDT': 0.01,
            'SOLUSDT': 0.1,
            'BNBUSDT': 0.01,
            'XRPUSDT': 1,
            'DOGEUSDT': 1,
            'AVAXUSDT': 0.1,
            'LINKUSDT': 0.1,
            'MATICUSDT': 1,
            'ARBUSDT': 1
        }
        
        min_qty = min_quantities.get(symbol, 0.01)
        return max(quantity - (quantity % min_qty), min_qty)
    
    def _analyze_timeframe(self, klines: List, timeframe: str) -> Dict:
        """時間枠ごとの分析"""
        closes = np.array([float(k['close']) for k in klines])
        
        # EMA計算
        ema_short = self._calculate_ema(closes, 20)
        ema_long = self._calculate_ema(closes, 50)
        
        # トレンド判定
        if ema_short[-1] > ema_long[-1] and ema_short[-5] <= ema_long[-5]:
            trend = 'BULLISH'
            strength = 0.8
        elif ema_short[-1] < ema_long[-1] and ema_short[-5] >= ema_long[-5]:
            trend = 'BEARISH'
            strength = 0.8
        elif ema_short[-1] > ema_long[-1]:
            trend = 'BULLISH'
            strength = 0.5
        elif ema_short[-1] < ema_long[-1]:
            trend = 'BEARISH'
            strength = 0.5
        else:
            trend = 'NEUTRAL'
            strength = 0.3
            
        return {'trend': trend, 'strength': strength}
    
    def _find_sr_levels(self, klines: List) -> Dict:
        """サポート/レジスタンスレベル検出"""
        if not klines:
            return {'support': [], 'resistance': []}
            
        highs = [float(k['high']) for k in klines]
        lows = [float(k['low']) for k in klines]
        
        # ピボットポイント
        resistance = []
        support = []
        
        for i in range(2, len(klines) - 2):
            # レジスタンス（高値のピーク）
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistance.append(highs[i])
            
            # サポート（安値の谷）
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                support.append(lows[i])
        
        return {
            'support': sorted(set(support), reverse=True)[:3],  # 上位3つ
            'resistance': sorted(set(resistance))[:3]  # 下位3つ
        }
    
    def _find_nearest_level(self, price: float, levels: List[float]) -> Optional[float]:
        """最も近い価格レベルを検索"""
        if not levels:
            return None
        return min(levels, key=lambda x: abs(x - price))
    
    def _calculate_rsi(self, klines: List, period: int = 14) -> float:
        """RSI計算"""
        if len(klines) < period:
            return 50  # デフォルト
            
        closes = [float(k['close']) for k in klines]
        deltas = np.diff(closes)
        gains = deltas[deltas > 0]
        losses = -deltas[deltas < 0]
        
        avg_gain = np.mean(gains) if len(gains) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """指数移動平均計算"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(data)
        ema[0] = data[0]
        
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
            
        return ema
    
    def _calculate_risk_adjustment(self, symbol: str, direction: str) -> float:
        """リスク調整係数"""
        # 相関リスク
        group = None
        for g, symbols in self.correlations.items():
            if symbol in symbols:
                group = g
                break
        
        if group:
            # 同じグループの通貨が多いほどリスク増
            group_count = len([s for s in self.correlations[group]])
            if group_count > 1:
                return 0.8  # 20%削減
        
        return 1.0
    
    def _calculate_atr(self, klines: List, period: int = 14) -> float:
        """ATR（Average True Range）計算"""
        if not klines or len(klines) < period + 1:
            return 0
        
        true_ranges = []
        for i in range(1, len(klines)):
            high = float(klines[i]['high'])
            low = float(klines[i]['low'])
            prev_close = float(klines[i-1]['close'])
            
            tr = max([
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            ])
            true_ranges.append(tr)
        
        # 最新のATR値
        if len(true_ranges) >= period:
            return np.mean(true_ranges[-period:])
        return 0
    
    def _calculate_stop_loss_with_atr(self, price: float, direction: str, sr_levels: Dict, atr: float) -> float:
        """ATRベースのストップロス計算（Priority 1改善）"""
        if atr and atr > 0:
            # ATRの2倍をストップロスとして使用
            atr_stop = 2.0 * atr
            
            if direction == "LONG":
                atr_based_stop = price - atr_stop
                # サポートレベルも考慮
                if sr_levels['support']:
                    support_stop = sr_levels['support'][0] * 0.995
                    return max(atr_based_stop, support_stop)  # より保守的な方を選択
                return atr_based_stop
            else:
                atr_based_stop = price + atr_stop
                # レジスタンスレベルも考慮
                if sr_levels['resistance']:
                    resistance_stop = sr_levels['resistance'][0] * 1.005
                    return min(atr_based_stop, resistance_stop)
                return atr_based_stop
        
        # ATRが計算できない場合は既存のロジックを使用
        return self._calculate_stop_loss(price, direction, sr_levels)
    
    def _get_timezone_adjustment(self) -> Dict:
        """タイムゾーンベースの戦略調整（Priority 1改善）"""
        # 現在時刻（UTC）
        utc_now = datetime.now(pytz.UTC)
        
        # 各市場の時間帯
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        london_tz = pytz.timezone('Europe/London')
        ny_tz = pytz.timezone('America/New_York')
        
        # 現在時刻を各タイムゾーンに変換
        tokyo_time = utc_now.astimezone(tokyo_tz)
        london_time = utc_now.astimezone(london_tz)
        ny_time = utc_now.astimezone(ny_tz)
        
        hour_tokyo = tokyo_time.hour
        hour_london = london_time.hour
        hour_ny = ny_time.hour
        
        # アジア時間（東京時間 9:00-15:00）
        if 9 <= hour_tokyo <= 15:
            return {
                'confidence_multiplier': 1.2,  # レンジ相場が多いため信頼度上げる
                'reason': 'アジア時間（レンジ相場）'
            }
        
        # ロンドン時間（ロンドン時間 8:00-16:00）
        elif 8 <= hour_london <= 16:
            return {
                'confidence_multiplier': 1.1,  # 高ボラティリティ
                'reason': 'ロンドン時間（高流動性）'
            }
        
        # ニューヨーク時間（NY時間 9:00-16:00）
        elif 9 <= hour_ny <= 16:
            return {
                'confidence_multiplier': 1.15,  # トレンドが出やすい
                'reason': 'NY時間（トレンド相場）'
            }
        
        # オーバーラップ時間（ロンドン・NY重複）
        elif 13 <= hour_london <= 16 and 8 <= hour_ny <= 11:
            return {
                'confidence_multiplier': 1.25,  # 最高の流動性
                'reason': 'ロンドン・NY重複時間'
            }
        
        # その他の時間
        return {
            'confidence_multiplier': 0.9,  # 流動性が低い
            'reason': None
        }
    
    def _calculate_stop_loss(self, price: float, direction: str, sr_levels: Dict) -> float:
        """ストップロス計算"""
        if direction == "LONG":
            # 直近サポートの少し下
            if sr_levels['support']:
                return sr_levels['support'][0] * 0.995
            else:
                return price * 0.98  # 2%
        else:
            # 直近レジスタンスの少し上
            if sr_levels['resistance']:
                return sr_levels['resistance'][0] * 1.005
            else:
                return price * 1.02  # 2%
    
    def _calculate_take_profits(self, price: float, direction: str, sr_levels: Dict) -> List[float]:
        """段階的利確ポイント（旧バージョン、互換性のため残す）"""
        # 新しいexit_strategyがより高度な計算を行う
        if direction == "LONG":
            base = sr_levels['resistance'] if sr_levels['resistance'] else []
            return [
                price * 1.015,  # 1.5%
                price * 1.03,   # 3%
                base[0] if base else price * 1.05  # レジスタンスまたは5%
            ]
        else:
            base = sr_levels['support'] if sr_levels['support'] else []
            return [
                price * 0.985,  # 1.5%
                price * 0.97,   # 3%
                base[0] if base else price * 0.95  # サポートまたは5%
            ]
    
    def _calculate_position_size(self, confidence: float, risk_adj: float) -> float:
        """ポジションサイズ計算（積極的設定）"""
        base_size = 0.15  # 基本15%（変更前: 10%）⚡リスク増加V2
        
        # 信頼度による調整
        if confidence > 0.7:
            size_multiplier = 2.0   # 30%（変更前: 20%）⚡リスク増加V2
        elif confidence > 0.5:
            size_multiplier = 1.5   # 22.5%（変更前: 15%）⚡リスク増加V2
        else:
            size_multiplier = 1.0   # 15%（変更前: 10%）⚡リスク増加V2
            
        return base_size * size_multiplier * risk_adj
    
    def monitor_positions(self):
        """Dynamic Exit Matrixによるポジション監視と段階的決済"""
        while True:
            try:
                for symbol in list(self.position_manager.active_positions.keys()):
                    # 現在価格の取得
                    ticker = self.bybit.get_ticker(symbol)
                    if not ticker:
                        continue
                    
                    current_price = float(ticker.get('lastPrice', 0))
                    
                    # 決済条件のチェック
                    actions = self.position_manager.check_exits(symbol, current_price)
                    
                    # 決済アクションの実行
                    for action in actions:
                        self._execute_exit_action(symbol, action)
                
                time.sleep(5)  # 5秒ごとにチェック
                
            except Exception as e:
                logger.error(f"Position monitoring error: {e}")
                time.sleep(10)
    
    def _execute_exit_action(self, symbol: str, action: Dict):
        """決済アクションの実行"""
        try:
            position = self.position_manager.active_positions[symbol]
            remaining_size = position['exit_plan']['execution_status']['remaining_size']
            
            # 決済数量の計算
            exit_size = remaining_size * action['exit_ratio']
            
            logger.info(f"\n  🎯 {action['type'].upper()}: {symbol}")
            logger.info(f"     レベル: {action.get('level', 'N/A')}")
            logger.info(f"     数量: {exit_size:.6f} ({action['exit_ratio']*100:.0f}%)")
            logger.info(f"     価格: ${action['price']:,.2f}")
            logger.info(f"     理由: {action['reason']}")
            
            # 部分決済の実行
            close_order = self.bybit.close_position(
                symbol=symbol,
                qty=exit_size
            )
            
            if close_order and close_order.get('success'):
                # 実行状態の更新
                position['exit_plan']['execution_status']['remaining_size'] -= exit_size
                
                if action['type'] == 'take_profit':
                    position['exit_plan']['execution_status']['tp_executed'].append(action.get('level', 0))
                elif action['type'] == 'stop_loss':
                    position['exit_plan']['execution_status']['sl_executed'].append(action.get('level', 0))
                
                logger.info(f"  ✅ 部分決済成功!")
                
                # 全決済完了の場合
                if position['exit_plan']['execution_status']['remaining_size'] <= 0:
                    del self.position_manager.active_positions[symbol]
                    logger.info(f"  🏁 {symbol}: ポジション完全決済")
            else:
                logger.error(f"  ❌ 部分決済失敗: {close_order}")
                
        except Exception as e:
            logger.error(f"Exit action error for {symbol}: {e}")


def main():
    load_dotenv()
    
    logger.info("="*50)
    logger.info("🧠 Genius Multi-Currency Trading System")
    logger.info("="*50)
    
    # 初期化
    bybit = BybitService(
        api_key=os.getenv('BYBIT_API_KEY'),
        api_secret=os.getenv('BYBIT_API_SECRET'),
        testnet=False
    )
    
    trader = GeniusMultiTrader(bybit)
    
    # 残高確認
    balance = bybit.get_balance()
    usdt_balance = balance.get('USDT', {}).get('available_balance', 0)
    logger.info(f"💰 USDT Balance: ${usdt_balance:,.2f}")
    
    # 10通貨
    symbols = [
        'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT',
        'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT', 'MATICUSDT', 'ARBUSDT'
    ]
    
    # 天才の閾値（厳しめ）
    thresholds = {
        'BTCUSDT': 0.60,   # メジャー通貨は慎重に
        'ETHUSDT': 0.58,
        'SOLUSDT': 0.55,
        'default': 0.50    # その他は50%以上
    }
    
    # メインループ
    while True:
        try:
            logger.info("\n" + "="*50)
            logger.info(f"🧠 Genius Analysis Started...")
            
            opportunities = []
            
            # ビットコインのトレンドを先に確認（Priority 1改善）
            btc_result = trader.analyze_genius('BTCUSDT')
            if btc_result:
                btc_change = btc_result['change_24h']
                if btc_change < -0.02:  # -2%以下
                    trader.btc_trend = 'down'
                elif btc_change > 0.02:  # +2%以上
                    trader.btc_trend = 'up'
                else:
                    trader.btc_trend = 'neutral'
                logger.info(f"📊 BTC Trend: {trader.btc_trend} ({btc_change:+.2%})")
            
            for symbol in symbols:
                result = trader.analyze_genius(symbol)
                if result:
                    threshold = thresholds.get(symbol, thresholds['default'])
                    
                    logger.info(f"\n{symbol}:")
                    logger.info(f"  Price: ${result['price']:,.2f}")
                    logger.info(f"  Direction: {result['direction']}")
                    logger.info(f"  Confidence: {result['confidence']:.1%} (Need: {threshold:.0%})")
                    logger.info(f"  Volume Ratio: {result['volume_ratio']:.1f}x")
                    logger.info(f"  Reasons: {', '.join(result['reasons'])}")
                    if result.get('atr'):
                        logger.info(f"  ATR: ${result['atr']:,.2f}")
                    
                    if result['confidence'] >= threshold:
                        logger.info(f"  ✅ OPPORTUNITY FOUND!")
                        logger.info(f"  Stop Loss: ${result['stop_loss']:,.2f}")
                        logger.info(f"  Take Profits: {[f'${tp:,.2f}' for tp in result['take_profits']]}")
                        logger.info(f"  Position Size: {result['position_size']:.1%} of balance")
                        
                        # 決済戦略の詳細
                        if result.get('exit_strategy'):
                            partial_plan = result['exit_strategy']['partial_exit_plan']
                            logger.info(f"  🎯 部分決済プラン:")
                            for plan in partial_plan:
                                logger.info(f"    - レベル{plan['level']}: {plan['exit_ratio']*100:.0f}% ({plan['reason']})")
                        
                        opportunities.append(result)
                        
                        # 実際の取引を実行
                        if trader.execute_trade(result, usdt_balance):
                            logger.info(f"  🎯 取引実行完了!")
                
                time.sleep(1)  # API制限
            
            # 機会のサマリー
            if opportunities:
                logger.info(f"\n🎯 Found {len(opportunities)} opportunities")
                logger.info("Sorted by confidence:")
                for opp in sorted(opportunities, key=lambda x: x['confidence'], reverse=True):
                    logger.info(f"  {opp['symbol']}: {opp['direction']} @ {opp['confidence']:.1%}")
            else:
                logger.info("\n⏳ No opportunities meet genius criteria")
            
            # アクティブポジション表示と管理
            if trader.active_positions:
                logger.info(f"\n📊 Active Positions: {len(trader.active_positions)}")
                for symbol, pos in trader.active_positions.items():
                    # 現在価格を取得
                    ticker = bybit.get_ticker(symbol)
                    if ticker:
                        current_price = float(ticker.get('lastPrice', pos['entry_price']))
                        pnl = (current_price / pos['entry_price'] - 1) * 100
                        logger.info(f"  {symbol}: {pos['direction']} @ ${pos['entry_price']:,.2f} | PnL: {pnl:+.2f}%")
                        
                        # ポジション管理の推奨
                        if abs(pnl) > 1:  # 1%以上の変動
                            recommendations = trader.exit_strategy.manage_position(
                                pos, 
                                {'price': current_price, 'symbol': symbol}
                            )
                            if recommendations['recommendations']:
                                logger.info(f"    💡 推奨: {recommendations['recommendations'][0]['reason']}")
            
            # 5分待機
            logger.info(f"\n💤 Next analysis in 5 minutes...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            logger.info("\n👋 Shutting down...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    import threading
    
    # メインの取引スレッド
    main_thread = threading.Thread(target=main)
    main_thread.start()
    
    # ポジション監視スレッド（Dynamic Exit Matrix）
    logger.info("🔍 Starting Dynamic Exit Matrix position monitor...")
    
    # メインループが開始してtraderインスタンスが作成されるまで待機
    time.sleep(10)
    
    # 注：実際の実装では、traderインスタンスをグローバルに共有するか、
    # より適切な方法でポジション監視を統合する必要があります
    
    main_thread.join()