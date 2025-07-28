#!/usr/bin/env python3
"""
改善された信頼度計算ロジック
より多くの取引機会を捉えながら、質を維持
"""

import numpy as np
from typing import Dict, List, Optional

class ImprovedConfidenceCalculator:
    """改善された信頼度計算"""
    
    def __init__(self):
        # 基本設定
        self.base_confidence = 0.15  # 15%のベーススコア
        
        # MTF重み（合計60%に調整）
        self.mtf_weights = {
            '5': 0.05,    # 5%（短期）
            '15': 0.10,   # 10%
            '60': 0.20,   # 20%（中期重視）
            '240': 0.25   # 25%（長期重視）
        }
        
        # その他の要素の重み（合計40%）
        self.volume_weight = 0.15      # 15%
        self.sr_weight = 0.15          # 15%
        self.rsi_weight = 0.10         # 10%
        
    def calculate_improved_confidence(self, 
                                    mtf_signals: Dict,
                                    volume_ratio: float,
                                    price_to_support: float,
                                    price_to_resistance: float,
                                    rsi: float,
                                    btc_trend: str,
                                    timezone_factor: float,
                                    symbol: str) -> Dict:
        """
        改善された信頼度計算
        """
        
        # 1. 基本信頼度からスタート
        long_score = self.base_confidence
        short_score = self.base_confidence
        reasons = []
        
        # 2. MTF分析（最大60%）
        for tf, signal in mtf_signals.items():
            weight = self.mtf_weights.get(tf, 0.05)
            
            # トレンド強度を調整（より寛容に）
            adjusted_strength = self._adjust_trend_strength(signal['strength'])
            
            if signal['trend'] == 'BULLISH':
                long_score += adjusted_strength * weight
                if tf in ['60', '240'] and adjusted_strength > 0.6:
                    reasons.append(f"{tf}分足: 上昇トレンド")
            elif signal['trend'] == 'BEARISH':
                short_score += adjusted_strength * weight
                if tf in ['60', '240'] and adjusted_strength > 0.6:
                    reasons.append(f"{tf}分足: 下降トレンド")
        
        # 3. ボリューム分析（最大15%）
        volume_score = self._calculate_volume_score(volume_ratio)
        if volume_score > 0:
            reasons.append(f"ボリューム: {volume_ratio:.1f}x")
            # ボリュームは方向性を持たないので両方に加算
            if long_score > short_score:
                long_score += volume_score * self.volume_weight
            else:
                short_score += volume_score * self.volume_weight
        
        # 4. サポート/レジスタンス（最大15%）
        if price_to_support < 0.02:  # サポートから2%以内
            sr_score = (0.02 - price_to_support) / 0.02  # 0-1の範囲
            long_score += sr_score * self.sr_weight
            reasons.append("サポート付近")
        
        if price_to_resistance < 0.02:  # レジスタンスから2%以内
            sr_score = (0.02 - price_to_resistance) / 0.02
            short_score += sr_score * self.sr_weight
            reasons.append("レジスタンス付近")
        
        # 5. RSI分析（最大10%）
        rsi_score = self._calculate_rsi_score(rsi)
        if rsi_score != 0:
            if rsi < 50:
                long_score += abs(rsi_score) * self.rsi_weight
                reasons.append(f"RSI: {rsi:.0f}")
            else:
                short_score += abs(rsi_score) * self.rsi_weight
                reasons.append(f"RSI: {rsi:.0f}")
        
        # 6. 最終スコアと方向性
        base_confidence = max(long_score, short_score)
        direction = "LONG" if long_score > short_score else "SHORT"
        
        # 7. 調整要素（加重平均方式）
        adjustments = []
        
        # BTC相関調整
        btc_adjustment = 1.0
        if symbol != 'BTCUSDT' and btc_trend == 'down' and direction == 'LONG':
            btc_adjustment = 0.8  # 0.7 → 0.8（より寛容）
            reasons.append("BTC下降調整")
        adjustments.append(btc_adjustment)
        
        # タイムゾーン調整
        adjustments.append(timezone_factor)
        
        # 加重平均で調整
        avg_adjustment = sum(adjustments) / len(adjustments)
        final_confidence = base_confidence * avg_adjustment
        
        # 8. 信頼度のスムージング（極端な値を避ける）
        final_confidence = self._smooth_confidence(final_confidence)
        
        return {
            'confidence': min(final_confidence, 0.90),  # 最大90%
            'direction': direction,
            'reasons': reasons,
            'components': {
                'base': self.base_confidence,
                'mtf': long_score - self.base_confidence if direction == 'LONG' else short_score - self.base_confidence,
                'volume': volume_score * self.volume_weight if volume_score > 0 else 0,
                'sr': (long_score if direction == 'LONG' else short_score) - self.base_confidence,
                'rsi': abs(rsi_score) * self.rsi_weight
            }
        }
    
    def _adjust_trend_strength(self, strength: float) -> float:
        """トレンド強度をより寛容に調整"""
        # 元の強度マッピング:
        # 0.3 (neutral) → 0.4
        # 0.5 (weak trend) → 0.7
        # 0.8 (strong trend) → 1.0
        
        if strength >= 0.8:
            return 1.0
        elif strength >= 0.5:
            return 0.7 + (strength - 0.5) * 0.6  # 0.7-0.88の範囲
        else:
            return strength * 1.3  # 弱いシグナルも少し強化
    
    def _calculate_volume_score(self, volume_ratio: float) -> float:
        """ボリュームスコア計算（0-1）"""
        if volume_ratio > 2.0:
            return 1.0  # 2倍以上は満点
        elif volume_ratio > 1.5:
            return 0.8
        elif volume_ratio > 1.2:
            return 0.5
        elif volume_ratio > 1.0:
            return 0.3
        else:
            return 0.0
    
    def _calculate_rsi_score(self, rsi: float) -> float:
        """RSIスコア計算（-1 to 1）"""
        if rsi < 20:
            return -1.0  # 極端な売られすぎ
        elif rsi < 30:
            return -0.7
        elif rsi < 40:
            return -0.3
        elif rsi > 80:
            return 1.0  # 極端な買われすぎ
        elif rsi > 70:
            return 0.7
        elif rsi > 60:
            return 0.3
        else:
            return 0.0  # 中立
    
    def _smooth_confidence(self, confidence: float) -> float:
        """信頼度をスムージング（極端な値を避ける）"""
        # 低すぎる値を引き上げ
        if confidence < 0.25:
            return 0.25 + (confidence * 0.3)
        # 高すぎる値を少し抑える
        elif confidence > 0.85:
            return 0.85 + ((confidence - 0.85) * 0.5)
        else:
            return confidence

