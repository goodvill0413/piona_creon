"""
학습 시스템
- 매매 결과 분석
- 패턴별 승률 업데이트
- 종목별 프로파일 업데이트
- ML 모델 재학습
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime


class LearningSystem:
    """학습 시스템"""

    def __init__(self):
        self.name = "Learning System"
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')

    def update_from_trade(self, trade_result, patterns_used):
        """
        매매 결과로부터 학습

        Parameters:
            trade_result: 매매 결과 딕셔너리
            patterns_used: 사용된 패턴 리스트

        Returns:
            dict: 학습 결과
        """
        code = trade_result['code']
        profit_pct = trade_result['profit_pct']
        is_win = profit_pct > 0

        # 1) 패턴 통계 업데이트
        self._update_pattern_stats(patterns_used, is_win, profit_pct)

        # 2) 종목 프로파일 업데이트
        self._update_stock_profile(code, trade_result)

        # 3) 학습 로그
        learning_log = {
            "timestamp": datetime.now().isoformat(),
            "code": code,
            "profit_pct": profit_pct,
            "is_win": is_win,
            "patterns": patterns_used,
            "updated": True
        }

        return learning_log

    def _update_pattern_stats(self, patterns, is_win, profit_pct):
        """패턴별 통계 업데이트"""
        stats_file = os.path.join(self.model_path, 'pattern_stats.json')

        # 기존 통계 로드
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            except:
                stats = {}
        else:
            stats = {}

        # 각 패턴 업데이트
        for pattern in patterns:
            if pattern not in stats:
                stats[pattern] = {
                    "win_rate": 0.5,
                    "avg_return": 0,
                    "count": 0,
                    "total_wins": 0,
                    "total_return": 0
                }

            # 카운트 증가
            stats[pattern]['count'] += 1

            # 승리 카운트
            if is_win:
                stats[pattern]['total_wins'] += 1

            # 수익률 누적
            stats[pattern]['total_return'] += profit_pct

            # 승률 및 평균 수익률 재계산
            count = stats[pattern]['count']
            stats[pattern]['win_rate'] = stats[pattern]['total_wins'] / count
            stats[pattern]['avg_return'] = stats[pattern]['total_return'] / count

        # 저장
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

    def _update_stock_profile(self, code, trade_result):
        """종목별 프로파일 업데이트"""
        profile_file = os.path.join(self.model_path, 'stock_profile.json')

        # 기존 프로파일 로드
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
            except:
                profiles = {}
        else:
            profiles = {}

        # 종목 프로파일 초기화
        if code not in profiles:
            profiles[code] = {
                "total_trades": 0,
                "total_wins": 0,
                "total_return": 0,
                "max_profit": 0,
                "max_loss": 0,
                "avg_volatility": 3,
                "trading_modes": {}
            }

        profile = profiles[code]
        profit_pct = trade_result['profit_pct']
        trading_mode = trade_result.get('trading_mode', 'swing')

        # 업데이트
        profile['total_trades'] += 1

        if profit_pct > 0:
            profile['total_wins'] += 1

        profile['total_return'] += profit_pct

        # 최대 수익/손실
        if profit_pct > profile['max_profit']:
            profile['max_profit'] = profit_pct

        if profit_pct < profile['max_loss']:
            profile['max_loss'] = profit_pct

        # 매매 모드별 통계
        if trading_mode not in profile['trading_modes']:
            profile['trading_modes'][trading_mode] = {
                "count": 0,
                "wins": 0,
                "avg_return": 0
            }

        mode_stat = profile['trading_modes'][trading_mode]
        mode_stat['count'] += 1
        if profit_pct > 0:
            mode_stat['wins'] += 1
        mode_stat['avg_return'] = (
            (mode_stat['avg_return'] * (mode_stat['count'] - 1) + profit_pct) / mode_stat['count']
        )

        # 저장
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)

    def analyze_performance(self):
        """전체 성과 분석"""
        history_file = os.path.join(self.db_path, 'trading_history.json')

        if not os.path.exists(history_file):
            return {
                "total_trades": 0,
                "win_rate": 0,
                "avg_return": 0,
                "message": "매매 이력 없음"
            }

        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "avg_return": 0,
                "message": "매매 이력 로드 실패"
            }

        if not history:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "avg_return": 0,
                "message": "매매 이력 없음"
            }

        # 통계 계산
        total_trades = len(history)
        wins = [t for t in history if t['profit_pct'] > 0]
        win_rate = len(wins) / total_trades

        profits = [t['profit_pct'] for t in history]
        avg_return = np.mean(profits)
        max_profit = max(profits)
        max_loss = min(profits)

        # 최근 20회 성과
        recent_20 = history[-20:] if len(history) >= 20 else history
        recent_wins = [t for t in recent_20 if t['profit_pct'] > 0]
        recent_win_rate = len(recent_wins) / len(recent_20)
        recent_avg_return = np.mean([t['profit_pct'] for t in recent_20])

        return {
            "total_trades": total_trades,
            "wins": len(wins),
            "losses": total_trades - len(wins),
            "win_rate": round(win_rate * 100, 2),
            "avg_return": round(avg_return, 2),
            "max_profit": round(max_profit, 2),
            "max_loss": round(max_loss, 2),
            "recent_20_win_rate": round(recent_win_rate * 100, 2),
            "recent_20_avg_return": round(recent_avg_return, 2)
        }

    def get_best_patterns(self, top_n=5):
        """최고 성과 패턴 조회"""
        stats_file = os.path.join(self.model_path, 'pattern_stats.json')

        if not os.path.exists(stats_file):
            return []

        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        except:
            return []

        # 승률 및 수익률 기준 정렬
        patterns = []
        for pattern, data in stats.items():
            if data['count'] >= 5:  # 최소 5회 이상 거래
                score = data['win_rate'] * 0.6 + (data['avg_return'] / 100) * 0.4
                patterns.append({
                    "pattern": pattern,
                    "win_rate": round(data['win_rate'] * 100, 2),
                    "avg_return": round(data['avg_return'], 2),
                    "count": data['count'],
                    "score": round(score, 3)
                })

        # 정렬
        patterns = sorted(patterns, key=lambda x: x['score'], reverse=True)

        return patterns[:top_n]
