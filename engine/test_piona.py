# test_piona.py — PIONA_CREON 완전체 테스트 (2025-11-22 최종)
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "engine"))

from creon_data_fetcher import api
from inflection_engine import ShinInflectionEngine
from pattern_engine import ShinPatternEngine
from support_resistance_engine import VolumeProfileSR
from fibonacci_engine import CreonFibonacci
from compound_signal import PIONA_CompoundSignal

print("="*70)
print("           PIONA_CREON 연구소 가동 시작")
print("="*70)

print("삼성전자 데이터 수집 중... (CREON 안전 요청 1.1초 간격)")
df = api.get_ohlc("005930", days=500)

if df.empty:
    print("데이터 수집 실패 → CREON Plus를 실행하고 로그인하세요!")
    input("엔터 누르고 종료...")
    exit()

print(f"수집 성공 → {len(df)}일 데이터 확보")

print("4대 축 분석 실행 중...")
inf = ShinInflectionEngine().analyze(df)
pat = ShinPatternEngine().run_all_patterns(df)
sr  = VolumeProfileSR().analyze(df)
fib = CreonFibonacci().analyze(df)

final = PIONA_CompoundSignal().generate(inf, pat, sr, fib)

print("\n" + "="*70)
print("             PIONA_CREON 최종 리포트 (삼성전자)")
print("="*70)
print(f"현재가   : {final.get('current_price', 0):,} 원")
print(f"최종 신호 : {final['compound_signal']}")
print(f"신호 강도 : {final['strength']}/999")
print("-"*70)
for line in final['description']:
    print(" → " + line)
print("="*70)

if final['strength'] >= 900:
    print("4축 완성 신호 발생! → ML/Trader 즉시 실행 준비!")
elif final['strength'] >= 700:
    print("강력 매수 신호 → 적극 대응 종목")
else:
    print("현재는 관망 권장")

print("="*70)
input("분석 완료! 엔터 누르면 종료됩니다...")