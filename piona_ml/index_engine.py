"""
지수 방향 분석 엔진
- 코스피/코스닥 지수 방향 분석
- 지수 대비 종목 상대 강도 분석
"""
import pandas as pd
import numpy as np
import os


class IndexEngine:
    """지수 방향 분석 엔진"""

    def __init__(self):
        self.name = "Index Direction Analysis Engine"
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    def analyze(self, code, df):
        """
        지수 방향 분석 실행

        Parameters:
            code: 종목코드
            df: 종목 OHLCV 데이터프레임

        Returns:
            dict: 지수 분석 결과
        """
        # 종목이 코스피인지 코스닥인지 판단
        if code.startswith('U'):
            return {
                "signal": "INDEX_ITSELF",
                "score": 0,
                "index_direction": "none",
                "reason": "지수 자체는 분석 대상 아님"
            }

        # 코스피/코스닥 판단 (간단히 코드로 구분)
        # A로 시작하고 숫자가 000000~099999 -> 코스피
        # A로 시작하고 숫자가 100000~ -> 코스닥
        try:
            code_num = int(code.replace('A', ''))
            if code_num < 100000:
                index_code = 'U001'  # 코스피
                index_name = '코스피'
            else:
                index_code = 'U201'  # 코스닥
                index_name = '코스닥'
        except:
            # 판단 불가 시 기본 코스피
            index_code = 'U001'
            index_name = '코스피'

        # 지수 데이터 로드
        index_df = self._load_index_data(index_code)

        if index_df is None:
            return {
                "signal": "NO_INDEX_DATA",
                "score": 0,
                "index_direction": "unknown",
                "reason": f"{index_name} 지수 데이터 없음"
            }

        # 지수 방향 분석
        index_analysis = self._analyze_index_direction(index_df, index_name)

        # 상대 강도 분석
        relative_strength = self._analyze_relative_strength(df, index_df)

        # 최종 신호
        result = self._generate_signal(index_analysis, relative_strength, index_name)

        return result

    def _load_index_data(self, index_code):
        """지수 데이터 로드"""
        file_path = os.path.join(self.data_path, f"{index_code}_100days.pkl")

        if not os.path.exists(file_path):
            return None

        try:
            df = pd.read_pickle(file_path)
            return df
        except:
            return None

    def _analyze_index_direction(self, index_df, index_name):
        """지수 방향 분석"""
        close = index_df['close']

        if len(close) < 20:
            return {
                'direction': 'unknown',
                'strength': 0,
                'ret_5d': 0,
                'ret_20d': 0
            }

        # 수익률 계산
        ret_5d = (close.iloc[-1] / close.iloc[-5] - 1) * 100 if len(close) >= 5 else 0
        ret_20d = (close.iloc[-1] / close.iloc[-20] - 1) * 100 if len(close) >= 20 else 0

        # 방향 판단
        if ret_5d > 2 and ret_20d > 5:
            direction = 'strong_uptrend'
            strength = 10
        elif ret_5d > 1 and ret_20d > 2:
            direction = 'uptrend'
            strength = 5
        elif ret_5d < -2 and ret_20d < -5:
            direction = 'strong_downtrend'
            strength = -10
        elif ret_5d < -1 and ret_20d < -2:
            direction = 'downtrend'
            strength = -5
        else:
            direction = 'sideways'
            strength = 0

        return {
            'direction': direction,
            'strength': strength,
            'ret_5d': ret_5d,
            'ret_20d': ret_20d,
            'index_name': index_name
        }

    def _analyze_relative_strength(self, stock_df, index_df):
        """상대 강도 분석 (종목 vs 지수)"""
        # 최근 20일 수익률 비교
        if len(stock_df) < 20 or len(index_df) < 20:
            return {
                'relative_strength': 0,
                'outperformance': False
            }

        stock_ret = (stock_df['close'].iloc[-1] / stock_df['close'].iloc[-20] - 1) * 100
        index_ret = (index_df['close'].iloc[-1] / index_df['close'].iloc[-20] - 1) * 100

        relative_strength = stock_ret - index_ret
        outperformance = relative_strength > 0

        return {
            'relative_strength': relative_strength,
            'stock_ret': stock_ret,
            'index_ret': index_ret,
            'outperformance': outperformance
        }

    def _generate_signal(self, index_analysis, relative_strength, index_name):
        """최종 신호 생성"""
        score = 0
        signal = "NEUTRAL"
        reasons = []

        direction = index_analysis['direction']
        strength = index_analysis['strength']
        ret_5d = index_analysis['ret_5d']

        # 1) 지수 방향 점수
        if direction == 'strong_uptrend':
            score += 10
            signal = "INDEX_STRONG_UP"
            reasons.append(f"{index_name} 강한 상승 {ret_5d:.1f}% (+10점)")
        elif direction == 'uptrend':
            score += 5
            signal = "INDEX_UP"
            reasons.append(f"{index_name} 상승 {ret_5d:.1f}% (+5점)")
        elif direction == 'strong_downtrend':
            score -= 10
            signal = "INDEX_STRONG_DOWN"
            reasons.append(f"{index_name} 강한 하락 {ret_5d:.1f}% (-10점)")
        elif direction == 'downtrend':
            score -= 5
            signal = "INDEX_DOWN"
            reasons.append(f"{index_name} 하락 {ret_5d:.1f}% (-5점)")
        else:
            signal = "INDEX_SIDEWAYS"
            reasons.append(f"{index_name} 횡보 {ret_5d:.1f}% (0점)")

        # 2) 상대 강도
        rs = relative_strength.get('relative_strength', 0)
        if rs > 5:
            score += 3
            reasons.append(f"지수 대비 강세 +{rs:.1f}%p (+3점)")
        elif rs > 2:
            score += 2
            reasons.append(f"지수 대비 우세 +{rs:.1f}%p (+2점)")
        elif rs < -5:
            score -= 3
            reasons.append(f"지수 대비 약세 {rs:.1f}%p (-3점)")
        elif rs < -2:
            score -= 2
            reasons.append(f"지수 대비 열세 {rs:.1f}%p (-2점)")

        return {
            "signal": signal,
            "score": score,
            "index_direction": direction,
            "index_analysis": index_analysis,
            "relative_strength": relative_strength,
            "reasons": reasons
        }
