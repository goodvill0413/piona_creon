"""
AI 의사결정 엔진
- 과거 매매 데이터 학습
- 패턴별 승률 분석
- 종목별 특성 학습
- 최종 ML 점수 산출
"""
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime


class AIDecisionEngine:
    """AI 의사결정 엔진"""

    def __init__(self):
        self.name = "AI Decision Engine"
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')

        # 디렉토리 생성
        os.makedirs(self.db_path, exist_ok=True)
        os.makedirs(self.model_path, exist_ok=True)

        # 학습 데이터 로드
        self.trading_history = self._load_trading_history()
        self.pattern_stats = self._load_pattern_stats()
        self.stock_profile = self._load_stock_profile()

    def analyze(self, code, creon_signals, ml_signals):
        """
        AI 의사결정 분석

        Parameters:
            code: 종목코드
            creon_signals: PIONA_CREON 4대 엔진 결과
            ml_signals: PIONA_ML 6대 시장분석 결과

        Returns:
            dict: AI 의사결정 결과
        """
        # 1) 과거 승률 분석
        win_rate = self._calculate_win_rate(code)

        # 2) 최근 20회 매매 성과
        recent_performance = self._analyze_recent_performance(code, limit=20)

        # 3) 유사 패턴 분석
        pattern_similarity = self._analyze_pattern_similarity(code, creon_signals)

        # 4) 종목 고유 리스크
        risk_factor = self._calculate_risk_factor(code)

        # 5) ML 점수 계산
        ml_score = self._calculate_ml_score(
            win_rate,
            recent_performance,
            pattern_similarity,
            risk_factor
        )

        # 6) 매매 스타일 추천
        trading_style = self._recommend_trading_style(
            creon_signals,
            ml_signals,
            recent_performance
        )

        return {
            "ml_score": ml_score,
            "win_rate": win_rate,
            "recent_performance": recent_performance,
            "pattern_similarity": pattern_similarity,
            "risk_factor": risk_factor,
            "trading_style": trading_style,
            "recommendation": self._generate_recommendation(ml_score, trading_style)
        }

    def _load_trading_history(self):
        """매매 이력 로드"""
        history_file = os.path.join(self.db_path, 'trading_history.json')

        if not os.path.exists(history_file):
            return []

        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def _load_pattern_stats(self):
        """패턴별 통계 로드"""
        stats_file = os.path.join(self.model_path, 'pattern_stats.json')

        if not os.path.exists(stats_file):
            # 기본 패턴 통계 (초기값)
            return {
                "trinity_complete": {"win_rate": 0.65, "avg_return": 8.5, "count": 0},
                "double_bottom": {"win_rate": 0.60, "avg_return": 7.2, "count": 0},
                "golden_cross": {"win_rate": 0.55, "avg_return": 6.0, "count": 0},
                "support_bounce": {"win_rate": 0.58, "avg_return": 5.5, "count": 0},
                "fibo_support": {"win_rate": 0.62, "avg_return": 7.0, "count": 0}
            }

        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def _load_stock_profile(self):
        """종목별 프로파일 로드"""
        profile_file = os.path.join(self.model_path, 'stock_profile.json')

        if not os.path.exists(profile_file):
            return {}

        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def _calculate_win_rate(self, code):
        """종목별 과거 승률 계산"""
        if not self.trading_history:
            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.5,  # 기본값 50%
                "avg_profit": 0,
                "avg_loss": 0
            }

        # 해당 종목 매매 이력 필터링
        stock_trades = [t for t in self.trading_history if t.get('code') == code]

        if not stock_trades:
            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.5,
                "avg_profit": 0,
                "avg_loss": 0
            }

        wins = [t for t in stock_trades if t.get('profit_pct', 0) > 0]
        losses = [t for t in stock_trades if t.get('profit_pct', 0) <= 0]

        win_rate = len(wins) / len(stock_trades) if stock_trades else 0.5

        avg_profit = np.mean([t['profit_pct'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['profit_pct'] for t in losses]) if losses else 0

        return {
            "total_trades": len(stock_trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": win_rate,
            "avg_profit": avg_profit,
            "avg_loss": avg_loss
        }

    def _analyze_recent_performance(self, code, limit=20):
        """최근 N회 매매 성과 분석"""
        if not self.trading_history:
            return {
                "recent_trades": 0,
                "recent_win_rate": 0.5,
                "recent_avg_return": 0,
                "trend": "neutral"
            }

        # 해당 종목 최근 거래
        stock_trades = [t for t in self.trading_history if t.get('code') == code]
        stock_trades = sorted(stock_trades, key=lambda x: x.get('date', ''), reverse=True)
        recent_trades = stock_trades[:limit]

        if not recent_trades:
            return {
                "recent_trades": 0,
                "recent_win_rate": 0.5,
                "recent_avg_return": 0,
                "trend": "neutral"
            }

        wins = [t for t in recent_trades if t.get('profit_pct', 0) > 0]
        recent_win_rate = len(wins) / len(recent_trades)
        recent_avg_return = np.mean([t.get('profit_pct', 0) for t in recent_trades])

        # 추세 판단
        if recent_win_rate > 0.6 and recent_avg_return > 3:
            trend = "improving"
        elif recent_win_rate < 0.4 or recent_avg_return < -2:
            trend = "declining"
        else:
            trend = "neutral"

        return {
            "recent_trades": len(recent_trades),
            "recent_win_rate": recent_win_rate,
            "recent_avg_return": recent_avg_return,
            "trend": trend
        }

    def _analyze_pattern_similarity(self, code, creon_signals):
        """유사 패턴 분석"""
        # 현재 신호에서 패턴 추출
        patterns_detected = []

        # 변곡 신호
        if creon_signals.get('inflection', {}).get('trinity', {}).get('trinity_count', 0) >= 3:
            patterns_detected.append('trinity_complete')

        # 패턴 신호
        pattern_result = creon_signals.get('pattern', {})
        if pattern_result.get('final_signal') in ['BUY', 'STRONG_BUY']:
            for p in pattern_result.get('detected_patterns', []):
                if p['pattern'] in ['double_bottom', 'triple_bottom', 'inverse_head_shoulders']:
                    patterns_detected.append(p['pattern'])

        # 지지/저항 신호
        sr_result = creon_signals.get('support_resistance', {})
        if sr_result.get('signal') == 'near_support':
            patterns_detected.append('support_bounce')

        # 피보나치 신호
        fibo_result = creon_signals.get('fibonacci', {})
        if 'SUPPORT' in fibo_result.get('signal', ''):
            patterns_detected.append('fibo_support')

        # 패턴별 승률 집계
        if not patterns_detected:
            return {
                "patterns": [],
                "avg_win_rate": 0.5,
                "avg_return": 0,
                "confidence": 0
            }

        pattern_win_rates = []
        pattern_returns = []

        for pattern in patterns_detected:
            stats = self.pattern_stats.get(pattern, {})
            pattern_win_rates.append(stats.get('win_rate', 0.5))
            pattern_returns.append(stats.get('avg_return', 0))

        avg_win_rate = np.mean(pattern_win_rates)
        avg_return = np.mean(pattern_returns)
        confidence = len(patterns_detected) * 10  # 패턴 개수에 비례

        return {
            "patterns": patterns_detected,
            "avg_win_rate": avg_win_rate,
            "avg_return": avg_return,
            "confidence": min(confidence, 50)  # 최대 50점
        }

    def _calculate_risk_factor(self, code):
        """종목 고유 리스크 계산"""
        profile = self.stock_profile.get(code, {})

        # 기본 리스크 점수 (낮을수록 안전)
        risk_score = 50  # 중립

        # 과거 최대 손실률
        max_loss = profile.get('max_loss_pct', -10)
        if max_loss < -20:
            risk_score += 20  # 높은 리스크
        elif max_loss < -10:
            risk_score += 10
        elif max_loss > -5:
            risk_score -= 10  # 낮은 리스크

        # 변동성
        volatility = profile.get('avg_volatility', 3)
        if volatility > 5:
            risk_score += 10
        elif volatility < 2:
            risk_score -= 10

        # 리스크 등급
        if risk_score > 70:
            grade = "high"
        elif risk_score > 50:
            grade = "medium"
        else:
            grade = "low"

        return {
            "risk_score": risk_score,
            "grade": grade,
            "max_loss": max_loss,
            "volatility": volatility
        }

    def _calculate_ml_score(self, win_rate, recent_performance, pattern_similarity, risk_factor):
        """ML 점수 계산"""
        # 가중치
        A = 0.3  # 과거 승률
        B = 0.3  # 패턴 유사도
        C = 0.2  # 최근 성과
        D = 0.2  # 리스크

        # 점수 계산
        score_win_rate = win_rate['win_rate'] * 100 * A
        score_pattern = pattern_similarity['avg_win_rate'] * 100 * B
        score_recent = (recent_performance['recent_win_rate'] * 100) * C

        # 리스크 점수 (낮을수록 좋음, 역산)
        score_risk = (100 - risk_factor['risk_score']) * D

        total_score = score_win_rate + score_pattern + score_recent + score_risk

        return {
            "total": round(total_score, 1),
            "breakdown": {
                "win_rate_score": round(score_win_rate, 1),
                "pattern_score": round(score_pattern, 1),
                "recent_score": round(score_recent, 1),
                "risk_score": round(score_risk, 1)
            }
        }

    def _recommend_trading_style(self, creon_signals, ml_signals, recent_performance):
        """매매 스타일 추천"""
        # 각 분석 결과에서 스타일 추출
        styles = []

        # 심리 분석
        if ml_signals.get('psychology', {}).get('trading_style'):
            styles.append(ml_signals['psychology']['trading_style'])

        # 변동성 분석
        if ml_signals.get('volatility', {}).get('trading_style'):
            styles.append(ml_signals['volatility']['trading_style'])

        # 최근 성과 기반
        if recent_performance['trend'] == 'declining':
            styles.append('scalp')  # 부진하면 단타만

        # 빈도 집계
        if not styles:
            return 'swing'  # 기본값

        style_counts = {}
        for s in styles:
            style_counts[s] = style_counts.get(s, 0) + 1

        # 최다 빈도 스타일
        recommended_style = max(style_counts, key=style_counts.get)

        return recommended_style

    def _generate_recommendation(self, ml_score, trading_style):
        """최종 추천 생성"""
        score = ml_score['total']

        if score >= 60:
            action = "STRONG_BUY"
            reason = "AI 분석 결과 높은 승률 예상"
        elif score >= 50:
            action = "BUY"
            reason = "AI 분석 결과 긍정적"
        elif score >= 40:
            action = "HOLD"
            reason = "AI 분석 결과 중립"
        elif score >= 30:
            action = "CAUTION"
            reason = "AI 분석 결과 부정적"
        else:
            action = "AVOID"
            reason = "AI 분석 결과 높은 리스크"

        return {
            "action": action,
            "trading_style": trading_style,
            "reason": reason
        }
