#!/usr/bin/env python3
"""
天才トレーダーの決済戦略
勝率を最大化する高度な決済ロジック
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GeniusExitStrategy:
    """天才的な決済戦略"""
    
    def __init__(self):
        self.position_data = {}  # ポジション別のデータ
        
    def calculate_dynamic_exit_levels(self, 
                                    entry_price: float, 
                                    atr: float,
                                    confidence: float,
                                    market_conditions: Dict,
                                    symbol: str) -> Dict:
        """
        動的な決済レベルを計算
        市場状況と信頼度に応じて最適化
        """
        
        # 1. ベースとなる利確レベル
        base_tp_levels = self._calculate_base_tp_levels(entry_price, atr, confidence)
        
        # 2. 市場状況による調整
        adjusted_tp_levels = self._adjust_for_market_conditions(
            base_tp_levels, market_conditions, symbol
        )
        
        # 3. スマートストップロス
        smart_stop_loss = self._calculate_smart_stop_loss(
            entry_price, atr, market_conditions
        )
        
        # 4. トレーリングストップ設定
        trailing_config = self._get_trailing_config(confidence, market_conditions)
        
        return {
            'take_profits': adjusted_tp_levels,
            'stop_loss': smart_stop_loss,
            'trailing_config': trailing_config,
            'partial_exit_plan': self._create_partial_exit_plan(confidence)
        }
    
    def _calculate_base_tp_levels(self, price: float, atr: float, confidence: float) -> List[Dict]:
        """
        基本的な利確レベルを計算
        ATRとconfidenceに基づく動的調整
        """
        
        # 信頼度による利確倍率
        if confidence > 0.8:
            # 高信頼度: より大きな利益を狙う
            atr_multipliers = [1.0, 2.0, 3.5, 5.0]  # 4段階
            percentages = [0.015, 0.03, 0.05, 0.08]
        elif confidence > 0.65:
            # 中高信頼度: バランス型
            atr_multipliers = [0.8, 1.5, 2.5, 3.5]
            percentages = [0.012, 0.025, 0.04, 0.06]
        else:
            # 中信頼度: 確実な利確
            atr_multipliers = [0.6, 1.2, 2.0]  # 3段階
            percentages = [0.01, 0.02, 0.035]
        
        tp_levels = []
        
        for i, (atr_mult, pct) in enumerate(zip(atr_multipliers, percentages)):
            # ATRベースとパーセントベースの大きい方を採用
            atr_based = price + (atr * atr_mult)
            pct_based = price * (1 + pct)
            
            tp_price = max(atr_based, pct_based)
            
            tp_levels.append({
                'level': i + 1,
                'price': tp_price,
                'percentage': (tp_price / price - 1) * 100,
                'reason': f'ATR×{atr_mult} or {pct*100:.1f}%'
            })
        
        return tp_levels
    
    def _adjust_for_market_conditions(self, tp_levels: List[Dict], 
                                    market_conditions: Dict, 
                                    symbol: str) -> List[Dict]:
        """
        市場状況に応じて利確レベルを調整
        """
        adjusted_levels = []
        
        # 市場のトレンド強度
        trend_strength = market_conditions.get('trend_strength', 0.5)
        volatility = market_conditions.get('volatility', 'normal')
        volume_ratio = market_conditions.get('volume_ratio', 1.0)
        
        for tp in tp_levels:
            adjusted_price = tp['price']
            
            # 強いトレンドの場合、利確を遠くに
            if trend_strength > 0.7:
                adjusted_price *= 1.15
                tp['reason'] += ' +トレンド継続'
            
            # 高ボリュームの場合、モメンタム継続
            if volume_ratio > 2.0:
                adjusted_price *= 1.1
                tp['reason'] += ' +高ボリューム'
            
            # 高ボラティリティの場合、早めの利確
            if volatility == 'high':
                adjusted_price *= 0.9
                tp['reason'] += ' -高ボラ調整'
            
            tp['price'] = adjusted_price
            tp['percentage'] = (adjusted_price / tp_levels[0]['price'] - 1) * 100
            adjusted_levels.append(tp)
        
        return adjusted_levels
    
    def _calculate_smart_stop_loss(self, price: float, atr: float, 
                                 market_conditions: Dict) -> Dict:
        """
        スマートストップロス計算
        市場状況に応じて動的に調整
        """
        
        # 基本はATRの2倍
        base_stop = price - (atr * 2.0)
        
        # ボラティリティによる調整
        volatility = market_conditions.get('volatility', 'normal')
        if volatility == 'high':
            # 高ボラ時は広めに
            stop_loss = price - (atr * 2.5)
        elif volatility == 'low':
            # 低ボラ時は狭めに
            stop_loss = price - (atr * 1.5)
        else:
            stop_loss = base_stop
        
        # サポートレベルを考慮
        nearest_support = market_conditions.get('nearest_support')
        if nearest_support and nearest_support > stop_loss:
            # サポートの少し下に調整
            stop_loss = nearest_support * 0.995
        
        return {
            'price': stop_loss,
            'percentage': (stop_loss / price - 1) * 100,
            'type': 'smart_stop',
            'reason': f'ATR×2 + {volatility}ボラ調整'
        }
    
    def _get_trailing_config(self, confidence: float, market_conditions: Dict) -> Dict:
        """
        トレーリングストップの設定
        """
        trend_strength = market_conditions.get('trend_strength', 0.5)
        
        if confidence > 0.7 and trend_strength > 0.6:
            # 強いトレンドに乗る
            return {
                'enabled': True,
                'activation_profit': 0.015,  # 1.5%利益で発動
                'trailing_distance': 0.01,   # 1%の距離を維持
                'type': 'aggressive'
            }
        elif confidence > 0.6:
            # 標準的な設定
            return {
                'enabled': True,
                'activation_profit': 0.02,   # 2%利益で発動
                'trailing_distance': 0.015,  # 1.5%の距離
                'type': 'balanced'
            }
        else:
            # 保守的な設定
            return {
                'enabled': True,
                'activation_profit': 0.025,  # 2.5%利益で発動
                'trailing_distance': 0.02,   # 2%の距離
                'type': 'conservative'
            }
    
    def _create_partial_exit_plan(self, confidence: float) -> List[Dict]:
        """
        部分決済プラン
        信頼度に応じて最適な決済割合を設定
        """
        if confidence > 0.75:
            # 高信頼度: トレンドに乗る
            return [
                {'level': 1, 'exit_ratio': 0.2, 'reason': '初期利確'},
                {'level': 2, 'exit_ratio': 0.3, 'reason': '利益確保'},
                {'level': 3, 'exit_ratio': 0.3, 'reason': '追加利確'},
                {'level': 4, 'exit_ratio': 0.2, 'reason': 'ムーンショット'}
            ]
        elif confidence > 0.65:
            # 中高信頼度: バランス型
            return [
                {'level': 1, 'exit_ratio': 0.3, 'reason': '早期利確'},
                {'level': 2, 'exit_ratio': 0.4, 'reason': 'メイン利確'},
                {'level': 3, 'exit_ratio': 0.3, 'reason': '残り決済'}
            ]
        else:
            # 中信頼度: 確実性重視
            return [
                {'level': 1, 'exit_ratio': 0.5, 'reason': '半分利確'},
                {'level': 2, 'exit_ratio': 0.3, 'reason': '追加利確'},
                {'level': 3, 'exit_ratio': 0.2, 'reason': '最終決済'}
            ]
    
    def manage_position(self, position: Dict, current_market: Dict) -> Dict:
        """
        ポジション管理の推奨アクション
        """
        symbol = position['symbol']
        entry_price = position['entry_price']
        current_price = current_market['price']
        
        # 損益率を計算
        pnl_ratio = (current_price / entry_price - 1) * 100
        
        recommendations = []
        
        # 利益が出ている場合
        if pnl_ratio > 0:
            # トレーリングストップの更新
            if pnl_ratio > 2:
                recommendations.append({
                    'action': 'update_trailing',
                    'new_stop': current_price * 0.98,
                    'reason': '利益保護'
                })
            
            # 部分利確の判定
            exit_plan = position.get('partial_exit_plan', [])
            for plan in exit_plan:
                if pnl_ratio > plan['level'] * 1.5 and not plan.get('executed'):
                    recommendations.append({
                        'action': 'partial_exit',
                        'ratio': plan['exit_ratio'],
                        'reason': plan['reason']
                    })
        
        # 損失が出ている場合
        elif pnl_ratio < -1:
            # 損切りラインの見直し
            if current_market.get('support_nearby'):
                recommendations.append({
                    'action': 'hold',
                    'reason': 'サポート付近'
                })
            elif pnl_ratio < -2:
                recommendations.append({
                    'action': 'consider_exit',
                    'reason': '損失拡大リスク'
                })
        
        return {
            'symbol': symbol,
            'pnl_ratio': pnl_ratio,
            'recommendations': recommendations,
            'health_score': self._calculate_position_health(position, current_market)
        }
    
    def _calculate_position_health(self, position: Dict, market: Dict) -> float:
        """
        ポジションの健全性スコア（0-100）
        """
        score = 50  # ベーススコア
        
        pnl_ratio = (market['price'] / position['entry_price'] - 1) * 100
        
        # 利益によるスコア
        if pnl_ratio > 0:
            score += min(pnl_ratio * 5, 30)  # 最大+30
        else:
            score += max(pnl_ratio * 3, -30)  # 最大-30
        
        # トレンド方向
        if market.get('trend_aligned', True):
            score += 10
        else:
            score -= 10
        
        # ボリューム
        if market.get('volume_increasing', False):
            score += 10
        
        return max(0, min(100, score))