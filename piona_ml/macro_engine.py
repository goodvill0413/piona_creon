"""
거시(Macro) 분석 엔진
- 이동평균선 정배열/역배열 분석
- 추세 강도 분석
- 시장 상태 판단
"""
import pandas as pd
import numpy as np


class MacroEngine:
    """거시 경제 및 시장 추세 분석 엔진"""

    def __init__(self):
        self.name = "Macro Analysis Engine"

    def analyze(self, df):
        """
        거시 분석 실행

        Parameters:
            df: OHLCV 데이터프레임 (최소 300일 권장)

        Returns:
            dict: 거시 분석 결과
        """
        if len(df) < 60:
            return {
                "signal": "INSUFFICIENT_DATA",
                "score": 0,
                "trend": "unknown",
                "reason": "데이터 부족 (최소 60일 필요)"
            }

        # 이동평균선 계산
        ma_dict = self._calculate_moving_averages(df)

        # 정배열/역배열 체크
        alignment = self._check_alignment(ma_dict)

        # 추세 강도 분석
        trend_strength = self._analyze_trend_strength(df, ma_dict)

        # 최종 신호 및 점수
        result = self._generate_signal(alignment, trend_strength, ma_dict)

        return result

    def _calculate_moving_averages(self, df):
        """이동평균선 계산"""
        close = df['close']

        ma_dict = {
            'ma5': close.rolling(5).mean().iloc[-1] if len(df) >= 5 else None,
            'ma20': close.rolling(20).mean().iloc[-1] if len(df) >= 20 else None,
            'ma60': close.rolling(60).mean().iloc[-1] if len(df) >= 60 else None,
            'ma120': close.rolling(120).mean().iloc[-1] if len(df) >= 120 else None,
            'ma200': close.rolling(200).mean().iloc[-1] if len(df) >= 200 else None,
            'ma300': close.rolling(300).mean().iloc[-1] if len(df) >= 300 else None,
            'current': close.iloc[-1]
        }

        return ma_dict

    def _check_alignment(self, ma_dict):
        """정배열/역배열 체크"""
        current = ma_dict['current']

        # 필수 이평선만 체크 (5, 20, 60)
        mas = []
        for key in ['ma5', 'ma20', 'ma60', 'ma120', 'ma200']:
            if ma_dict.get(key) is not None:
                mas.append(ma_dict[key])

        if len(mas) < 3:
            return "neutral"

        # 정배열: 현재가 > MA5 > MA20 > MA60 ...
        is_upward = all(mas[i] > mas[i+1] for i in range(len(mas)-1))
        is_downward = all(mas[i] < mas[i+1] for i in range(len(mas)-1))

        # 현재가와 비교
        above_all = current > mas[0]
        below_all = current < mas[-1]

        if is_upward and above_all:
            return "perfect_upward"  # 완벽한 정배열
        elif is_upward:
            return "upward"  # 정배열
        elif is_downward and below_all:
            return "perfect_downward"  # 완벽한 역배열
        elif is_downward:
            return "downward"  # 역배열
        else:
            return "neutral"  # 혼조

    def _analyze_trend_strength(self, df, ma_dict):
        """추세 강도 분석"""
        close = df['close']

        # 최근 20일 수익률
        if len(df) >= 20:
            ret_20 = (close.iloc[-1] / close.iloc[-20] - 1) * 100
        else:
            ret_20 = 0

        # 최근 60일 수익률
        if len(df) >= 60:
            ret_60 = (close.iloc[-1] / close.iloc[-60] - 1) * 100
        else:
            ret_60 = 0

        # MA20 기울기
        if len(df) >= 25 and ma_dict['ma20'] is not None:
            ma20_series = close.rolling(20).mean()
            ma20_slope = (ma20_series.iloc[-1] / ma20_series.iloc[-5] - 1) * 100
        else:
            ma20_slope = 0

        return {
            'ret_20d': ret_20,
            'ret_60d': ret_60,
            'ma20_slope': ma20_slope
        }

    def _generate_signal(self, alignment, trend_strength, ma_dict):
        """최종 신호 생성"""
        score = 0
        signal = "NEUTRAL"
        trend = "sideways"
        reasons = []

        # 1) 정배열/역배열 점수
        if alignment == "perfect_upward":
            score += 8
            signal = "BULL_MARKET"
            trend = "strong_uptrend"
            reasons.append("완벽한 정배열 (+8점)")
        elif alignment == "upward":
            score += 5
            signal = "BULL_MARKET"
            trend = "uptrend"
            reasons.append("정배열 (+5점)")
        elif alignment == "neutral":
            score += 3
            signal = "SIDEWAYS"
            trend = "sideways"
            reasons.append("혼조장 (+3점)")
        elif alignment == "downward":
            score -= 5
            signal = "BEAR_MARKET"
            trend = "downtrend"
            reasons.append("역배열 (-5점)")
        elif alignment == "perfect_downward":
            score -= 10
            signal = "BEAR_MARKET"
            trend = "strong_downtrend"
            reasons.append("완벽한 역배열 (-10점)")

        # 2) 추세 강도 점수
        ret_20 = trend_strength['ret_20d']
        ret_60 = trend_strength['ret_60d']

        if ret_20 > 10:
            score += 3
            reasons.append(f"20일 수익률 강세 {ret_20:.1f}% (+3점)")
        elif ret_20 > 5:
            score += 2
            reasons.append(f"20일 수익률 상승 {ret_20:.1f}% (+2점)")
        elif ret_20 < -10:
            score -= 3
            reasons.append(f"20일 수익률 약세 {ret_20:.1f}% (-3점)")
        elif ret_20 < -5:
            score -= 2
            reasons.append(f"20일 수익률 하락 {ret_20:.1f}% (-2점)")

        # 3) 300일선 규칙
        if ma_dict.get('ma300') is not None:
            if ma_dict['current'] > ma_dict['ma300']:
                reasons.append("300일선 위 (안전)")
            else:
                reasons.append("300일선 아래 (주의)")

        return {
            "signal": signal,
            "score": score,
            "trend": trend,
            "alignment": alignment,
            "trend_strength": trend_strength,
            "ma_values": ma_dict,
            "reasons": reasons
        }
