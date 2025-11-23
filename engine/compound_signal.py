# engine/fibonacci_engine.py
# CREON 전용 피보나치 엔진 — 신창환 방식 아님
# 자동 스윙 고저점 탐지 → 0.382, 0.618, 1.272, 1.618 실시간 계산

import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime

class CreonFibonacci:
    FIBO_LEVELS = {
        "retracement": [0.236, 0.382, 0.5, 0.618, 0.786],
        "extension": [1.272, 1.618, 2.0, 2.618]
    }

    def _find_swing_points(self, high: List[float], low: List[float], window: int = 10) -> Dict:
        """자동으로 최근 의미있는 고점/저점 탐지"""
        highs_idx = []
        lows_idx = []
        
        for i in range(window, len(high) - window):
            if high[i] == max(high[i-window:i+window+1]):
                highs_idx.append((i, high[i]))
            if low[i] == min(low[i-window:i+window+1]):
                lows_idx.append((i, low[i]))
        
        # 가장 최근 유효 스윙 2개씩만 사용
        recent_high = max(highs_idx[-2:], key=lambda x: x[1]) if len(highs_idx) >= 2 else None
        recent_low = min(lows_idx[-2:], key=lambda x: x[1]) if len(lows_idx) >= 2 else None
        
        return {
            "last_high": recent_high,
            "last_low": recent_low,
            "prev_high": highs_idx[-3] if len(highs_idx) >= 3 else None,
            "prev_low": lows_idx[-3] if len(lows_idx) >= 3 else None
        }

    def analyze(self, df) -> Dict:
        high = df['high'].tolist()
        low = df['low'].tolist()
        close = df['close'].tolist()
        current = close[-1]

        swings = self._find_swing_points(high, low)
        result = {
            "timestamp": datetime.now().isoformat(),
            "current_price": current,
            "retracement": {},
            "extension": {},
            "signal": "HOLD"
        }

        # 상승 추세 가정 (최근 저점 → 고점)
        if swings["last_low"] and swings["last_high"] and swings["last_low"][0] < swings["last_high"][0]:
            low_pt = swings["last_low"][1]
            high_pt = swings["last_high"][1]
            diff = high_pt - low_pt
            
            levels = {}
            for r in self.FIBO_LEVELS["retracement"]:
                level = high_pt - diff * r
                levels[f"{r:.3f}"] = round(level)
                if abs(current - level) / current < 0.015:
                    result["signal"] = f"0.{int(r*1000)} 되돌림 지지 테스트"
            
            for e in self.FIBO_LEVELS["extension"]:
                level = high_pt + diff * (e - 1)
                levels[f"{e:.3f}"] = round(level)
                
            result["retracement"] = levels
            if current > high_pt * 1.01:
                result["signal"] = "확장 구간 진입 (1.272~1.618 목표)"

        return result