class DynamicThresholdManager:
    """市場状況に応じた動的閾値管理"""
    
    def __init__(self):
        self.base_thresholds = {
            'BTCUSDT': 0.50,
            'ETHUSDT': 0.48,
            'SOLUSDT': 0.45,
            'default': 0.40
        }
        
    def get_dynamic_threshold(self, symbol: str, market_conditions: Dict) -> float:
        """市場状況に応じて閾値を動的に調整"""
        base = self.base_thresholds.get(symbol, self.base_thresholds['default'])
        
        # ボラティリティ調整
        if market_conditions.get('volatility') == 'high':
            base *= 0.9  # 高ボラ時は閾値を下げる
        elif market_conditions.get('volatility') == 'low':
            base *= 1.1  # 低ボラ時は閾値を上げる
        
        # トレンド強度調整
        trend_strength = market_conditions.get('trend_strength', 0.5)
        if trend_strength > 0.7:
            base *= 0.95  # 強いトレンドでは積極的に
        
        # 時間帯調整
        if 'good_session' in market_conditions.get('reasons', []):
            base *= 0.95
        
        return base

# 使用例
def integrate_improved_confidence(analyzer_instance):
    """既存のanalyze_geniusメソッドに統合"""
    
    calculator = ImprovedConfidenceCalculator()
    threshold_manager = DynamicThresholdManager()
    
    # analyze_genius内で使用
    # confidence = calculator.calculate_improved_confidence(...)
    # threshold = threshold_manager.get_dynamic_threshold(symbol, market_conditions)
    
    return calculator, threshold_manager