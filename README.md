# PIONA 통합 자동매매 시스템

## 📋 개요

PIONA는 **기술분석 + 시장분석 + AI 의사결정**을 통합한 자동매매 시스템입니다.

### 시스템 구성

```
┌────────────────────────────────────────────────────────┐
│                   PIONA 통합 시스템                      │
├────────────────────────────────────────────────────────┤
│                                                          │
│  [1] PIONA_CREON (4대 기술분석)                          │
│      ├─ 신창환 변곡이론                                   │
│      ├─ 차트 패턴 분석                                    │
│      ├─ 지지·저항 (볼륨 프로파일)                         │
│      └─ 피보나치 분석                                     │
│                                                          │
│  [2] PIONA_ML (6대 시장분석)                             │
│      ├─ 거시(Macro) 분석                                 │
│      ├─ 심리(Psychology) 분석                            │
│      ├─ 수급(Supply) 분석                                │
│      ├─ 변동성(ATR) 분석                                 │
│      ├─ DART 공시 분석                                   │
│      └─ 지수 방향 분석                                    │
│                                                          │
│  [3] AI 의사결정 (ML)                                    │
│      ├─ 과거 승률 학습                                    │
│      ├─ 최근 20회 매매 성과                              │
│      ├─ 유사 패턴 분석                                    │
│      ├─ 종목 고유 리스크                                  │
│      └─ 패턴 조합 실제 수익률                             │
│                                                          │
│  [4] 통합 점수 계산 & 매매 모드 결정                       │
│      └─ 단타 / 스윙 / 장기 자동 선택                       │
│                                                          │
│  [5] 자동매매 실행 & 학습                                 │
│      └─ 매매 결과를 ML에 재반영 (지속 학습)               │
│                                                          │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 빠른 시작

### 1단계: 초기 데이터 수집 (최초 1회)

```bash
python collector_init_100days.py
```

- 202개 종목(코스피 100 + 코스닥 100 + 지수 2) × 100일 데이터 수집
- 소요 시간: 약 5~10분

### 2단계: 자동매매 실행

```bash
python piona_main.py
```

- 유니버스 전체 스캔
- 매수/매도 신호 자동 실행
- 포지션 관리 (손절/익절)
- 매매 결과 학습

### 3단계: 일일 데이터 업데이트 (매일 실행)

```bash
python collector_update_daily.py
```

- 최신 1일 데이터 추가
- Rolling 100일 유지
- 매일 오후 4시 이후 실행 권장

---

## 📂 프로젝트 구조

```
piona_creon/
├── engine/                          # PIONA_CREON (4대 기술분석)
│   ├── inflection_engine.py         # 신창환 변곡이론
│   ├── pattern_engine.py            # 차트 패턴
│   ├── support_resistance_engine.py # 지지/저항
│   └── fibonacci_engine.py          # 피보나치
│
├── piona_ml/                        # PIONA_ML (6대 시장분석)
│   ├── macro_engine.py              # 거시 분석
│   ├── psychology_engine.py         # 심리 분석
│   ├── supply_engine.py             # 수급 분석
│   ├── volatility_engine.py         # 변동성 분석
│   ├── dart_engine.py               # DART 공시
│   ├── index_engine.py              # 지수 방향
│   └── ai_decision_engine.py        # AI 의사결정
│
├── trading_system/                  # 자동매매 시스템
│   ├── score_calculator.py          # 통합 점수 계산
│   ├── auto_trader.py               # 자동매매 실행
│   └── learning_system.py           # 학습 시스템
│
├── database/                        # 데이터베이스
│   ├── trading_history.json         # 매매 이력
│   └── positions.json               # 현재 포지션
│
├── models/                          # ML 모델
│   ├── pattern_stats.json           # 패턴별 통계
│   └── stock_profile.json           # 종목별 프로파일
│
├── data/                            # 종목 데이터
│   └── {종목코드}_100days.pkl
│
├── piona_main.py                    # 통합 메인 스크립트
├── test_system.py                   # 시스템 테스트
└── README.md                        # 이 문서
```

---

## 🎯 핵심 기능

### 1) 4대 기술분석 점수 (PIONA_CREON)

| 항목 | 점수 | 설명 |
|------|------|------|
| 삼위일체 완성 | +30 | 후행스팬 관통 + 양운 + 대변곡 |
| 후행스팬 관통 | +10 | 현재가 > 26일 전 고가 |
| 양운 형성 | +5 | 선행스팬1 > 선행스팬2 |
| SS2 상승 | +5 | 선행스팬2 상승 빗각 |
| 51/77 대변곡 | +5 | 불가항력 변곡 발생 |
| 매수 패턴 | +10~+20 | 더블보텀, 역헤숄더 등 |
| 매도 패턴 | -10~-20 | 더블탑, 헤숄더 등 |
| 강한 지지 반등 | +10 | POC/VAL 근접 |
| 강한 저항 | -10 | VAH 저항 |
| 피보나치 0.618 지지 | +8 | 황금비 되돌림 |

### 2) 6대 시장분석 점수 (PIONA_ML)

| 항목 | 점수 | 설명 |
|------|------|------|
| 완벽한 정배열 | +8 | 현재가 > MA5 > MA20 > MA60 |
| 정배열 | +5 | 이평선 정배열 |
| 역배열 | -10 | 이평선 역배열 |
| RSI 과매도 | +8 | RSI < 30 |
| RSI 과매수 | -8 | RSI > 70 |
| 외인+기관 순매수 | +10 | 5일 순매수 지속 |
| 외인+기관 순매도 | -10 | 5일 순매도 지속 |
| 적정 변동성 | +5 | ATR 1.5~3% (스윙 최적) |
| 지수 강한 상승 | +10 | 코스피/코스닥 5일 +2% 이상 |
| 지수 강한 하락 | -10 | 코스피/코스닥 5일 -2% 이하 |

### 3) AI ML 점수

```python
ml_score = (과거 승률 × 30%) + (패턴 유사도 × 30%) + (최근 성과 × 20%) + (리스크 역산 × 20%)
```

- 매매 결과가 쌓일수록 정확도 향상
- 패턴별 실제 승률 학습
- 종목별 특성 학습

---

## 📊 매매 모드 결정 로직

### 단타 (SCALP) - 1~3일

- 변동성 높음 (ATR > 3%)
- 시장 심리 불안정 (공포/탐욕 지수 극단)
- 수급 급변
- AI 단타 승률 높음

### 스윙 (SWING) - 5일~4주

- 변곡 강함 (삼위일체 2개 이상)
- 적정 변동성 (ATR 1.5~3%)
- 시장 중립~긍정
- AI 스윙 승률 높음

### 장기 (LONG) - 수주~수개월

- 300일선 위 정배열
- 대세 상승
- 변동성 낮음 (ATR < 1.5%)
- AI 장기 승률 높음

---

## 🧪 시스템 테스트

```bash
python test_system.py
```

테스트 항목:
1. 데이터 로딩
2. CREON 4대 엔진
3. ML 6대 엔진
4. AI 의사결정
5. 통합 점수 계산
6. 자동매매 시스템

---

## 💡 사용 예시

### 예시 1: 특정 종목 분석

```python
from piona_main import PIONASystem

