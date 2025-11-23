import sys
import numpy as np
from typing import List, Dict
from datetime import datetime

class VolumeProfileSR:
    def __init__(self, price_bins: int = 100):
        self.price_bins = price_bins

    def _build_volume_profile(self, high: List[float], low: List[float], close: List[float], volume: List[float]) -> Dict:
        if not high or not low or min(low) >= max(high):
            return {"poc": 0, "vah": 0, "val": 0}
        prices = np.linspace(min(low), max(high), self.price_bins)
        profile = np.zeros(self.price_bins)
        for h, l, c, v in zip(high, low, close, volume):
            idx_low = max(0, np.searchsorted(prices, l, side='right') - 1)
            idx_high = min(self.price_bins - 1, np.searchsorted(prices, h, side='right') - 1)
            if idx_low == idx_high:
                profile[idx_low] += v
            else:
                portion = v / max(1, (idx_high - idx_low + 1))
                profile[idx_low:idx_high+1] += portion
        poc_idx = np.argmax(profile)
        poc_price = prices[poc_idx]
        total_vol = profile.sum()
        if total_vol == 0:
            return {"poc": round(poc_price, 2), "vah": round(max(high), 2), "val": round(min(low), 2)}
        sorted_indices = np.argsort(profile)[::-1]
        cumsum = 0
        va_indices = []
        for idx in sorted_indices:
            cumsum += profile[idx]
            va_indices.append(idx)
            if cumsum >= total_vol * 0.7:
                break
        vah_price = prices[max(va_indices)]
        val_price = prices[min(va_indices)]
        return {"poc": round(poc_price, 2), "vah": round(vah_price, 2), "val": round(val_price, 2)}

    def _find_support_resistance(self, high: List[float], low: List[float], close: List[float], window: int = 10) -> Dict:
        supports = []
        resistances = []
        for i in range(window, len(high) - window):
            if low[i] == min(low[i-window:i+window+1]):
                supports.append({"level": low[i], "strength": "pivot", "index": i})
            if high[i] == max(high[i-window:i+window+1]):
                resistances.append({"level": high[i], "strength": "pivot", "index": i})
        return {"supports": supports[-5:], "resistances": resistances[-5:]}

    def _detect_gaps(self, high: List[float], low: List[float]) -> List[Dict]:
        gaps = []
        for i in range(1, len(high)):
            if low[i] > high[i-1]:
                gaps.append({"type": "gap_up", "level": high[i-1], "size": low[i] - high[i-1], "index": i})
            elif high[i] < low[i-1]:
                gaps.append({"type": "gap_down", "level": low[i-1], "size": low[i-1] - high[i], "index": i})
        return gaps[-10:]

    def _calc_atr(self, high: List[float], low: List[float], close: List[float], period: int = 14) -> float:
        if len(high) < period + 1:
            return 0
        tr_list = []
        for i in range(1, len(high)):
            tr = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
            tr_list.append(tr)
        return np.mean(tr_list[-period:])

    def analyze(self, df) -> Dict:
        high = df['high'].tolist()
        low = df['low'].tolist()
        close = df['close'].tolist()
        volume = df['volume'].tolist()
        current_price = close[-1]

        profile = self._build_volume_profile(high, low, close, volume)
        pivots = self._find_support_resistance(high, low, close)
        gaps = self._detect_gaps(high, low)
        atr = self._calc_atr(high, low, close)

        supports = []
        resistances = []

        if profile["poc"] > 0:
            if current_price > profile["poc"]:
                supports.append({"level": profile["poc"], "strength": "POC", "type": "volume"})
            else:
                resistances.append({"level": profile["poc"], "strength": "POC", "type": "volume"})

        if profile["val"] > 0:
            supports.append({"level": profile["val"], "strength": "VAL", "type": "volume"})
        if profile["vah"] > 0:
            resistances.append({"level": profile["vah"], "strength": "VAH", "type": "volume"})

        for s in pivots["supports"]:
            if s["level"] < current_price:
                supports.append({"level": s["level"], "strength": "pivot", "type": "price"})
        for r in pivots["resistances"]:
            if r["level"] > current_price:
                resistances.append({"level": r["level"], "strength": "pivot", "type": "price"})

        for gap in gaps:
            if gap["type"] == "gap_up" and gap["level"] < current_price:
                supports.append({"level": gap["level"], "strength": "gap", "type": "gap"})
            elif gap["type"] == "gap_down" and gap["level"] > current_price:
                resistances.append({"level": gap["level"], "strength": "gap", "type": "gap"})

        supports = sorted(supports, key=lambda x: x["level"], reverse=True)[:5]
        resistances = sorted(resistances, key=lambda x: x["level"])[:5]

        nearest_support = supports[0]["level"] if supports else 0
        nearest_resistance = resistances[0]["level"] if resistances else 0

        if nearest_support > 0:
            support_distance = (current_price - nearest_support) / current_price * 100
        else:
            support_distance = 100

        if nearest_resistance > 0:
            resistance_distance = (nearest_resistance - current_price) / current_price * 100
        else:
            resistance_distance = 100

        if current_price > profile["poc"] and current_price > profile["val"]:
            signal = "uptrend_structure"
        elif current_price < profile["poc"]:
            signal = "downtrend_structure"
        elif support_distance < 2:
            signal = "near_support"
        elif resistance_distance < 2:
            signal = "near_resistance"
        else:
            signal = "neutral"

        return {
            "timestamp": datetime.now().isoformat(),
            "code": df['code'].iloc[0] if 'code' in df.columns else "UNKNOWN",
            "current_price": current_price,
            "poc": profile["poc"],
            "value_area": [profile["val"], profile["vah"]],
            "atr": round(atr, 2),
            "strong_supports": supports,
            "strong_resistances": resistances,
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "support_distance_pct": round(support_distance, 2),
            "resistance_distance_pct": round(resistance_distance, 2),
            "signal": signal
        }

if __name__ == "__main__":
    print("Support/Resistance Engine Test - need data", flush=True)