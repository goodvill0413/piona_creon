"""
PIONA 통합 자동매매 시스템 메인 스크립트

시스템 구성:
1. PIONA_CREON: 4대 기술분석 엔진
2. PIONA_ML: 6대 시장분석 엔진
3. AI 의사결정 엔진
4. 통합 점수 계산 및 매매 모드 결정
5. 자동매매 실행
6. 학습 시스템
"""
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# 엔진 임포트
from engine.inflection_engine import InflectionEngine
from engine.pattern_engine import PatternEngine
from engine.support_resistance_engine import SupportResistanceEngine
from engine.fibonacci_engine import FibonacciEngine

from piona_ml.macro_engine import MacroEngine
from piona_ml.psychology_engine import PsychologyEngine
from piona_ml.supply_engine import SupplyEngine
from piona_ml.volatility_engine import VolatilityEngine
from piona_ml.dart_engine import DartEngine
from piona_ml.index_engine import IndexEngine
from piona_ml.ai_decision_engine import AIDecisionEngine

from trading_system.score_calculator import ScoreCalculator
from trading_system.auto_trader import AutoTrader
from trading_system.learning_system import LearningSystem


class PIONASystem:
    """PIONA 통합 자동매매 시스템"""

    def __init__(self, mode='simulation'):
        """
        Parameters:
            mode: 'simulation' (모의매매) 또는 'real' (실전매매)
        """
        self.mode = mode
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')

        print("=" * 60)
        print("PIONA 통합 자동매매 시스템 초기화 중...")
        print("=" * 60)

        # PIONA_CREON 엔진 (4대 기술분석)
        self.inflection_engine = InflectionEngine()
        self.pattern_engine = PatternEngine()
        self.sr_engine = SupportResistanceEngine()
        self.fibo_engine = FibonacciEngine()

        # PIONA_ML 엔진 (6대 시장분석)
        self.macro_engine = MacroEngine()
        self.psychology_engine = PsychologyEngine()
        self.supply_engine = SupplyEngine()
        self.volatility_engine = VolatilityEngine()
        self.dart_engine = DartEngine()
        self.index_engine = IndexEngine()

        # AI 의사결정
        self.ai_engine = AIDecisionEngine()

        # 통합 점수 계산
        self.score_calculator = ScoreCalculator()

        # 자동매매
        self.trader = AutoTrader(mode=mode)

        # 학습 시스템
        self.learning_system = LearningSystem()

        print(f"✓ 모드: {mode}")
        print(f"✓ PIONA_CREON: 4대 기술분석 엔진 로드")
        print(f"✓ PIONA_ML: 6대 시장분석 엔진 로드")
        print(f"✓ AI 의사결정 엔진 로드")
        print("=" * 60)

    def analyze_stock(self, code):
        """
        종목 분석 실행

        Parameters:
            code: 종목코드

        Returns:
            dict: 전체 분석 결과
        """
        print(f"\n{'='*60}")
        print(f"종목 분석 시작: {code}")
        print(f"{'='*60}")

        # 1) 데이터 로드
        df = self._load_data(code)
        if df is None or len(df) < 60:
            print(f"✗ 데이터 부족: {code}")
            return None

        print(f"✓ 데이터 로드 완료: {len(df)}일")

        # 2) PIONA_CREON 분석 (4대 기술분석)
        print(f"\n[PIONA_CREON] 4대 기술분석 실행 중...")
        creon_signals = self._run_creon_analysis(df)
        print(f"✓ 변곡이론: {creon_signals['inflection']['final_signal']}")
        print(f"✓ 패턴분석: {creon_signals['pattern']['final_signal']}")
        print(f"✓ 지지저항: {creon_signals['support_resistance']['signal']}")
        print(f"✓ 피보나치: {creon_signals['fibonacci']['signal']}")

        # 3) PIONA_ML 분석 (6대 시장분석)
        print(f"\n[PIONA_ML] 6대 시장분석 실행 중...")
        ml_signals = self._run_ml_analysis(code, df)
        print(f"✓ 거시: {ml_signals['macro']['signal']} (점수: {ml_signals['macro']['score']})")
        print(f"✓ 심리: {ml_signals['psychology']['signal']} (점수: {ml_signals['psychology']['score']})")
        print(f"✓ 수급: {ml_signals['supply']['signal']} (점수: {ml_signals['supply']['score']})")
        print(f"✓ 변동성: {ml_signals['volatility']['signal']} (점수: {ml_signals['volatility']['score']})")
        print(f"✓ DART: {ml_signals['dart']['signal']} (점수: {ml_signals['dart']['score']})")
        print(f"✓ 지수: {ml_signals['index']['signal']} (점수: {ml_signals['index']['score']})")

        # 4) AI 의사결정
        print(f"\n[AI] 의사결정 실행 중...")
        ai_result = self.ai_engine.analyze(code, creon_signals, ml_signals)
        print(f"✓ ML 점수: {ai_result['ml_score']['total']}")
        print(f"✓ 승률: {ai_result['win_rate']['win_rate']*100:.1f}%")
        print(f"✓ 추천 스타일: {ai_result['trading_style']}")

        # 5) 통합 점수 계산
        print(f"\n[통합] 최종 점수 계산 중...")
        final_decision = self.score_calculator.calculate(creon_signals, ml_signals, ai_result)
        print(f"✓ CREON 점수: {final_decision['creon_score']['total']}")
        print(f"✓ ML 점수: {final_decision['ml_score']['total']}")
        print(f"✓ AI 점수: {final_decision['ai_score']}")
        print(f"✓ 총합 점수: {final_decision['total_score']}")
        print(f"✓ 매매 모드: {final_decision['trading_mode']}")
        print(f"✓ 최종 신호: {final_decision['final_signal']['action']}")

        return {
            'code': code,
            'df': df,
            'creon_signals': creon_signals,
            'ml_signals': ml_signals,
            'ai_result': ai_result,
            'final_decision': final_decision
        }

    def execute_trading(self, analysis_result):
        """
        매매 실행

        Parameters:
            analysis_result: analyze_stock() 결과

        Returns:
            dict: 실행 결과
        """
        if analysis_result is None:
            return None

        code = analysis_result['code']
        df = analysis_result['df']
        final_decision = analysis_result['final_decision']
        ml_signals = analysis_result['ml_signals']

        # 현재가 및 손절/목표가
        current_price = df['close'].iloc[-1]
        stop_loss = ml_signals['volatility'].get('stop_loss', current_price * 0.95)
        targets = ml_signals['volatility'].get('targets', {})

        stock_info = {
            'current_price': current_price,
            'stop_loss': stop_loss,
            'target_1': targets.get('target_1', current_price * 1.05),
            'target_2': targets.get('target_2', current_price * 1.10)
        }

        print(f"\n{'='*60}")
        print(f"[매매 실행] {code}")
        print(f"{'='*60}")
        print(f"현재가: {current_price:,}")
        print(f"손절가: {stop_loss:,}")
        print(f"목표가1: {stock_info['target_1']:,}")
        print(f"목표가2: {stock_info['target_2']:,}")

        # 매매 실행
        result = self.trader.execute_signal(code, final_decision, stock_info)

        print(f"\n실행 결과: {result['status']}")
        print(f"액션: {result.get('action', 'NONE')}")

        # 매도 완료 시 학습
        if result.get('action') == 'SELL' and result.get('status') == 'SUCCESS':
            self._update_learning(analysis_result, result)

        return result

    def scan_universe(self, codes=None):
        """
        유니버스 전체 스캔

        Parameters:
            codes: 종목 리스트 (None이면 data 폴더에서 자동 로드)

        Returns:
            list: 매수 후보 리스트
        """
        if codes is None:
            codes = self._get_all_codes()

        print(f"\n{'='*60}")
        print(f"유니버스 스캔 시작: {len(codes)}개 종목")
        print(f"{'='*60}")

        buy_candidates = []
        sell_candidates = []

        for i, code in enumerate(codes, 1):
            print(f"\n[{i}/{len(codes)}] {code} 분석 중...")

            try:
                analysis = self.analyze_stock(code)
                if analysis is None:
                    continue

                final_signal = analysis['final_decision']['final_signal']['action']
                total_score = analysis['final_decision']['total_score']

                if final_signal in ['STRONG_BUY', 'BUY']:
                    buy_candidates.append({
                        'code': code,
                        'signal': final_signal,
                        'score': total_score,
                        'analysis': analysis
                    })
                    print(f"✓ 매수 후보 추가: {code} ({final_signal}, 점수: {total_score})")

                elif final_signal in ['STRONG_SELL', 'SELL']:
                    sell_candidates.append({
                        'code': code,
                        'signal': final_signal,
                        'score': total_score
                    })

            except Exception as e:
                print(f"✗ 분석 실패: {code} - {str(e)}")
                continue

        # 점수순 정렬
        buy_candidates = sorted(buy_candidates, key=lambda x: x['score'], reverse=True)

        print(f"\n{'='*60}")
        print(f"스캔 완료")
        print(f"{'='*60}")
        print(f"매수 후보: {len(buy_candidates)}개")
        print(f"매도 후보: {len(sell_candidates)}개")

        return buy_candidates

    def run_auto_trading(self, codes=None):
        """
        자동매매 실행 (스캔 + 매매)

        Parameters:
            codes: 종목 리스트
        """
        print(f"\n{'='*60}")
        print(f"PIONA 자동매매 시작")
        print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # 1) 보유 종목 체크 (손절/익절)
        self._check_positions()

        # 2) 유니버스 스캔
        buy_candidates = self.scan_universe(codes)

        # 3) 상위 후보 매수
        if buy_candidates:
            print(f"\n{'='*60}")
            print(f"매수 실행")
            print(f"{'='*60}")

            for candidate in buy_candidates[:5]:  # 상위 5개만
                code = candidate['code']
                analysis = candidate['analysis']

                print(f"\n[매수] {code} (점수: {candidate['score']})")
                result = self.execute_trading(analysis)

                if result and result.get('status') == 'SUCCESS':
                    print(f"✓ 매수 완료: {code}")

        # 4) 성과 분석
        self._print_performance()

        print(f"\n{'='*60}")
        print(f"자동매매 완료")
        print(f"{'='*60}")

    def _run_creon_analysis(self, df):
        """PIONA_CREON 4대 기술분석 실행"""
        return {
            'inflection': self.inflection_engine.analyze(df),
            'pattern': self.pattern_engine.analyze(df),
            'support_resistance': self.sr_engine.analyze(df),
            'fibonacci': self.fibo_engine.analyze(df)
        }

    def _run_ml_analysis(self, code, df):
        """PIONA_ML 6대 시장분석 실행"""
        return {
            'macro': self.macro_engine.analyze(df),
            'psychology': self.psychology_engine.analyze(df),
            'supply': self.supply_engine.analyze(df),
            'volatility': self.volatility_engine.analyze(df),
            'dart': self.dart_engine.analyze(code),
            'index': self.index_engine.analyze(code, df)
        }

    def _load_data(self, code):
        """데이터 로드"""
        file_path = os.path.join(self.data_path, f"{code}_100days.pkl")

        if not os.path.exists(file_path):
            return None

        try:
            df = pd.read_pickle(file_path)
            return df
        except:
            return None

    def _get_all_codes(self):
        """data 폴더에서 모든 종목코드 추출"""
        if not os.path.exists(self.data_path):
            return []

        files = [f for f in os.listdir(self.data_path) if f.endswith('.pkl')]
        codes = [f.split('_')[0] for f in files]

        # 지수 제외
        codes = [c for c in codes if not c.startswith('U')]

        return codes

    def _check_positions(self):
        """보유 종목 손절/익절 체크"""
        positions = self.trader.get_open_positions()

        if not positions:
            print("보유 종목 없음")
            return

        print(f"\n{'='*60}")
        print(f"보유 종목 체크: {len(positions)}개")
        print(f"{'='*60}")

        for code, position in positions.items():
            df = self._load_data(code)
            if df is None:
                continue

            current_price = df['close'].iloc[-1]
            stock_info = {
                'current_price': current_price
            }

            analysis = self.analyze_stock(code)
            if analysis:
                result = self.execute_trading(analysis)
                print(f"{code}: {result.get('status')} - {result.get('action')}")

    def _update_learning(self, analysis_result, trade_result):
        """학습 시스템 업데이트"""
        creon_signals = analysis_result['creon_signals']

        # 사용된 패턴 추출
        patterns_used = []

        # 변곡
        trinity_count = creon_signals['inflection']['trinity']['trinity_count']
        if trinity_count >= 3:
            patterns_used.append('trinity_complete')

        # 패턴
        for p in creon_signals['pattern'].get('detected_patterns', []):
            patterns_used.append(p['pattern'])

        # 학습
        learning_log = self.learning_system.update_from_trade(trade_result, patterns_used)
        print(f"\n✓ 학습 완료: {learning_log}")

    def _print_performance(self):
        """성과 출력"""
        performance = self.learning_system.analyze_performance()

        print(f"\n{'='*60}")
        print(f"[성과 분석]")
        print(f"{'='*60}")
        print(f"총 거래: {performance.get('total_trades', 0)}회")
        print(f"승률: {performance.get('win_rate', 0)}%")
        print(f"평균 수익률: {performance.get('avg_return', 0)}%")
        print(f"최근 20회 승률: {performance.get('recent_20_win_rate', 0)}%")
        print(f"최근 20회 평균 수익률: {performance.get('recent_20_avg_return', 0)}%")


def main():
    """메인 함수"""
    # PIONA 시스템 초기화
    piona = PIONASystem(mode='simulation')

    # 사용 예시 1: 특정 종목 분석
    # analysis = piona.analyze_stock('005930')
    # result = piona.execute_trading(analysis)

    # 사용 예시 2: 전체 유니버스 스캔
    # buy_candidates = piona.scan_universe()

    # 사용 예시 3: 자동매매 실행
    piona.run_auto_trading()


if __name__ == "__main__":
    main()
