"""
수급(Supply) 분석 엔진
- 외국인/기관/프로그램 수급 분석
- 순매수 추세 분석
- 수급 강도 평가
"""
import pandas as pd
import numpy as np


class SupplyEngine:
    """수급 분석 엔진"""

    def __init__(self):
        self.name = "Supply Analysis Engine"

    def analyze(self, df):
        """
        수급 분석 실행

        Parameters:
            df: OHLCV + 수급 데이터프레임 (frgn_net_buy, inst_net_buy)

        Returns:
            dict: 수급 분석 결과
        """
        if 'frgn_net_buy' not in df.columns or 'inst_net_buy' not in df.columns:
            return {
                "signal": "NO_SUPPLY_DATA",
                "score": 0,
                "supply_trend": "unknown",
                "reason": "수급 데이터 없음 (지수일 수 있음)"
            }

        if len(df) < 5:
            return {
                "signal": "INSUFFICIENT_DATA",
                "score": 0,
                "supply_trend": "unknown",
                "reason": "데이터 부족 (최소 5일 필요)"
            }

        # 외국인 수급 분석
        frgn_analysis = self._analyze_investor(df, 'frgn_net_buy', '외국인')

        # 기관 수급 분석
        inst_analysis = self._analyze_investor(df, 'inst_net_buy', '기관')

        # 수급 강도 분석
        supply_strength = self._analyze_supply_strength(df)

        # 최종 신호
        result = self._generate_signal(frgn_analysis, inst_analysis, supply_strength)

        return result

    def _analyze_investor(self, df, column, investor_name):
        """투자자별 수급 분석"""
        data = df[column].fillna(0)

        if len(data) < 1:
            return {
                'total': 0,
                'recent_5d': 0,
                'recent_20d': 0,
                'trend': 'none'
            }

        # 최근 수급
        total = data.iloc[-1]
        recent_5d = data.iloc[-5:].sum() if len(data) >= 5 else data.sum()
        recent_20d = data.iloc[-20:].sum() if len(data) >= 20 else data.sum()

        # 추세 판단
        if recent_5d > 0 and recent_20d > 0:
            trend = 'strong_buy'
        elif recent_5d > 0:
            trend = 'buy'
        elif recent_5d < 0 and recent_20d < 0:
            trend = 'strong_sell'
        elif recent_5d < 0:
            trend = 'sell'
        else:
            trend = 'neutral'

        return {
            'investor': investor_name,
            'today': total,
            'recent_5d': recent_5d,
            'recent_20d': recent_20d,
            'trend': trend
        }

    def _analyze_supply_strength(self, df):
        """수급 강도 분석"""
        frgn = df['frgn_net_buy'].fillna(0)
        inst = df['inst_net_buy'].fillna(0)
        volume = df['volume']

        # 최근 5일 수급 비율
        if len(df) >= 5:
            frgn_5d = frgn.iloc[-5:].sum()
            inst_5d = inst.iloc[-5:].sum()
            volume_5d = volume.iloc[-5:].sum()

            frgn_ratio = (frgn_5d / volume_5d * 100) if volume_5d > 0 else 0
            inst_ratio = (inst_5d / volume_5d * 100) if volume_5d > 0 else 0
        else:
            frgn_ratio = 0
            inst_ratio = 0

        return {
            'frgn_ratio': frgn_ratio,
            'inst_ratio': inst_ratio,
            'combined': frgn_ratio + inst_ratio
        }

    def _generate_signal(self, frgn_analysis, inst_analysis, supply_strength):
        """최종 신호 생성"""
        score = 0
        signal = "NEUTRAL"
        supply_trend = "neutral"
        reasons = []

        # 1) 외국인 수급
        frgn_trend = frgn_analysis['trend']
        frgn_5d = frgn_analysis['recent_5d']

        if frgn_trend == 'strong_buy':
            score += 5
            reasons.append(f"외국인 강력 순매수 5일:{frgn_5d:,} (+5점)")
        elif frgn_trend == 'buy':
            score += 3
            reasons.append(f"외국인 순매수 5일:{frgn_5d:,} (+3점)")
        elif frgn_trend == 'strong_sell':
            score -= 5
            reasons.append(f"외국인 강력 순매도 5일:{frgn_5d:,} (-5점)")
        elif frgn_trend == 'sell':
            score -= 3
            reasons.append(f"외국인 순매도 5일:{frgn_5d:,} (-3점)")

        # 2) 기관 수급
        inst_trend = inst_analysis['trend']
        inst_5d = inst_analysis['recent_5d']

        if inst_trend == 'strong_buy':
            score += 5
            reasons.append(f"기관 강력 순매수 5일:{inst_5d:,} (+5점)")
        elif inst_trend == 'buy':
            score += 3
            reasons.append(f"기관 순매수 5일:{inst_5d:,} (+3점)")
        elif inst_trend == 'strong_sell':
            score -= 5
            reasons.append(f"기관 강력 순매도 5일:{inst_5d:,} (-5점)")
        elif inst_trend == 'sell':
            score -= 3
            reasons.append(f"기관 순매도 5일:{inst_5d:,} (-3점)")

        # 3) 수급 강도
        combined = supply_strength['combined']
        if abs(combined) > 10:
            if combined > 0:
                score += 2
                reasons.append(f"외인+기관 강한 순매수 비율 {combined:.1f}% (+2점)")
                supply_trend = "strong_buying"
            else:
                score -= 2
                reasons.append(f"외인+기관 강한 순매도 비율 {combined:.1f}% (-2점)")
                supply_trend = "strong_selling"

        # 최종 신호
        if score >= 8:
            signal = "STRONG_BUY"
            supply_trend = "strong_buying"
        elif score >= 3:
            signal = "BUY"
            supply_trend = "buying"
        elif score <= -8:
            signal = "STRONG_SELL"
            supply_trend = "strong_selling"
        elif score <= -3:
            signal = "SELL"
            supply_trend = "selling"
        else:
            signal = "NEUTRAL"
            supply_trend = "neutral"

        return {
            "signal": signal,
            "score": score,
            "supply_trend": supply_trend,
            "frgn_analysis": frgn_analysis,
            "inst_analysis": inst_analysis,
            "supply_strength": supply_strength,
            "reasons": reasons
        }
