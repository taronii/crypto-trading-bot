#!/usr/bin/env python3
"""
Dynamic Exit Matrix - 天才的段階的決済システム
勝率を最大化する革新的な決済戦略
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DynamicExitMatrix:
    """統合的な段階的決済システム"""
    
    def __init__(self):
        self.profit_cascade = ProfitCascadeStrategy()
        self.risk_shield = RiskShieldStrategy()
        self.smart_trail = SmartTrailStrategy()
        self.market_adaptive = MarketAdaptiveExit()
        self.position_tracker = {}
    
    def create_exit_plan(self, entry_price: float, atr: float, 
                        confidence: float, market_conditions: Dict,
                        position_size: float, symbol: str) -> Dict:
        """
        完全な決済プランを作成
        """
        # 1. 段階的利確レベル
        tp_levels = self.profit_cascade.calculate_tp_levels(
            entry_price, atr, confidence, market_conditions
        )
        
        # 2. 段階的損切りレベル
        sl_levels = self.risk_shield.calculate_sl_levels(
            entry_price, atr, position_size
        )
        
        # 3. トレーリング設定
        trailing_config = self.smart_trail.get_initial_config(
            market_conditions.get('volatility', 'normal')
        )
        
        # 4. 市場状況による調整
        adjusted_plan = self.market_adaptive.adjust_all_exits(
            {
                'take_profits': tp_levels,
                'stop_losses': sl_levels,
                'trailing': trailing_config
            },
            market_conditions
        )
        
        # 5. 実行プランの作成
        exit_plan = {
            'symbol': symbol,
            'entry_price': entry_price,
            'position_size': position_size,
            'take_profits': adjusted_plan['take_profits'],
            'stop_losses': adjusted_plan['stop_losses'],
            'trailing_config': adjusted_plan['trailing'],
            'execution_status': {
                'tp_executed': [],
                'sl_executed': [],
                'remaining_size': position_size
            },
            'created_at': datetime.now(),
            'confidence': confidence
        }
        
        return exit_plan

class ProfitCascadeStrategy:
    """利益を最大化する段階的利確戦略"""
    
    def calculate_tp_levels(self, entry_price: float, atr: float, 
                          confidence: float, market_conditions: Dict) -> List[Dict]:
        """
        信頼度と市場状況に基づく5段階利確レベル
        """
        levels = []
        
        # ATRベースの基本倍率
        base_atr_multiples = self._get_atr_multiples(confidence)
        
        # パーセンテージベースの基本値
        base_percentages = self._get_percentage_targets(confidence)
        
        # 決済比率
        exit_ratios = self._get_exit_ratios(confidence)
        
        for i in range(len(base_atr_multiples)):
            # ATRベースとパーセンテージベースの大きい方を採用
            atr_target = entry_price + (atr * base_atr_multiples[i])
            pct_target = entry_price * (1 + base_percentages[i])
            
            target_price = max(atr_target, pct_target)
            
            levels.append({
                'level': i + 1,
                'target_price': target_price,
                'exit_ratio': exit_ratios[i],
                'percentage_gain': ((target_price / entry_price) - 1) * 100,
                'atr_multiple': base_atr_multiples[i],
                'reason': self._get_level_reason(i),
                'executed': False
            })
        
        return levels
    
    def _get_atr_multiples(self, confidence: float) -> List[float]:
        """信頼度に基づくATR倍率"""
        if confidence > 0.8:
            return [0.5, 1.2, 2.0, 3.5, 5.0]  # 高信頼度：広めの間隔
        elif confidence > 0.65:
            return [0.4, 1.0, 1.8, 3.0, 4.0]  # 中高信頼度
        else:
            return [0.3, 0.8, 1.5, 2.5]        # 中信頼度：4段階のみ
    
    def _get_percentage_targets(self, confidence: float) -> List[float]:
        """信頼度に基づくパーセンテージ目標"""
        if confidence > 0.8:
            return [0.005, 0.015, 0.03, 0.05, 0.10]  # 0.5%, 1.5%, 3%, 5%, 10%
        elif confidence > 0.65:
            return [0.005, 0.012, 0.025, 0.04, 0.07]  # より保守的
        else:
            return [0.005, 0.01, 0.02, 0.035]         # 最も保守的
    
    def _get_exit_ratios(self, confidence: float) -> List[float]:
        """信頼度に基づく決済比率"""
        if confidence > 0.8:
            # 高信頼度：後半に重点
            return [0.20, 0.20, 0.25, 0.25, 0.10]
        elif confidence > 0.65:
            # 中高信頼度：バランス型
            return [0.25, 0.25, 0.20, 0.20, 0.10]
        else:
            # 中信頼度：前半に重点
            return [0.30, 0.30, 0.25, 0.15]
    
    def _get_level_reason(self, level: int) -> str:
        """各レベルの決済理由"""
        reasons = [
            "心理的安定確保",
            "元本回収",
            "利益確定",
            "トレンド利益",
            "ムーンショット"
        ]
        return reasons[level] if level < len(reasons) else "追加利益"

class RiskShieldStrategy:
    """段階的にリスクを軽減する損切り戦略"""
    
    def calculate_sl_levels(self, entry_price: float, atr: float, 
                          position_size: float) -> List[Dict]:
        """
        3段階の損切りレベルを計算
        """
        levels = []
        
        # 第1警戒線：早期警告（0.5%または0.5×ATR）
        first_trigger = min(
            entry_price * 0.995,  # -0.5%
            entry_price - (atr * 0.5)
        )
        levels.append({
            'level': 1,
            'trigger_price': first_trigger,
            'exit_ratio': 0.25,
            'action': 'reduce',
            'percentage_loss': ((first_trigger / entry_price) - 1) * 100,
            'reason': '早期リスク軽減',
            'executed': False
        })
        
        # 第2防衛線：本格的な防御（1.5%または1.0×ATR）
        second_trigger = min(
            entry_price * 0.985,  # -1.5%
            entry_price - (atr * 1.0)
        )
        levels.append({
            'level': 2,
            'trigger_price': second_trigger,
            'exit_ratio': 0.50,
            'action': 'reduce',
            'percentage_loss': ((second_trigger / entry_price) - 1) * 100,
            'reason': 'トレンド転換の可能性',
            'executed': False
        })
        
        # 最終防衛線：完全撤退（2.0×ATR）
        final_trigger = entry_price - (atr * 2.0)
        levels.append({
            'level': 3,
            'trigger_price': final_trigger,
            'exit_ratio': 0.25,
            'action': 'close_all',
            'percentage_loss': ((final_trigger / entry_price) - 1) * 100,
            'reason': '最大損失回避',
            'executed': False
        })
        
        return levels

class SmartTrailStrategy:
    """利益を守りながら最大化するトレーリング戦略"""
    
    def get_initial_config(self, volatility: str) -> Dict:
        """初期トレーリング設定"""
        configs = {
            'low': {
                'enabled': True,
                'activation_profit': 0.01,    # 1%で発動
                'callback_rate': 0.005,       # 0.5%の押し目
                'step_size': 0.0025,          # 0.25%ごとに更新
                'aggressive_mode': False
            },
            'normal': {
                'enabled': True,
                'activation_profit': 0.015,   # 1.5%で発動
                'callback_rate': 0.008,       # 0.8%の押し目
                'step_size': 0.005,           # 0.5%ごとに更新
                'aggressive_mode': False
            },
            'high': {
                'enabled': True,
                'activation_profit': 0.02,    # 2%で発動
                'callback_rate': 0.012,       # 1.2%の押し目
                'step_size': 0.01,            # 1%ごとに更新
                'aggressive_mode': True       # 積極的モード
            }
        }
        
        return configs.get(volatility, configs['normal'])
    
    def update_trailing_stop(self, current_price: float, entry_price: float,
                           highest_price: float, config: Dict) -> Dict:
        """トレーリングストップの更新"""
        current_profit = (current_price / entry_price) - 1
        
        # 発動チェック
        if current_profit < config['activation_profit']:
            return {'active': False, 'stop_price': None}
        
        # 新しいストップ価格を計算
        if config['aggressive_mode'] and current_profit > 0.05:
            # 5%以上の利益で積極モード
            callback = config['callback_rate'] * 0.5  # コールバック率を半分に
        else:
            callback = config['callback_rate']
        
        new_stop = current_price * (1 - callback)
        
        # ステップサイズごとに更新
        return {
            'active': True,
            'stop_price': new_stop,
            'current_profit': current_profit * 100,
            'callback_percentage': callback * 100
        }

class MarketAdaptiveExit:
    """市場状況に応じた決済調整"""
    
    def adjust_all_exits(self, base_exits: Dict, market_conditions: Dict) -> Dict:
        """すべての決済レベルを市場状況に応じて調整"""
        adjusted = base_exits.copy()
        
        # ボラティリティ調整
        volatility_factor = self._get_volatility_factor(
            market_conditions.get('volatility', 'normal')
        )
        
        # トレンド強度調整
        trend_factor = self._get_trend_factor(
            market_conditions.get('trend_strength', 0.5)
        )
        
        # 時間帯調整
        session_factor = self._get_session_factor(
            market_conditions.get('session', 'other')
        )
        
        # 利確レベルの調整
        for tp in adjusted['take_profits']:
            tp['target_price'] *= (volatility_factor * trend_factor * session_factor)
        
        # 損切りレベルの調整（ボラティリティが高い時は近めに）
        for sl in adjusted['stop_losses']:
            if market_conditions.get('volatility') == 'high':
                sl['trigger_price'] = sl['trigger_price'] * 1.005  # 0.5%近く
        
        # トレーリング設定の調整
        if market_conditions.get('trend_strength', 0) > 0.7:
            adjusted['trailing']['aggressive_mode'] = True
            adjusted['trailing']['callback_rate'] *= 1.2  # より寛容に
        
        return adjusted
    
    def _get_volatility_factor(self, volatility: str) -> float:
        """ボラティリティに基づく調整係数"""
        factors = {
            'low': 0.9,     # 低ボラ：利確を近く
            'normal': 1.0,  # 通常
            'high': 1.2     # 高ボラ：利確を遠く
        }
        return factors.get(volatility, 1.0)
    
    def _get_trend_factor(self, trend_strength: float) -> float:
        """トレンド強度に基づく調整係数"""
        if trend_strength > 0.8:
            return 1.15  # 強トレンド：利確を延長
        elif trend_strength > 0.6:
            return 1.05
        else:
            return 1.0
    
    def _get_session_factor(self, session: str) -> float:
        """取引時間帯に基づく調整係数"""
        factors = {
            'asian': 0.95,           # アジア時間：レンジ傾向
            'london': 1.05,          # ロンドン時間：ブレイクアウト
            'ny': 1.05,              # NY時間：トレンド
            'london_ny_overlap': 1.1  # 重複時間：最高流動性
        }
        return factors.get(session, 1.0)

class PositionManager:
    """ポジションの実行管理"""
    
    def __init__(self, exit_matrix: DynamicExitMatrix):
        self.exit_matrix = exit_matrix
        self.active_positions = {}
    
    def check_exits(self, symbol: str, current_price: float) -> List[Dict]:
        """決済条件のチェックと実行指示"""
        if symbol not in self.active_positions:
            return []
        
        position = self.active_positions[symbol]
        exit_plan = position['exit_plan']
        actions = []
        
        # 利確チェック
        for tp in exit_plan['take_profits']:
            if not tp['executed'] and current_price >= tp['target_price']:
                actions.append({
                    'type': 'take_profit',
                    'level': tp['level'],
                    'exit_ratio': tp['exit_ratio'],
                    'price': current_price,
                    'reason': tp['reason']
                })
                tp['executed'] = True
        
        # 損切りチェック
        for sl in exit_plan['stop_losses']:
            if not sl['executed'] and current_price <= sl['trigger_price']:
                actions.append({
                    'type': 'stop_loss',
                    'level': sl['level'],
                    'exit_ratio': sl['exit_ratio'],
                    'price': current_price,
                    'reason': sl['reason']
                })
                sl['executed'] = True
        
        # トレーリングストップチェック
        if exit_plan['trailing_config']['enabled']:
            trailing = self._check_trailing_stop(position, current_price)
            if trailing:
                actions.append(trailing)
        
        return actions
    
    def _check_trailing_stop(self, position: Dict, current_price: float) -> Optional[Dict]:
        """トレーリングストップのチェック"""
        entry_price = position['exit_plan']['entry_price']
        config = position['exit_plan']['trailing_config']
        
        # 最高値の更新
        if 'highest_price' not in position:
            position['highest_price'] = current_price
        else:
            position['highest_price'] = max(position['highest_price'], current_price)
        
        # トレーリング計算
        result = self.exit_matrix.smart_trail.update_trailing_stop(
            current_price, entry_price, position['highest_price'], config
        )
        
        if result['active'] and current_price <= result['stop_price']:
            return {
                'type': 'trailing_stop',
                'exit_ratio': 1.0,  # 全決済
                'price': current_price,
                'reason': f"トレーリングストップ（最高値から{result['callback_percentage']:.1f}%下落）"
            }
        
        return None