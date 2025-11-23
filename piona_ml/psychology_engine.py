"""
심리(Psychology) 분석 엔진
- 공포/탐욕 지수 계산
- RSI, Stochastic 기반 과매수/과매도 분석
- 매매 타이밍 추천
"""
import pandas as pd
import numpy as np


class PsychologyEngine:
    """시장 심리 분석 엔진"""

    def __init__(self):
        self.name = "Psychology Analysis Engine"

    def analyze(self, df):
        """
        심리 분석 실행

        Parameters:
            df: OHLCV 데이터프레임

        Returns:
            dict: 심리 분석 결과
        """
        if len(df) < 14:
            return {
                "signal": "INSUFFICIENT_DATA",
                "score": 0,
                "psychology": "unknown",
                "reason": "데이터 부족 (최소 14일 필요)"
            }

        # RSI 계산
        rsi = self._calculate_rsi(df)

        # Stochastic 계산
        stoch = self._calculate_stochastic(df)

        # 공포/탐욕 지수
        fear_greed = self._calculate_fear_greed(rsi, stoch, df)

        # 최종 신호
        result = self._generate_signal(rsi, stoch, fear_greed)

        return result

    def _calculate_rsi(self, df, period=14):
        """RSI (Relative Strength Index) 계산"""
        close = df['close']
        delta = close.diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def _calculate_stochastic(self, df, period=14):
        """Stochastic Oscillator 계산"""
        high = df['high']
        low = df['low']
        close = df['close']

        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()

        stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        stoch_d = stoch_k.rolling(window=3).mean()

        return {
            'k': stoch_k.iloc[-1],
            'd': stoch_d.iloc[-1]
        }

    def _calculate_fear_greed(self, rsi, stoch, df):
        """공포/탐욕 지수 계산 (0~100)"""
        # RSI 기여도
        rsi_score = rsi

        # Stochastic 기여도
        stoch_score = stoch['k']

        # 최근 변동성
        if len(df) >= 20:
            returns = df['close'].pct_change().iloc[-20:]
            volatility = returns.std() * 100
            volatility_score = min(volatility * 2, 20)  # 변동성이 높으면 공포
        else:
            volatility_score = 10

        # 종합 지수 (0~100)
        fear_greed_index = (rsi_score * 0.5 + stoch_score * 0.3 + volatility_score * 0.2)

        return {
            'index': fear_greed_index,
            'volatility': volatility if len(df) >= 20 else 0
        }

    def _generate_signal(self, rsi, stoch, fear_greed):
        """최종 신호 생성"""
        score = 0
        signal = "NEUTRAL"
        psychology = "neutral"
        reasons = []
        trading_style = "swing"  # 기본: 스윙

        fg_index = fear_greed['index']

        # 1) 공포/탐욕 분석
        if fg_index < 20:
            psychology = "extreme_fear"
            score += 5
            trading_style = "long_term"
            reasons.append(f"극단적 공포 지수 {fg_index:.1f} → 장기 매수 유리 (+5점)")
        elif fg_index < 40:
            psychology = "fear"
            score += 3
            trading_style = "swing"
            reasons.append(f"공포 지수 {fg_index:.1f} → 스윙 매수 유리 (+3점)")
        elif fg_index > 80:
            psychology = "extreme_greed"
            score -= 5
            trading_style = "scalp"
            reasons.append(f"극단적 탐욕 지수 {fg_index:.1f} → 단타만 권장 (-5점)")
        elif fg_index > 60:
            psychology = "greed"
            score -= 2
            trading_style = "scalp"
            reasons.append(f"탐욕 지수 {fg_index:.1f} → 단타 유리 (-2점)")
        else:
            psychology = "neutral"
            trading_style = "swing"
            reasons.append(f"중립 지수 {fg_index:.1f} → 스윙 적합 (0점)")

        # 2) RSI 분석
        if rsi < 30:
            score += 8
            signal = "OVERSOLD"
            reasons.append(f"RSI 과매도 {rsi:.1f} → 강력 매수 (+8점)")
        elif rsi < 40:
            score += 3
            reasons.append(f"RSI 매수 구간 {rsi:.1f} (+3점)")
        elif rsi > 70:
            score -= 8
            signal = "OVERBOUGHT"
            reasons.append(f"RSI 과매수 {rsi:.1f} → 매도/관망 (-8점)")
        elif rsi > 60:
            score -= 3
            reasons.append(f"RSI 매도 구간 {rsi:.1f} (-3점)")

        # 3) Stochastic 분석
        stoch_k = stoch['k']
        stoch_d = stoch['d']

        if stoch_k < 20 and stoch_d < 20:
            score += 5
            reasons.append(f"Stochastic 과매도 K:{stoch_k:.1f} D:{stoch_d:.1f} (+5점)")
        elif stoch_k > stoch_d and stoch_k < 50:
            score += 3
            reasons.append(f"Stochastic 골든크로스 K:{stoch_k:.1f} (+3점)")
        elif stoch_k > 80 and stoch_d > 80:
            score -= 5
            reasons.append(f"Stochastic 과매수 K:{stoch_k:.1f} D:{stoch_d:.1f} (-5점)")
        elif stoch_k < stoch_d and stoch_k > 50:
            score -= 3
            reasons.append(f"Stochastic 데드크로스 K:{stoch_k:.1f} (-3점)")

        return {
            "signal": signal if signal != "NEUTRAL" else ("BUY" if score > 5 else "SELL" if score < -5 else "NEUTRAL"),
            "score": score,
            "psychology": psychology,
            "fear_greed_index": fg_index,
            "rsi": rsi,
            "stochastic": stoch,
            "trading_style": trading_style,
            "reasons": reasons
        }
