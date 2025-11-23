"""
PIONA 시스템 테스트 스크립트
- 각 컴포넌트 개별 테스트
- 통합 테스트
"""
import pandas as pd
import numpy as np
import os


def test_data_loading():
    """데이터 로딩 테스트"""
    print("\n[테스트 1] 데이터 로딩")
    print("=" * 60)

    data_path = os.path.join(os.path.dirname(__file__), 'data')

    if not os.path.exists(data_path):
        print("✗ data 폴더가 없습니다.")
        return False

    files = [f for f in os.listdir(data_path) if f.endswith('.pkl')]

    if not files:
        print("✗ PKL 파일이 없습니다.")
        print("  먼저 collector_init_100days.py를 실행하세요.")
        return False

    print(f"✓ {len(files)}개 파일 발견")

    # 샘플 파일 로드
    sample_file = files[0]
    try:
        df = pd.read_pickle(os.path.join(data_path, sample_file))
        print(f"✓ 샘플 파일 로드 성공: {sample_file}")
        print(f"  - 데이터 길이: {len(df)}일")
        print(f"  - 컬럼: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"✗ 파일 로드 실패: {str(e)}")
        return False


def test_creon_engines():
    """PIONA_CREON 4대 엔진 테스트"""
    print("\n[테스트 2] PIONA_CREON 4대 기술분석 엔진")
    print("=" * 60)

    from engine.inflection_engine import InflectionEngine
    from engine.pattern_engine import PatternEngine
    from engine.support_resistance_engine import SupportResistanceEngine
    from engine.fibonacci_engine import FibonacciEngine

    # 더미 데이터 생성
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    df = pd.DataFrame({
        'date': dates,
        'open': np.random.randint(80000, 85000, 100),
        'high': np.random.randint(85000, 90000, 100),
        'low': np.random.randint(75000, 80000, 100),
        'close': np.random.randint(80000, 85000, 100),
        'volume': np.random.randint(10000000, 20000000, 100),
        'amount': np.random.randint(1000000000, 2000000000, 100)
    })

    try:
        inflection = InflectionEngine()
        result = inflection.analyze(df)
        print(f"✓ 변곡이론 엔진: {result['final_signal']}")
    except Exception as e:
        print(f"✗ 변곡이론 엔진 실패: {str(e)}")
        return False

    try:
        pattern = PatternEngine()
        result = pattern.analyze(df)
        print(f"✓ 패턴 엔진: {result['final_signal']}")
    except Exception as e:
        print(f"✗ 패턴 엔진 실패: {str(e)}")
        return False

    try:
        sr = SupportResistanceEngine()
        result = sr.analyze(df)
        print(f"✓ 지지/저항 엔진: {result['signal']}")
    except Exception as e:
        print(f"✗ 지지/저항 엔진 실패: {str(e)}")
        return False

    try:
        fibo = FibonacciEngine()
        result = fibo.analyze(df)
        print(f"✓ 피보나치 엔진: {result['signal']}")
    except Exception as e:
        print(f"✗ 피보나치 엔진 실패: {str(e)}")
        return False

    return True


def test_ml_engines():
    """PIONA_ML 6대 시장분석 엔진 테스트"""
    print("\n[테스트 3] PIONA_ML 6대 시장분석 엔진")
    print("=" * 60)

    from piona_ml.macro_engine import MacroEngine
    from piona_ml.psychology_engine import PsychologyEngine
    from piona_ml.supply_engine import SupplyEngine
    from piona_ml.volatility_engine import VolatilityEngine
    from piona_ml.dart_engine import DartEngine
    from piona_ml.index_engine import IndexEngine

    # 더미 데이터
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    df = pd.DataFrame({
        'date': dates,
        'open': np.random.randint(80000, 85000, 100),
        'high': np.random.randint(85000, 90000, 100),
        'low': np.random.randint(75000, 80000, 100),
        'close': np.random.randint(80000, 85000, 100),
        'volume': np.random.randint(10000000, 20000000, 100),
        'frgn_net_buy': np.random.randint(-100000, 100000, 100),
        'inst_net_buy': np.random.randint(-100000, 100000, 100)
    })

    try:
        macro = MacroEngine()
        result = macro.analyze(df)
        print(f"✓ 거시 엔진: {result['signal']} (점수: {result['score']})")
    except Exception as e:
        print(f"✗ 거시 엔진 실패: {str(e)}")
        return False

    try:
        psych = PsychologyEngine()
        result = psych.analyze(df)
        print(f"✓ 심리 엔진: {result['signal']} (점수: {result['score']})")
    except Exception as e:
        print(f"✗ 심리 엔진 실패: {str(e)}")
        return False

    try:
        supply = SupplyEngine()
        result = supply.analyze(df)
        print(f"✓ 수급 엔진: {result['signal']} (점수: {result['score']})")
    except Exception as e:
        print(f"✗ 수급 엔진 실패: {str(e)}")
        return False

    try:
        vol = VolatilityEngine()
        result = vol.analyze(df)
        print(f"✓ 변동성 엔진: {result['signal']} (점수: {result['score']})")
    except Exception as e:
        print(f"✗ 변동성 엔진 실패: {str(e)}")
        return False

    try:
        dart = DartEngine()
        result = dart.analyze('005930')
        print(f"✓ DART 엔진: {result['signal']}")
    except Exception as e:
        print(f"✗ DART 엔진 실패: {str(e)}")
        return False

    try:
        index = IndexEngine()
        result = index.analyze('005930', df)
        print(f"✓ 지수 엔진: {result['signal']} (점수: {result['score']})")
    except Exception as e:
        print(f"✗ 지수 엔진 실패: {str(e)}")
        return False

    return True


def test_ai_engine():
    """AI 의사결정 엔진 테스트"""
    print("\n[테스트 4] AI 의사결정 엔진")
    print("=" * 60)

    from piona_ml.ai_decision_engine import AIDecisionEngine

    try:
        ai = AIDecisionEngine()
        creon_signals = {}
        ml_signals = {}
        result = ai.analyze('005930', creon_signals, ml_signals)
        print(f"✓ AI 엔진: ML 점수 {result['ml_score']['total']}")
        print(f"  - 승률: {result['win_rate']['win_rate']*100:.1f}%")
        print(f"  - 추천 스타일: {result['trading_style']}")
        return True
    except Exception as e:
        print(f"✗ AI 엔진 실패: {str(e)}")
        return False


def test_score_calculator():
    """통합 점수 계산 테스트"""
    print("\n[테스트 5] 통합 점수 계산")
    print("=" * 60)

    from trading_system.score_calculator import ScoreCalculator

    try:
        calculator = ScoreCalculator()

        # 더미 신호
        creon_signals = {
            'inflection': {'final_signal': 'BUY', 'trinity': {'trinity_count': 2}, 'ma300_rule': {'above_ma300': True}},
            'pattern': {'final_signal': 'BUY'},
            'support_resistance': {'signal': 'uptrend_structure'},
            'fibonacci': {'signal': 'FIBO_SUPPORT'}
        }

        ml_signals = {
            'macro': {'score': 5},
            'psychology': {'score': 3, 'trading_style': 'swing'},
            'supply': {'score': 5},
            'volatility': {'score': 5, 'trading_style': 'swing'},
            'dart': {'score': 0},
            'index': {'score': 5}
        }

        ai_result = {
            'ml_score': {'total': 50},
            'trading_style': 'swing'
        }

        result = calculator.calculate(creon_signals, ml_signals, ai_result)
        print(f"✓ 통합 점수: {result['total_score']}")
        print(f"  - CREON: {result['creon_score']['total']}")
        print(f"  - ML: {result['ml_score']['total']}")
        print(f"  - AI: {result['ai_score']}")
        print(f"  - 매매 모드: {result['trading_mode']}")
        print(f"  - 최종 신호: {result['final_signal']['action']}")
        return True
    except Exception as e:
        print(f"✗ 통합 점수 계산 실패: {str(e)}")
        return False


def test_trading_system():
    """자동매매 시스템 테스트"""
    print("\n[테스트 6] 자동매매 시스템")
    print("=" * 60)

    from trading_system.auto_trader import AutoTrader
    from trading_system.learning_system import LearningSystem

    try:
        trader = AutoTrader(mode='simulation')
        print(f"✓ 자동매매 시스템 초기화 (모드: simulation)")

        learning = LearningSystem()
        print(f"✓ 학습 시스템 초기화")

        performance = learning.analyze_performance()
        print(f"✓ 성과 분석: 총 {performance['total_trades']}회 거래")

        return True
    except Exception as e:
        print(f"✗ 자동매매 시스템 실패: {str(e)}")
        return False


def run_all_tests():
    """전체 테스트 실행"""
    print("\n" + "=" * 60)
    print("PIONA 시스템 통합 테스트")
    print("=" * 60)

    tests = [
        ("데이터 로딩", test_data_loading),
        ("CREON 엔진", test_creon_engines),
        ("ML 엔진", test_ml_engines),
        ("AI 엔진", test_ai_engine),
        ("점수 계산", test_score_calculator),
        ("매매 시스템", test_trading_system)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} 테스트 중 오류: {str(e)}")
            results.append((name, False))

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    for name, result in results:
        status = "✓ 통과" if result else "✗ 실패"
        print(f"{name}: {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\n총 {passed}/{total} 테스트 통과")

    if passed == total:
        print("\n✓ 모든 테스트 통과! 시스템 정상 작동")
    else:
        print("\n✗ 일부 테스트 실패. 오류 확인 필요")


if __name__ == "__main__":
    run_all_tests()
