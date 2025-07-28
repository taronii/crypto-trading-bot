#!/usr/bin/env python3
"""
天才トレーダー版マルチ通貨取引システム
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
            
            return {
                'symbol': symbol,
                'price': current_price,
                'confidence': min(confidence, 0.85),  # 最大85%
                'direction': direction,
                'change_24h': change_24h,
                'volume_ratio': volume_24h / avg_volume if avg_volume > 0 else 1,
                'reasons': reasons,
                'stop_loss': self._calculate_stop_loss_with_atr(current_price, direction, sr_levels, atr_14),
                'take_profits': self._calculate_take_profits(current_price, direction, sr_levels),
                'position_size': self._calculate_position_size(confidence, risk_adjustment),
                'atr': atr_14
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
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
        """段階的利確ポイント"""
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
        """ポジションサイズ計算"""
        base_size = 0.01  # 基本1%
        
        # 信頼度による調整
        if confidence > 0.7:
            size_multiplier = 1.5
        elif confidence > 0.5:
            size_multiplier = 1.0
        else:
            size_multiplier = 0.5
            
        return base_size * size_multiplier * risk_adj


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
                        
                        opportunities.append(result)
                
                time.sleep(1)  # API制限
            
            # 機会のサマリー
            if opportunities:
                logger.info(f"\n🎯 Found {len(opportunities)} opportunities")
                logger.info("Sorted by confidence:")
                for opp in sorted(opportunities, key=lambda x: x['confidence'], reverse=True):
                    logger.info(f"  {opp['symbol']}: {opp['direction']} @ {opp['confidence']:.1%}")
            else:
                logger.info("\n⏳ No opportunities meet genius criteria")
            
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
    main()