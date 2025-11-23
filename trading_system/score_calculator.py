"""
통합 점수 계산 시스템
- PIONA_CREON (4대 기술분석) 점수
- PIONA_ML (6대 시장분석) 점수
- AI ML 점수
- 최종 매매 모드 결정
"""
import pandas as pd
import numpy as np


class ScoreCalculator:
    """통합 점수 계산기"""

    def __init__(self):
        self.name = "Integrated Score Calculator"

    def calculate(self, creon_signals, ml_signals, ai_result):
        """
        통합 점수 계산

        Parameters:
            creon_signals: PIONA_CREON 4대 엔진 결과
            ml_signals: PIONA_ML 6대 시장분석 결과
            ai_result: AI 의사결정 결과

        Returns:
            dict: 통합 점수 및 최종 결정
        """
        # 1) PIONA_CREON 점수 (4대 기술분석)
        creon_score = self._calculate_creon_score(creon_signals)

        # 2) PIONA_ML 점수 (6대 시장분석)
        ml_score = self._calculate_ml_score(ml_signals)

        # 3) AI ML 점수
        ai_score = ai_result.get('ml_score', {}).get('total', 0)

        # 4) 총합 점수
        total_score = creon_score['total'] + ml_score['total'] + ai_score

        # 5) 매매 모드 결정
        trading_mode = self._determine_trading_mode(
            creon_signals,
            ml_signals,
            ai_result,
            total_score
        )

        # 6) 최종 신호
        final_signal = self._generate_final_signal(total_score, trading_mode)

        return {
            "creon_score": creon_score,
            "ml_score": ml_score,
            "ai_score": ai_score,
            "total_score": round(total_score, 1),
            "trading_mode": trading_mode,
            "final_signal": final_signal,
            "recommendation": self._generate_recommendation(final_signal, trading_mode)
        }

    def _calculate_creon_score(self, creon_signals):
        """PIONA_CREON 점수 계산 (4대 기술분석)"""
        score = 0
        details = []

        # 1) 변곡 이론 점수
        inflection = creon_signals.get('inflection', {})
        trinity = inflection.get('trinity', {})

        # 삼위일체 완성
        if trinity.get('trinity_count', 0) >= 3:
            score += 30
            details.append("삼위일체 완성 (+30점)")

        # 후행스팬 관통
        if trinity.get('lagging_ok', False):
            score += 10
            details.append("후행스팬 관통 (+10점)")

        # 양운
        if trinity.get('cloud_ok', False):
            score += 5
            details.append("양운 형성 (+5점)")

        # SS2 상승
        if trinity.get('ss2_ok', False):
            score += 5
            details.append("SS2 상승 (+5점)")

        # 대변곡
        if trinity.get('major_inflection_ok', False):
            score += 5
            details.append("51/77 대변곡 (+5점)")

        # 300일선 규칙
        ma300_rule = inflection.get('ma300_rule', {})
        if not ma300_rule.get('above_ma300', True):
            score -= 20
            details.append("300일선 아래 음운 (-20점)")

        # 2) 패턴 분석 점수
        pattern = creon_signals.get('pattern', {})
        final_signal = pattern.get('final_signal', 'NEUTRAL')

        if final_signal == 'STRONG_BUY':
            score += 20
            details.append("강력 매수 패턴 (+20점)")
        elif final_signal == 'BUY':
            score += 10
            details.append("매수 패턴 (+10점)")
        elif final_signal == 'STRONG_SELL':
            score -= 20
            details.append("강력 매도 패턴 (-20점)")
        elif final_signal == 'SELL':
            score -= 10
            details.append("매도 패턴 (-10점)")

        # 3) 지지/저항 점수
        sr = creon_signals.get('support_resistance', {})
        sr_signal = sr.get('signal', 'neutral')

        if sr_signal == 'near_support':
            score += 10
            details.append("강한 지지선 반등 (+10점)")
        elif sr_signal == 'near_resistance':
            score -= 10
            details.append("강한 저항선 아래 (-10점)")
        elif sr_signal == 'uptrend_structure':
            score += 5
            details.append("상승 구조 (+5점)")
        elif sr_signal == 'downtrend_structure':
            score -= 5
            details.append("하락 구조 (-5점)")

        # 4) 피보나치 점수
        fibo = creon_signals.get('fibonacci', {})
        fibo_signal = fibo.get('signal', 'NEUTRAL')

        if 'SUPPORT_STRONG' in fibo_signal:
            score += 8
            details.append("피보나치 0.618 지지 (+8점)")
        elif 'SUPPORT' in fibo_signal:
            score += 5
            details.append("피보나치 되돌림 지지 (+5점)")
        elif 'RESISTANCE' in fibo_signal:
            score -= 5
            details.append("피보나치 저항 (-5점)")

        return {
            "total": score,
            "details": details
        }

    def _calculate_ml_score(self, ml_signals):
        """PIONA_ML 점수 계산 (6대 시장분석)"""
        score = 0
        details = []

        # 1) 거시 분석 점수
        if 'macro' in ml_signals:
            macro = ml_signals['macro']
            macro_score = macro.get('score', 0)
            score += macro_score
            if macro_score != 0:
                details.append(f"거시 분석 ({macro_score:+d}점)")

        # 2) 심리 분석 점수
        if 'psychology' in ml_signals:
            psych = ml_signals['psychology']
            psych_score = psych.get('score', 0)
            score += psych_score
            if psych_score != 0:
                details.append(f"심리 분석 ({psych_score:+d}점)")

        # 3) 수급 분석 점수
        if 'supply' in ml_signals:
            supply = ml_signals['supply']
            supply_score = supply.get('score', 0)
            score += supply_score
            if supply_score != 0:
                details.append(f"수급 분석 ({supply_score:+d}점)")

        # 4) 변동성 분석 점수
        if 'volatility' in ml_signals:
            vol = ml_signals['volatility']
            vol_score = vol.get('score', 0)
            score += vol_score
            if vol_score != 0:
                details.append(f"변동성 분석 ({vol_score:+d}점)")

        # 5) DART 공시 점수
        if 'dart' in ml_signals:
            dart = ml_signals['dart']
            dart_score = dart.get('score', 0)
            score += dart_score
            if dart_score != 0:
                details.append(f"DART 공시 ({dart_score:+d}점)")

        # 6) 지수 방향 점수
        if 'index' in ml_signals:
            index = ml_signals['index']
            index_score = index.get('score', 0)
            score += index_score
            if index_score != 0:
                details.append(f"지수 방향 ({index_score:+d}점)")

        return {
            "total": score,
            "details": details
        }

    def _determine_trading_mode(self, creon_signals, ml_signals, ai_result, total_score):
        """매매 모드 결정 (단타/스윙/장기)"""
        votes = []

        # 1) 심리 분석 의견
        if 'psychology' in ml_signals:
            psych_style = ml_signals['psychology'].get('trading_style', 'swing')
            votes.append(psych_style)

        # 2) 변동성 분석 의견
        if 'volatility' in ml_signals:
            vol_style = ml_signals['volatility'].get('trading_style', 'swing')
            votes.append(vol_style)

        # 3) AI 추천 의견
        ai_style = ai_result.get('trading_style', 'swing')
        votes.append(ai_style)

        # 4) 기술적 신호 기반 의견
        inflection = creon_signals.get('inflection', {})
        trinity_count = inflection.get('trinity', {}).get('trinity_count', 0)

        if trinity_count >= 3:
            votes.append('swing')  # 삼위일체는 스윙 유리
            votes.append('swing')  # 가중치

        ma300_rule = inflection.get('ma300_rule', {})
        if ma300_rule.get('above_ma300', False):
            votes.append('long_term')  # 300일선 위는 장기 유리

        # 5) 수급 신호
        if 'supply' in ml_signals:
            supply_trend = ml_signals['supply'].get('supply_trend', 'neutral')
            if supply_trend in ['strong_buying', 'buying']:
                votes.append('swing')  # 수급 좋으면 스윙
            elif supply_trend in ['strong_selling', 'selling']:
                votes.append('scalp')  # 수급 나쁘면 단타만

        # 6) 지수 방향
        if 'index' in ml_signals:
            index_direction = ml_signals['index'].get('index_direction', 'sideways')
            if 'uptrend' in index_direction:
                votes.append('swing')
            elif 'downtrend' in index_direction:
                votes.append('scalp')

        # 투표 집계
        if not votes:
            return 'swing'  # 기본값

        vote_counts = {
            'scalp': votes.count('scalp'),
            'swing': votes.count('swing'),
            'long_term': votes.count('long_term')
        }

        # 최다 득표
        mode = max(vote_counts, key=vote_counts.get)

        return mode

    def _generate_final_signal(self, total_score, trading_mode):
        """최종 신호 생성"""
        # 점수 기준
        if total_score >= 50:
            action = "STRONG_BUY"
            confidence = "very_high"
        elif total_score >= 30:
            action = "BUY"
            confidence = "high"
        elif total_score >= 10:
            action = "WEAK_BUY"
            confidence = "medium"
        elif total_score >= -10:
            action = "HOLD"
            confidence = "low"
        elif total_score >= -30:
            action = "WEAK_SELL"
            confidence = "low"
        elif total_score >= -50:
            action = "SELL"
            confidence = "medium"
        else:
            action = "STRONG_SELL"
            confidence = "high"

        return {
            "action": action,
            "confidence": confidence,
            "score": total_score
        }

    def _generate_recommendation(self, final_signal, trading_mode):
        """최종 추천 생성"""
        action = final_signal['action']
        confidence = final_signal['confidence']

        # 매매 기간
        if trading_mode == 'scalp':
            period = "1~3일"
            style_desc = "단타"
        elif trading_mode == 'swing':
            period = "5일~4주"
            style_desc = "스윙"
        else:  # long_term
            period = "수주~수개월"
            style_desc = "장기"

        # 추천 메시지
        if action in ['STRONG_BUY', 'BUY']:
            message = f"[매수 추천] {style_desc} 매매 ({period}) - 신뢰도: {confidence}"
        elif action == 'WEAK_BUY':
            message = f"[약한 매수] {style_desc} 매매 ({period}) - 신뢰도: {confidence}"
        elif action == 'HOLD':
            message = f"[관망] 현재 진입 시점 아님 - 신뢰도: {confidence}"
        elif action == 'WEAK_SELL':
            message = f"[약한 매도] 보유 종목 정리 검토 - 신뢰도: {confidence}"
        elif action in ['SELL', 'STRONG_SELL']:
            message = f"[매도 추천] 보유 종목 즉시 정리 - 신뢰도: {confidence}"
        else:
            message = f"[중립] - 신뢰도: {confidence}"

        return {
            "message": message,
            "trading_mode": trading_mode,
            "period": period,
            "action": action,
            "confidence": confidence
        }