piona = PIONASystem(mode='simulation')

# 삼성전자 분석
analysis = piona.analyze_stock('005930')

# 매매 실행
result = piona.execute_trading(analysis)
```

### 예시 2: 전체 유니버스 스캔

```python
# 매수 후보 발굴
buy_candidates = piona.scan_universe()

# 상위 5개 출력
for candidate in buy_candidates[:5]:
    print(f"{candidate['code']}: {candidate['score']}점")
```

### 예시 3: 자동매매 실행

```python
# 스캔 + 매매 + 학습 모두 자동
piona.run_auto_trading()
```

---

## 📈 학습 시스템

### 자동 학습 항목

1. **패턴별 승률**
   - 삼위일체 완성 → 실제 승률 65%
   - 더블보텀 → 실제 승률 60%
   - 피보나치 지지 → 실제 승률 62%

2. **종목별 프로파일**
   - 최대 수익/손실
   - 평균 변동성
   - 매매 모드별 승률

3. **최근 20회 성과**
   - 승률 추세 (상승/하락/중립)
   - 평균 수익률
   - 리스크 점수

### 학습 데이터 저장

- `database/trading_history.json`: 전체 매매 이력
- `models/pattern_stats.json`: 패턴별 통계
- `models/stock_profile.json`: 종목별 프로파일

---

## ⚙️ 설정

### 모의매매 vs 실전매매

```python
# 모의매매 (기본)
piona = PIONASystem(mode='simulation')

# 실전매매 (향후 구현)
piona = PIONASystem(mode='real')
```

### 자금 관리 (향후 구현)

- 종목당 투자 비율
- 손절 비율
- 분할 매수/매도

---

## 📝 주의사항

### 1. Creon 로그인 필수

- 데이터 수집 전 Creon Plus 로그인 필요
- 연결 끊김 시 `크레온연결복구.bat` 실행

### 2. API 제약

- 요청 간격 1.1초 (자동 처리)
- 일일 조회 제한 있음

### 3. 백테스팅 한계

- 과거 데이터 기반 분석
- 미래 수익 보장 불가
- 참고용으로만 활용

### 4. 실전 매매 주의

- 충분한 모의매매 검증 후 실전 진입
- 소액으로 시작
- 손절 규칙 준수

---

## 🔄 일일 운영 루틴

### 매일 오후 4시 이후

```bash
# 1) 최신 데이터 업데이트
python collector_update_daily.py

# 2) 자동매매 실행
python piona_main.py

# 3) 성과 확인
# - database/trading_history.json
# - 콘솔 출력 확인
```

### 주말

- 학습 데이터 백업
- 성과 분석
- 전략 점검

---

## 📊 성과 분석

### 콘솔 출력

```
[성과 분석]
총 거래: 50회
승률: 62.0%
평균 수익률: 3.5%
최근 20회 승률: 65.0%
최근 20회 평균 수익률: 4.2%
```

### 최고 성과 패턴

```python
from trading_system.learning_system import LearningSystem

learning = LearningSystem()
best_patterns = learning.get_best_patterns(top_n=5)

for pattern in best_patterns:
    print(f"{pattern['pattern']}: 승률 {pattern['win_rate']}%")
```

---

## 🛠️ 향후 개선 계획

1. **실전매매 연동**
   - Creon API 매수/매도 주문
   - 체결 확인 및 재시도

2. **웹 대시보드**
   - Flask/Django 기반
   - 실시간 모니터링
   - 성과 차트

3. **알림 기능**
   - 삼위일체 발생 시 카톡/이메일
   - 손절/익절 알림

4. **고도화**
   - 딥러닝 모델 적용
   - 멀티 타임프레임 분석
   - 포트폴리오 최적화

---

## 📞 문의 및 기여

### 면책 조항

- 본 시스템의 분석 결과는 투자 참고 자료일 뿐, 투자 권유가 아닙니다.
- 투자 손실에 대한 책임은 투자자 본인에게 있습니다.
- 실전 투자 전 충분한 검증과 학습을 권장합니다.

---

**작성일**: 2025-11-23
**버전**: 2.0
**시스템명**: PIONA 통합 자동매매 시스템
**구성**: CREON (4대 분석) + ML (6대 분석) + AI (의사결정) + 자동매매 + 학습
