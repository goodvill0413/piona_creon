import sys
import numpy as np
from typing import List, Dict
from collections import defaultdict
from datetime import datetime

class ShinPatternEngine:
    def __init__(self):
        self.pattern_db = defaultdict(list)

    def _find_pivots(self, prices: List[float], window: int = 5) -> Dict:
        highs = []
        lows = []
        for i in range(window, len(prices) - window):
            if prices[i] == max(prices[i-window:i+window+1]):
                highs.append((i, prices[i]))
            if prices[i] == min(prices[i-window:i+window+1]):
                lows.append((i, prices[i]))
        return {"highs": highs, "lows": lows}

    def detect_double_bottom(self, low: List[float], high: List[float], close: List[float]) -> Dict:
        pivots = self._find_pivots(low)
        lows = pivots["lows"]
        if len(lows) < 2:
            return {"detected": False}
        last_two = lows[-2:]
        if last_two[0][1] == 0 or last_two[1][1] == 0:
            return {"detected": False}
        depth_diff = abs(last_two[0][1] - last_two[1][1]) / last_two[0][1]
        neckline = max(high[last_two[0][0]:last_two[1][0]+1]) if last_two[1][0] > last_two[0][0] else high[last_two[0][0]]
        if depth_diff < 0.05 and close[-1] > neckline:
            target = close[-1] + (neckline - min(l[1] for l in last_two)) * 1.5
            return {"detected": True, "pattern": "double_bottom", "confidence": 85, "target": round(target), "signal": "BUY"}
        return {"detected": False}

    def detect_double_top(self, high: List[float], low: List[float], close: List[float]) -> Dict:
        pivots = self._find_pivots(high)
        highs = pivots["highs"]
        if len(highs) < 2:
            return {"detected": False}
        last_two = highs[-2:]
        if last_two[0][1] == 0 or last_two[1][1] == 0:
            return {"detected": False}
        height_diff = abs(last_two[0][1] - last_two[1][1]) / last_two[0][1]
        neckline = min(low[last_two[0][0]:last_two[1][0]+1]) if last_two[1][0] > last_two[0][0] else low[last_two[0][0]]
        if height_diff < 0.05 and close[-1] < neckline:
            return {"detected": True, "pattern": "double_top", "confidence": 85, "signal": "SELL"}
        return {"detected": False}

    def detect_triple_bottom(self, low: List[float], high: List[float], close: List[float]) -> Dict:
        pivots = self._find_pivots(low)
        lows = pivots["lows"]
        if len(lows) < 3:
            return {"detected": False}
        last_three = lows[-3:]
        prices = [l[1] for l in last_three]
        if min(prices) == 0 or any(p == 0 for p in prices):
            return {"detected": False}
        avg = sum(prices) / 3
        if avg > 0 and all(abs(p - avg) / avg < 0.03 for p in prices):
            neckline = max(high[last_three[0][0]:last_three[-1][0]+1])
            if close[-1] > neckline:
                return {"detected": True, "pattern": "triple_bottom", "confidence": 90, "signal": "STRONG_BUY"}
        return {"detected": False}

    def detect_triple_top(self, high: List[float], low: List[float], close: List[float]) -> Dict:
        pivots = self._find_pivots(high)
        highs = pivots["highs"]
        if len(highs) < 3:
            return {"detected": False}
        last_three = highs[-3:]
        prices = [h[1] for h in last_three]
        if min(prices) == 0 or any(p == 0 for p in prices):
            return {"detected": False}
        avg = sum(prices) / 3
        if avg > 0 and all(abs(p - avg) / avg < 0.03 for p in prices):
            neckline = min(low[last_three[0][0]:last_three[-1][0]+1])
            if close[-1] < neckline:
                return {"detected": True, "pattern": "triple_top", "confidence": 90, "signal": "STRONG_SELL"}
        return {"detected": False}

    def detect_head_shoulders(self, high: List[float], low: List[float], close: List[float]) -> Dict:
        pivots = self._find_pivots(high)
        highs = pivots["highs"]
        if len(highs) < 3:
            return {"detected": False}
        last_three = highs[-3:]
        left, head, right = last_three[0][1], last_three[1][1], last_three[2][1]
        if left > 0 and head > left and head > right and abs(left - right) / left < 0.05:
            neckline = min(low[last_three[0][0]:last_three[-1][0]+1])
            if close[-1] < neckline:
                return {"detected": True, "pattern": "head_shoulders", "confidence": 92, "signal": "STRONG_SELL"}
        return {"detected": False}

    def detect_inverse_head_shoulders(self, low: List[float], high: List[float], close: List[float]) -> Dict:
        pivots = self._find_pivots(low)
        lows = pivots["lows"]
        if len(lows) < 3:
            return {"detected": False}
        last_three = lows[-3:]
        left, head, right = last_three[0][1], last_three[1][1], last_three[2][1]
        if left > 0 and head < left and head < right and abs(left - right) / left < 0.05:
            neckline = max(high[last_three[0][0]:last_three[-1][0]+1])
            if close[-1] > neckline:
                return {"detected": True, "pattern": "inverse_head_shoulders", "confidence": 92, "signal": "STRONG_BUY"}
        return {"detected": False}

    def detect_ascending_triangle(self, high: List[float], low: List[float], close: List[float]) -> Dict:
        if len(high) < 20:
            return {"detected": False}
        recent_high = high[-20:]
        recent_low = low[-20:]
        high_std = np.std(recent_high)
        low_trend = np.polyfit(range(20), recent_low, 1)[0]
        if high_std < np.mean(recent_high) * 0.02 and low_trend > 0:
            resistance = np.mean(recent_high)
            if close[-1] > resistance:
                return {"detected": True, "pattern": "ascending_triangle", "confidence": 80, "signal": "BUY"}
        return {"detected": False}

    def detect_descending_triangle(self, high: List[float], low: List[float], close: List[float]) -> Dict:
        if len(high) < 20:
            return {"detected": False}
        recent_high = high[-20:]
        recent_low = low[-20:]
        low_std = np.std(recent_low)
        high_trend = np.polyfit(range(20), recent_high, 1)[0]
        if low_std < np.mean(recent_low) * 0.02 and high_trend < 0:
            support = np.mean(recent_low)
            if close[-1] < support:
                return {"detected": True, "pattern": "descending_triangle", "confidence": 80, "signal": "SELL"}
        return {"detected": False}

    def detect_bullish_engulfing(self, open_p: List[float], close: List[float]) -> Dict:
        if len(close) < 3:
            return {"detected": False}
        prev_open, prev_close = open_p[-2], close[-2]
        curr_open, curr_close = open_p[-1], close[-1]
        if prev_close < prev_open and curr_close > curr_open:
            if curr_open < prev_close and curr_close > prev_open:
                return {"detected": True, "pattern": "bullish_engulfing", "confidence": 75, "signal": "BUY"}
        return {"detected": False}

    def detect_bearish_engulfing(self, open_p: List[float], close: List[float]) -> Dict:
        if len(close) < 3:
            return {"detected": False}
        prev_open, prev_close = open_p[-2], close[-2]
        curr_open, curr_close = open_p[-1], close[-1]
        if prev_close > prev_open and curr_close < curr_open:
            if curr_open > prev_close and curr_close < prev_open:
                return {"detected": True, "pattern": "bearish_engulfing", "confidence": 75, "signal": "SELL"}
        return {"detected": False}

    def detect_morning_star(self, open_p: List[float], close: List[float], high: List[float], low: List[float]) -> Dict:
        if len(close) < 4:
            return {"detected": False}
        day1_bearish = close[-3] < open_p[-3]
        day2_small = abs(close[-2] - open_p[-2]) < (high[-2] - low[-2]) * 0.3
        day3_bullish = close[-1] > open_p[-1]
        day2_gap = open_p[-2] < close[-3]
        day3_recovery = close[-1] > (open_p[-3] + close[-3]) / 2
        if day1_bearish and day2_small and day2_gap and day3_bullish and day3_recovery:
            return {"detected": True, "pattern": "morning_star", "confidence": 82, "signal": "BUY"}
        return {"detected": False}

    def detect_evening_star(self, open_p: List[float], close: List[float], high: List[float], low: List[float]) -> Dict:
        if len(close) < 4:
            return {"detected": False}
        day1_bullish = close[-3] > open_p[-3]
        day2_small = abs(close[-2] - open_p[-2]) < (high[-2] - low[-2]) * 0.3
        day3_bearish = close[-1] < open_p[-1]
        day2_gap = open_p[-2] > close[-3]
        day3_decline = close[-1] < (open_p[-3] + close[-3]) / 2
        if day1_bullish and day2_small and day2_gap and day3_bearish and day3_decline:
            return {"detected": True, "pattern": "evening_star", "confidence": 82, "signal": "SELL"}
        return {"detected": False}

    def detect_hammer(self, open_p: List[float], close: List[float], high: List[float], low: List[float]) -> Dict:
        if len(close) < 2:
            return {"detected": False}
        body = abs(close[-1] - open_p[-1])
        lower_shadow = min(open_p[-1], close[-1]) - low[-1]
        upper_shadow = high[-1] - max(open_p[-1], close[-1])
        if body > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.5:
            return {"detected": True, "pattern": "hammer", "confidence": 70, "signal": "BUY"}
        return {"detected": False}

    def detect_shooting_star(self, open_p: List[float], close: List[float], high: List[float], low: List[float]) -> Dict:
        if len(close) < 2:
            return {"detected": False}
        body = abs(close[-1] - open_p[-1])
        upper_shadow = high[-1] - max(open_p[-1], close[-1])
        lower_shadow = min(open_p[-1], close[-1]) - low[-1]
        if body > 0 and upper_shadow > body * 2 and lower_shadow < body * 0.5:
            return {"detected": True, "pattern": "shooting_star", "confidence": 70, "signal": "SELL"}
        return {"detected": False}

    def detect_doji(self, open_p: List[float], close: List[float], high: List[float], low: List[float]) -> Dict:
        if len(close) < 2:
            return {"detected": False}
        body = abs(close[-1] - open_p[-1])
        total_range = high[-1] - low[-1]
        if total_range > 0 and body < total_range * 0.1:
            return {"detected": True, "pattern": "doji", "confidence": 60, "signal": "REVERSAL_WARNING"}
        return {"detected": False}

    def detect_three_white_soldiers(self, open_p: List[float], close: List[float]) -> Dict:
        if len(close) < 4:
            return {"detected": False}
        bullish1 = close[-3] > open_p[-3]
        bullish2 = close[-2] > open_p[-2]
        bullish3 = close[-1] > open_p[-1]
        higher_closes = close[-1] > close[-2] > close[-3]
        opens_in_body = open_p[-2] > open_p[-3] and open_p[-1] > open_p[-2]
        if bullish1 and bullish2 and bullish3 and higher_closes and opens_in_body:
            return {"detected": True, "pattern": "three_white_soldiers", "confidence": 85, "signal": "STRONG_BUY"}
        return {"detected": False}

    def detect_three_black_crows(self, open_p: List[float], close: List[float]) -> Dict:
        if len(close) < 4:
            return {"detected": False}
        bearish1 = close[-3] < open_p[-3]
        bearish2 = close[-2] < open_p[-2]
        bearish3 = close[-1] < open_p[-1]
        lower_closes = close[-1] < close[-2] < close[-3]
        opens_in_body = open_p[-2] < open_p[-3] and open_p[-1] < open_p[-2]
        if bearish1 and bearish2 and bearish3 and lower_closes and opens_in_body:
            return {"detected": True, "pattern": "three_black_crows", "confidence": 85, "signal": "STRONG_SELL"}
        return {"detected": False}

    def detect_gap_up(self, low: List[float], high: List[float]) -> Dict:
        if len(low) < 2:
            return {"detected": False}
        if low[-1] > high[-2]:
            gap_size = (low[-1] - high[-2]) / high[-2] * 100
            if gap_size > 1:
                return {"detected": True, "pattern": "gap_up", "confidence": 65, "gap_pct": round(gap_size, 2), "signal": "MOMENTUM"}
        return {"detected": False}

    def detect_gap_down(self, low: List[float], high: List[float]) -> Dict:
        if len(low) < 2:
            return {"detected": False}
        if high[-1] < low[-2]:
            gap_size = (low[-2] - high[-1]) / low[-2] * 100
            if gap_size > 1:
                return {"detected": True, "pattern": "gap_down", "confidence": 65, "gap_pct": round(gap_size, 2), "signal": "WEAKNESS"}
        return {"detected": False}

    def detect_volume_spike(self, volume: List[float], close: List[float]) -> Dict:
        if len(volume) < 21:
            return {"detected": False}
        avg_vol = np.mean(volume[-21:-1])
        if avg_vol > 0 and volume[-1] is not None and volume[-1] > avg_vol * 2:
            if close[-2] > 0:
                price_change = (close[-1] - close[-2]) / close[-2] * 100
            else:
                price_change = 0
            signal = "VOLUME_BUY" if price_change > 0 else "VOLUME_SELL"
            return {"detected": True, "pattern": "volume_spike", "confidence": 70, "vol_ratio": round(volume[-1]/avg_vol, 2), "signal": signal}
        return {"detected": False}

    def run_all_patterns(self, df) -> Dict:
        close = df['close'].tolist()
        high = df['high'].tolist()
        low = df['low'].tolist()
        open_p = df['open'].tolist()
        volume = df['volume'].tolist()

        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "code": df['code'].iloc[0] if 'code' in df.columns else "UNKNOWN",
            "detected_patterns": [],
            "buy_signals": 0,
            "sell_signals": 0
        }

        patterns = [
            self.detect_double_bottom(low, high, close),
            self.detect_double_top(high, low, close),
            self.detect_triple_bottom(low, high, close),
            self.detect_triple_top(high, low, close),
            self.detect_head_shoulders(high, low, close),
            self.detect_inverse_head_shoulders(low, high, close),
            self.detect_ascending_triangle(high, low, close),
            self.detect_descending_triangle(high, low, close),
            self.detect_bullish_engulfing(open_p, close),
            self.detect_bearish_engulfing(open_p, close),
            self.detect_morning_star(open_p, close, high, low),
            self.detect_evening_star(open_p, close, high, low),
            self.detect_hammer(open_p, close, high, low),
            self.detect_shooting_star(open_p, close, high, low),
            self.detect_doji(open_p, close, high, low),
            self.detect_three_white_soldiers(open_p, close),
            self.detect_three_black_crows(open_p, close),
            self.detect_gap_up(low, high),
            self.detect_gap_down(low, high),
            self.detect_volume_spike(volume, close),
        ]

        for p in patterns:
            if p.get("detected"):
                results["detected_patterns"].append(p)
                signal = p.get("signal", "")
                if "BUY" in signal:
                    results["buy_signals"] += 1
                elif "SELL" in signal:
                    results["sell_signals"] += 1

        total_conf = sum(p.get("confidence", 0) for p in results["detected_patterns"])
        results["total_confidence"] = total_conf

        if results["buy_signals"] > results["sell_signals"] and total_conf > 150:
            results["final_signal"] = "STRONG_BUY"
        elif results["buy_signals"] > results["sell_signals"]:
            results["final_signal"] = "BUY"
        elif results["sell_signals"] > results["buy_signals"] and total_conf > 150:
            results["final_signal"] = "STRONG_SELL"
        elif results["sell_signals"] > results["buy_signals"]:
            results["final_signal"] = "SELL"
        else:
            results["final_signal"] = "HOLD"

        return results

if __name__ == "__main__":
    print("Pattern Engine Test - need data", flush=True)