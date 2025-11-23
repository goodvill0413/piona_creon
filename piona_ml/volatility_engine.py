"""
변동성(Volatility) 분석 엔진
- ATR (Average True Range) 계산
- 변동성 기반 매매 타이밍 및 스타일 추천
- 손절가/목표가 계산
"""
import pandas as pd
import numpy as np


class VolatilityEngine:
    """변동성 분석 엔진"""

    def __init__(self):
        self.name = "Volatility Analysis Engine"

    def analyze(self, df, period=14):
        """
        변동성 분석 실행

        Parameters:
            df: OHLCV 데이터프레임
            period: ATR 계산 기간 (기본 14일)

        Returns:
            dict: 변동성 분석 결과
        """
        if len(df) < period:
            return {
                "signal": "INSUFFICIENT_DATA",
                "score": 0,
                "volatility_level": "unknown",
                "trading_style": "swing",
                "reason": f"데이터 부족 (최소 {period}일 필요)"
            }

        # ATR 계산
        atr = self._calculate_atr(df, period)

        # 변동성 레벨 분석
        volatility_level = self._analyze_volatility_level(df, atr)

        # 매매 스타일 추천
        trading_style = self._recommend_trading_style(volatility_level)

        # 손절가/목표가 계산
        stop_loss, targets = self._calculate_levels(df, atr)

        # 최종 신호
        result = self._generate_signal(atr, volatility_level, trading_style, stop_loss, targets)

        return result

    def _calculate_atr(self, df, period):
        """ATR (Average True Range) 계산"""
        high = df['high']
        low = df['low']
        close = df['close']

        # True Range 계산
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # ATR = TR의 이동평균
        atr = tr.rolling(window=period).mean()

        return {
            'current': atr.iloc[-1],
            'avg_20d': atr.iloc[-20:].mean() if len(atr) >= 20 else atr.mean(),
            'series': atr
        }

    def _analyze_volatility_level(self, df, atr):
        """변동성 레벨 분석"""
        current_atr = atr['current']
        avg_atr = atr['avg_20d']
        current_price = df['close'].iloc[-1]

        # ATR 비율 (%)
        atr_pct = (current_atr / current_price) * 100

        # 변동성 레벨 분류
        if atr_pct > 5:
            level = "very_high"
        elif atr_pct > 3:
            level = "high"
        elif atr_pct > 1.5:
            level = "normal"
        elif atr_pct > 0.8:
            level = "low"
        else:
            level = "very_low"

        # ATR 추세 (확대/축소)
        if current_atr > avg_atr * 1.2:
            trend = "expanding"
        elif current_atr < avg_atr * 0.8:
            trend = "contracting"
        else:
            trend = "stable"

        return {
            'level': level,
            'atr_pct': atr_pct,
            'trend': trend,
            'current_atr': current_atr,
            'avg_atr': avg_atr
        }

    def _recommend_trading_style(self, volatility_level):
        """변동성 기반 매매 스타일 추천"""
        level = volatility_level['level']

        if level == "very_high":
            return "scalp"  # 단타
        elif level == "high":
            return "scalp"  # 단타
        elif level == "normal":
            return "swing"  # 스윙
        elif level == "low":
            return "swing"  # 스윙
        else:  # very_low
            return "long_term"  # 장기

    def _calculate_levels(self, df, atr):
        """손절가/목표가 계산"""
        current_price = df['close'].iloc[-1]
        current_atr = atr['current']

        # 손절가: 현재가 - 2*ATR
        stop_loss = current_price - (2 * current_atr)

        # 목표가
        targets = {
            'target_1': current_price + (1.5 * current_atr),  # 1차 목표
            'target_2': current_price + (3 * current_atr),    # 2차 목표
            'target_3': current_price + (5 * current_atr)     # 3차 목표
        }

        return stop_loss, targets

    def _generate_signal(self, atr, volatility_level, trading_style, stop_loss, targets):
        """최종 신호 생성"""
        score = 0
        signal = "NEUTRAL"
        reasons = []

        level = volatility_level['level']
        atr_pct = volatility_level['atr_pct']
        trend = volatility_level['trend']

        # 1) 변동성 레벨 점수
        if level == "very_high":
            score = 0  # 중립 (위험하지만 기회도 있음)
            signal = "HIGH_VOLATILITY"
            reasons.append(f"매우 높은 변동성 {atr_pct:.2f}% → 단타 전용 (0점)")
        elif level == "high":
            score = 0
            signal = "HIGH_VOLATILITY"
            reasons.append(f"높은 변동성 {atr_pct:.2f}% → 단타 권장 (0점)")
        elif level == "normal":
            score = 5
            signal = "OPTIMAL_VOLATILITY"
            reasons.append(f"적정 변동성 {atr_pct:.2f}% → 스윙 최적 (+5점)")
        elif level == "low":
            score = 3
            signal = "LOW_VOLATILITY"
            reasons.append(f"낮은 변동성 {atr_pct:.2f}% → 스윙/장기 적합 (+3점)")
        else:  # very_low
            score = 2
            signal = "VERY_LOW_VOLATILITY"
            reasons.append(f"매우 낮은 변동성 {atr_pct:.2f}% → 장기 보유 적합 (+2점)")

        # 2) ATR 추세
        if trend == "expanding":
            reasons.append("변동성 확대 중 → 돌발 변수 주의")
        elif trend == "contracting":
            reasons.append("변동성 축소 중 → 안정적 흐름")
        else:
            reasons.append("변동성 안정적")

        return {
            "signal": signal,
            "score": score,
            "volatility_level": level,
            "trading_style": trading_style,
            "atr": atr,
            "volatility_analysis": volatility_level,
            "stop_loss": stop_loss,
            "targets": targets,
            "reasons": reasons
        }
