import sys
import numpy as np
from typing import List, Dict
from datetime import datetime

class CreonFibonacci:
    FIBO_RETRACEMENT = [0.236, 0.382, 0.5, 0.618, 0.786]
    FIBO_EXTENSION = [1.0, 1.272, 1.414, 1.618, 2.0, 2.618]

    def _find_swing_points(self, high: List[float], low: List[float], window: int = 10) -> Dict:
        highs_idx = []
        lows_idx = []
        for i in range(window, len(high) - window):
            if high[i] == max(high[i-window:i+window+1]):
                highs_idx.append((i, high[i]))
            if low[i] == min(low[i-window:i+window+1]):
                lows_idx.append((i, low[i]))
        result = {
            "swing_highs": highs_idx[-5:] if highs_idx else [],
            "swing_lows": lows_idx[-5:] if lows_idx else [],
            "highest": max(highs_idx, key=lambda x: x[1]) if highs_idx else None,
            "lowest": min(lows_idx, key=lambda x: x[1]) if lows_idx else None
        }
        if len(highs_idx) >= 2:
            result["last_high"] = highs_idx[-1]
            result["prev_high"] = highs_idx[-2]
        if len(lows_idx) >= 2:
            result["last_low"] = lows_idx[-1]
            result["prev_low"] = lows_idx[-2]
        return result

    def _calc_retracement_levels(self, high_pt: float, low_pt: float, is_uptrend: bool) -> Dict:
        diff = high_pt - low_pt
        levels = {}
        if is_uptrend:
            for r in self.FIBO_RETRACEMENT:
                levels[f"ret_{r}"] = round(high_pt - diff * r)
        else:
            for r in self.FIBO_RETRACEMENT:
                levels[f"ret_{r}"] = round(low_pt + diff * r)
        return levels

    def _calc_extension_levels(self, high_pt: float, low_pt: float, is_uptrend: bool) -> Dict:
        diff = high_pt - low_pt
        levels = {}
        if is_uptrend:
            for e in self.FIBO_EXTENSION:
                levels[f"ext_{e}"] = round(low_pt + diff * e)
        else:
            for e in self.FIBO_EXTENSION:
                levels[f"ext_{e}"] = round(high_pt - diff * e)
        return levels

    def _determine_trend(self, close: List[float]) -> str:
        if len(close) < 50:
            return "unknown"
        ma20 = np.mean(close[-20:])
        ma50 = np.mean(close[-50:])
        current = close[-1]
        if current > ma20 > ma50:
            return "uptrend"
        elif current < ma20 < ma50:
            return "downtrend"
        else:
            return "sideways"

    def _check_fibo_levels(self, current: float, levels: Dict, tolerance: float = 0.015) -> List[str]:
        near_levels = []
        if current == 0:
            return near_levels
        for name, level in levels.items():
            if level > 0 and abs(current - level) / current < tolerance:
                near_levels.append(f"{name}:{level}")
        return near_levels

    def analyze(self, df) -> Dict:
        high = df['high'].tolist()
        low = df['low'].tolist()
        close = df['close'].tolist()
        current = close[-1]

        swings = self._find_swing_points(high, low)
        trend = self._determine_trend(close)

        result = {
            "timestamp": datetime.now().isoformat(),
            "code": df['code'].iloc[0] if 'code' in df.columns else "UNKNOWN",
            "current_price": current,
            "trend": trend,
            "retracement_levels": {},
            "extension_levels": {},
            "near_levels": [],
            "signal": "HOLD"
        }

        if not swings.get("highest") or not swings.get("lowest"):
            return result

        high_pt = swings["highest"][1]
        low_pt = swings["lowest"][1]
        high_idx = swings["highest"][0]
        low_idx = swings["lowest"][0]

        is_uptrend = low_idx < high_idx

        ret_levels = self._calc_retracement_levels(high_pt, low_pt, is_uptrend)
        ext_levels = self._calc_extension_levels(high_pt, low_pt, is_uptrend)

        result["retracement_levels"] = ret_levels
        result["extension_levels"] = ext_levels
        result["swing_high"] = high_pt
        result["swing_low"] = low_pt
        result["is_uptrend"] = is_uptrend

        near_ret = self._check_fibo_levels(current, ret_levels)
        near_ext = self._check_fibo_levels(current, ext_levels)
        result["near_levels"] = near_ret + near_ext

        if is_uptrend:
            if near_ret:
                if any("0.618" in lvl or "0.5" in lvl for lvl in near_ret):
                    result["signal"] = "FIBO_SUPPORT_STRONG"
                else:
                    result["signal"] = "FIBO_SUPPORT"
            elif current > high_pt:
                if near_ext:
                    result["signal"] = "FIBO_EXTENSION_TARGET"
                else:
                    result["signal"] = "ABOVE_SWING_HIGH"
            elif current < low_pt:
                result["signal"] = "BELOW_SWING_LOW"
        else:
            if near_ret:
                if any("0.618" in lvl or "0.5" in lvl for lvl in near_ret):
                    result["signal"] = "FIBO_RESISTANCE_STRONG"
                else:
                    result["signal"] = "FIBO_RESISTANCE"
            elif current < low_pt:
                if near_ext:
                    result["signal"] = "FIBO_EXTENSION_TARGET"
                else:
                    result["signal"] = "BELOW_SWING_LOW"
            elif current > high_pt:
                result["signal"] = "ABOVE_SWING_HIGH"

        return result

if __name__ == "__main__":
    print("Fibonacci Engine Test - need data", flush=True)