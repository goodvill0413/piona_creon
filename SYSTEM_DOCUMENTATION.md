# PIONA_CREON 시스템 상세 설명서

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [폴더 및 파일 구조](#폴더-및-파일-구조)
4. [핵심 컴포넌트](#핵심-컴포넌트)
5. [데이터 수집 시스템](#데이터-수집-시스템)
6. [분석 엔진 (4대 엔진)](#분석-엔진-4대-엔진)
7. [사용 방법](#사용-방법)
8. [데이터 구조](#데이터-구조)

---

## 프로젝트 개요

### 프로젝트명
**PIONA_CREON** - 주식 기술적 분석 시스템

### 목적
크레온(Creon) API를 통해 한국 주식시장 데이터를 수집하고, 4대 분석 엔진을 활용하여 종합적인 기술적 분석 및 매매 신호를 제공하는 시스템

### 주요 특징
- **200개 종목 + 2개 지수**: KOSPI 100종목 + KOSDAQ 100종목 + 코스피/코스닥 지수
- **4대 분석 엔진**: 신창환 변곡이론, 차트 패턴, 지지/저항, 피보나치 분석
- **실시간 + 백테스팅**: 실시간 데이터 수집 및 저장된 데이터 분석 모두 지원
- **자동화**: 초기 100일 데이터 수집 및 일일 업데이트 자동화

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    PIONA_CREON 시스템                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [1] 데이터 수집 계층 (Data Collection Layer)                 │
│      ├── Creon API 연동 (creon_ohlcv.py, creon_supply.py)   │
│      ├── 통합 데이터 수집기 (data_merger.py)                  │
│      └── 유니버스 관리 (universe.py)                          │
│                          ↓                                    │
│  [2] 데이터 저장 계층 (Data Storage Layer)                    │
│      ├── 초기 100일 수집 (collector_init_100days.py)         │
│      ├── 일일 업데이트 (collector_update_daily.py)            │
│      └── PKL 파일 저장 (data/*.pkl)                          │
│                          ↓                                    │
│  [3] 분석 엔진 계층 (Analysis Engine Layer)                   │
│      ├── 신창환 변곡이론 (inflection_engine.py)               │
│      ├── 차트 패턴 분석 (pattern_engine.py)                   │
│      ├── 지지/저항 분석 (support_resistance_engine.py)        │
│      └── 피보나치 분석 (fibonacci_engine.py)                  │
│                          ↓                                    │
│  [4] 분석 실행 계층 (Analysis Execution Layer)                │
│      ├── 실시간 분석 (analyze_live.py)                        │
│      └── 백데이터 분석 (analyze_backdata.py)                  │
│                          ↓                                    │
│  [5] 결과 출력 계층 (Output Layer)                            │
│      └── 종합 리포트 (매수/매도 신호, 신뢰도, 상세 분석)       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 폴더 및 파일 구조

### 루트 디렉토리 구조

```
piona_creon/
├── engine/                          # 분석 엔진 폴더
│   ├── inflection_engine.py         # [엔진1] 신창환 변곡이론
│   ├── pattern_engine.py            # [엔진2] 차트 패턴 분석
│   ├── support_resistance_engine.py # [엔진3] 지지/저항 분석
│   ├── fibonacci_engine.py          # [엔진4] 피보나치 분석
│   └── compound_signal.py           # (미사용) 복합 신호 처리
│
├── data/                            # 데이터 저장 폴더 (자동 생성)
│   └── {종목코드}_100days.pkl       # 종목별 100일 데이터
│
├── universe.py                      # 유니버스 관리 (200종목 + 지수)
├── creon_ohlcv.py                   # OHLCV 데이터 수집기
├── creon_supply.py                  # 투자자별 매매 데이터 수집기
├── data_merger.py                   # 통합 데이터 수집기 (12컬럼)
│
├── collector_init_100days.py        # 초기 100일 데이터 수집 스크립트
├── collector_update_daily.py        # 일일 업데이트 스크립트
├── get_data_only.py                 # 개별 종목 데이터 수집 (사용자 입력)
│
├── analyze_live.py                  # 실시간 4대 엔진 분석
├── analyze_backdata.py              # 저장된 데이터 분석 (상세 리포트)
│
└── 크레온연결복구.bat                # Creon 연결 복구 배치 파일
```

---

## 핵심 컴포넌트

### 1. **universe.py** - 유니버스 관리자

#### 역할
- 분석 대상 종목 및 지수 목록 관리
- 총 202개: KOSPI 100종목 + KOSDAQ 100종목 + 코스피/코스닥 지수 2개

#### 주요 메서드
```python
UniverseManager()
  ├── get_symbols_only()      # 전체 202개 반환 (지수 포함)
  ├── get_index_only()         # 지수만 반환 ["U001", "U201"]
  └── get_stocks_only()        # 종목만 반환 (200개)
```

#### 지수 코드
- `U001`: 코스피 지수
- `U201`: 코스닥 지수

---

### 2. **creon_ohlcv.py** - OHLCV 데이터 수집기

#### 역할
Creon API를 통해 주가 기본 데이터(시가, 고가, 저가, 종가, 거래량, 거래대금) 수집

#### 데이터 항목 (7개 컬럼)
| 컬럼명 | 설명 | 타입 |
|--------|------|------|
| date | 날짜 | datetime |
| open | 시가 | int |
| high | 고가 | int |
| low | 저가 | int |
| close | 종가 | int |
| volume | 거래량 | int |
| amount | 거래대금 | int |

#### 추가 계산 항목
- **range**: `high - low` (일일 가격 변동폭)
- **gap**: `open - close.shift(1)` (전일 종가 대비 시가 갭)

#### API 제약사항
- **요청 간격**: 1.1초 (Rate Limit)
- **최대 조회일**: 500일 (기본), 최대 1000일

---

### 3. **creon_supply.py** - 투자자별 매매동향 수집기

#### 역할
외국인 및 기관의 순매수/순매도 데이터 수집

#### 데이터 항목 (3개 컬럼)
| 컬럼명 | 설명 | 타입 |
|--------|------|------|
| date | 날짜 | datetime |
| frgn_net_buy | 외국인 순매수량 | int |
| inst_net_buy | 기관 순매수량 | int |

#### 주의사항
- 지수(U001, U201)는 투자자별 데이터가 없음 → `None` 반환

---

### 4. **data_merger.py** - 통합 데이터 수집기 (12컬럼)

#### 역할
OHLCV + 투자자별 데이터를 통합하여 12개 컬럼으로 구성된 완전한 데이터셋 생성

#### 최종 데이터 구조 (12컬럼)

| 순서 | 컬럼명 | 설명 | 출처 |
|------|--------|------|------|
| 1 | date | 날짜 | OHLCV |
| 2 | code | 종목코드 | OHLCV |
| 3 | open | 시가 | OHLCV |
| 4 | high | 고가 | OHLCV |
| 5 | low | 저가 | OHLCV |
| 6 | close | 종가 | OHLCV |
| 7 | volume | 거래량 | OHLCV |
| 8 | amount | 거래대금 | OHLCV |
| 9 | range | 일일변동폭 | OHLCV (계산) |
| 10 | gap | 시가갭 | OHLCV (계산) |
| 11 | frgn_net_buy | 외국인순매수 | Supply |
| 12 | inst_net_buy | 기관순매수 | Supply |

#### 주요 클래스

**CreonOHLCV**
- Creon StockChart API 연동
- 일봉 데이터 수집
- 지수 처리: U로 시작하는 코드는 그대로, 종목은 'A' 접두사 추가

**CreonSupply**
- Creon CpSvr7254 API 연동
- 투자자별 매매동향 수집
- 지수는 스킵

**DataMerger**
- 위 두 클래스 통합
- `get_full_data(code, days)` 메서드로 12컬럼 데이터 반환

---

## 데이터 수집 시스템

### 1. **collector_init_100days.py** - 초기 100일 데이터 수집

#### 역할
유니버스 전체 202종목에 대해 최초 100일 데이터를 수집하여 `data/` 폴더에 저장

#### 실행 흐름
1. `UniverseManager`로부터 202개 종목 리스트 로드
2. 각 종목마다 `DataMerger.get_full_data(code, 100)` 호출
3. 데이터가 이미 존재하고 100일 이상이면 **건너뛰기** (중복 방지)
4. 성공 시 `data/{code}_100days.pkl` 파일로 저장
5. 최종 성공/실패 통계 출력

#### 사용 시점
- 최초 시스템 셋업 시
- 전체 데이터 재수집 필요 시

#### 예상 소요 시간
- 약 5~10분 (202종목 × 1.1초/종목 ≈ 4분 + API 처리 시간)

---

### 2. **collector_update_daily.py** - 일일 업데이트

#### 역할
기존 100일 데이터에 최신 1일 데이터를 추가하여 업데이트 (Rolling 100일 유지)

#### 실행 흐름
1. 각 종목의 `data/{code}_100days.pkl` 파일 로드
2. 최신 2일 데이터를 새로 수집
3. 기존 데이터의 마지막 날짜보다 새로운 데이터만 추가
4. 전체 데이터를 최신 100일만 유지 (`df.tail(100)`)
5. 파일 덮어쓰기

#### 사용 시점
- 매일 장 마감 후 (오후 4시 이후)
- Windows 작업 스케줄러로 자동화 가능

#### 예상 소요 시간
- 약 3~5분 (이미 최신인 종목은 건너뜀)

---

### 3. **get_data_only.py** - 개별 종목 데이터 수집

#### 역할
사용자가 직접 종목코드와 기간을 입력하여 데이터 수집

#### 사용 방법
1. 실행 시 종목코드 입력 (예: `005930,000660`)
2. 수집 기간 입력 (기본 500일, 최대 1000일)
3. `data/{code}_{days}days.pkl` 형태로 저장

#### 활용 사례
- 특정 종목의 장기 데이터(500일~1000일) 수집
- 유니버스 외 종목 분석
- 테스트 및 연구용

---

## 분석 엔진 (4대 엔진)

### 엔진 1: **inflection_engine.py** - 신창환 변곡이론

#### 이론 배경
신창환의 일목균형표 기반 변곡점 이론을 100% 구현

#### 핵심 개념

**1. 변곡수**
```
[9, 13, 26, 33, 42, 51, 65, 77, 88, 100]
```
- **소마디**: 26일
- **중마디**: 51일
- **대마디**: 77일
- **불가항력 변곡**: 51, 77, 88일

**2. 일목균형표 5선**
| 선명 | 계산식 | 의미 |
|------|--------|------|
| 전환선 | 최근 9일 고저 중간값 | 단기 추세 |
| 기준선 | 최근 26일 고저 중간값 | 중기 추세 |
| 선행스팬1 | (전환선+기준선)/2 | 구름 상단/하단 |
| 선행스팬2 | 최근 52일 고저 중간값 | 구름 상단/하단 |
| 후행스팬 | 현재 종가를 26일 전 표기 | 매수 신호 |

**3. 삼위일체 매수 조건**
```
① 후행스팬 관통: 현재 종가 > 26일 전 고가
② 양운 형성: 선행스팬1 > 선행스팬2 (붉은 구름)
③ 51/77일 대변곡 발생
④ SS2 상승 빗각 (추가 조건)
```

**4. 절대 금기 규칙**
```
300일 이평선 아래 + 음운(검은구름)
→ 절대 매수 금지 (99% 손실 위험)
```

#### 분석 결과 구조

```python
{
  "final_signal": "ULTIMATE_BUY",  # 최종 신호
  "confidence": 99.9,               # 신뢰도 (%)

  "ichimoku": {                     # 일목균형표
    "conversion": 82000,
    "base": 80000,
    "lead1": 81000,
    "lead2": 79000,
    "cloud_color": "양운"
  },

  "trinity": {                      # 삼위일체
    "lagging_ok": True,
    "cloud_ok": True,
    "major_inflection_ok": True,
    "ss2_ok": True,
    "trinity_count": 3
  },

  "ma300_rule": {                   # 300일선 규칙
    "ma300": 75000,
    "above_ma300": True,
    "signal": "안전_300선위_양운_매수가능"
  },

  "inflections": [...]              # 변곡일 상세
}
```

#### 신호 종류
- `ULTIMATE_BUY`: 삼위일체 + SS2 상승빗각 → 최강 매수
- `STRONG_BUY`: 삼위일체 완성 → 강력 매수
- `BUY`: 2요소 이상 충족 → 매수
- `ABSOLUTE_NO_BUY`: 절대 금기 → 절대 매수 금지
- `HOLD`: 1요소 충족 → 관망
- `WAIT`: 미충족 → 대기

---

### 엔진 2: **pattern_engine.py** - 차트 패턴 분석

#### 지원 패턴 (20개)

**반전 패턴**
1. Double Bottom (쌍바닥) → BUY
2. Double Top (쌍봉) → SELL
3. Triple Bottom (삼중바닥) → STRONG_BUY
4. Triple Top (삼중천정) → STRONG_SELL
5. Head & Shoulders (헤드앤숄더) → STRONG_SELL
6. Inverse Head & Shoulders (역헤드앤숄더) → STRONG_BUY

**지속 패턴**
7. Ascending Triangle (상승삼각형) → BUY
8. Descending Triangle (하락삼각형) → SELL

**캔들 패턴**
9. Bullish Engulfing (상승장악형) → BUY
10. Bearish Engulfing (하락장악형) → SELL
11. Morning Star (샛별형) → BUY
12. Evening Star (석별형) → SELL
13. Hammer (망치형) → BUY
14. Shooting Star (유성형) → SELL
15. Doji (도지) → REVERSAL_WARNING
16. Three White Soldiers (삼병) → STRONG_BUY
17. Three Black Crows (흑삼병) → STRONG_SELL

**갭/볼륨 패턴**
18. Gap Up (상승갭) → MOMENTUM
19. Gap Down (하락갭) → WEAKNESS
20. Volume Spike (거래량 급증) → VOLUME_BUY/SELL

#### 패턴 감지 알고리즘

**피봇 포인트 탐지**
```python
def _find_pivots(prices, window=5):
    # 좌우 5일 중 최고점 → 저항
    # 좌우 5일 중 최저점 → 지지
```

**더블 보텀 예시**
```python
조건:
  1. 두 개의 저점 발견
  2. 저점 깊이 차이 < 5%
  3. 현재가 > 넥라인 (두 저점 사이 고점)
→ BUY 신호, 목표가 = 넥라인 + (넥라인-저점) × 1.5
```

#### 분석 결과 구조

```python
{
  "detected_patterns": [
    {
      "pattern": "double_bottom",
      "confidence": 85,
      "signal": "BUY",
      "target": 85000
    }
  ],
  "buy_signals": 3,
  "sell_signals": 1,
  "total_confidence": 240,
  "final_signal": "STRONG_BUY"  # buy > sell && conf > 150
}
```

---

### 엔진 3: **support_resistance_engine.py** - 지지/저항 분석

#### 분석 기법

**1. Volume Profile**
- 가격대별 거래량 분포 분석
- **POC** (Point of Control): 최다 거래 가격대
- **Value Area**: 전체 거래량의 70%가 집중된 구간 (VAL ~ VAH)

**2. Pivot Points**
- 좌우 10일 중 최고점/최저점을 저항/지지로 인식

**3. Gap Analysis**
- 갭상승/갭하락 발생 가격대를 저항/지지로 활용

**4. ATR (Average True Range)**
- 14일 평균 진폭 계산
- 손절/목표가 설정에 활용

#### 지지/저항 레벨 분류

| 레벨 | 타입 | 설명 |
|------|------|------|
| POC | volume | 최다 거래 가격대 (강력) |
| VAL/VAH | volume | Value Area 경계 |
| pivot | price | 고점/저점 |
| gap | gap | 미체결 갭 |

#### 분석 결과 구조

```python
{
  "poc": 82000,                    # POC 가격
  "value_area": [79000, 85000],    # Value Area
  "atr": 1500,                     # 평균진폭

  "strong_supports": [             # 주요 지지선
    {"level": 80000, "strength": "POC", "type": "volume"},
    {"level": 78500, "strength": "pivot", "type": "price"}
  ],

  "strong_resistances": [          # 주요 저항선
    {"level": 85000, "strength": "VAH", "type": "volume"}
  ],

  "nearest_support": 80000,        # 가장 가까운 지지
  "nearest_resistance": 85000,     # 가장 가까운 저항
  "support_distance_pct": 2.5,     # 지지선까지 거리 (%)
  "resistance_distance_pct": 3.7,  # 저항선까지 거리 (%)

  "signal": "uptrend_structure"    # 구조 판단
}
```

#### 신호 종류
- `uptrend_structure`: 현재가 > POC, 상승 구조
- `downtrend_structure`: 현재가 < POC, 하락 구조
- `near_support`: 지지선 근접 (2% 이내)
- `near_resistance`: 저항선 근접 (2% 이내)
- `neutral`: 중립

---

### 엔진 4: **fibonacci_engine.py** - 피보나치 분석

#### 피보나치 비율

**되돌림 (Retracement)**
```
0.236, 0.382, 0.5, 0.618, 0.786
```
- 상승 후 조정 시 지지선
- 하락 후 반등 시 저항선

**확장 (Extension)**
```
1.0, 1.272, 1.414, 1.618, 2.0, 2.618
```
- 목표가 설정
- 1.618 (황금비)이 가장 중요

#### 스윙 포인트 탐지

```python
def _find_swing_points(high, low, window=10):
    # 좌우 10일 중 최고점 → Swing High
    # 좌우 10일 중 최저점 → Swing Low
```

#### 되돌림 레벨 계산

**상승 추세 (Swing Low < Swing High)**
```
ret_0.618 = Swing High - (Swing High - Swing Low) × 0.618
```

**하락 추세 (Swing High < Swing Low)**
```
ret_0.618 = Swing Low + (Swing High - Swing Low) × 0.618
```

#### 분석 결과 구조

```python
{
  "swing_high": 90000,
  "swing_low": 75000,
  "trend": "uptrend",
  "is_uptrend": True,

  "retracement_levels": {
    "ret_0.236": 86460,
    "ret_0.382": 84270,
    "ret_0.5": 82500,
    "ret_0.618": 80730,
    "ret_0.786": 78210
  },

  "extension_levels": {
    "ext_1.0": 90000,
    "ext_1.272": 94080,
    "ext_1.414": 96210,
    "ext_1.618": 99270,
    "ext_2.0": 105000
  },

  "near_levels": [
    "ret_0.5:82500",
    "ext_1.618:99270"
  ],

  "signal": "FIBO_SUPPORT_STRONG"
}
```

#### 신호 종류
- `FIBO_SUPPORT_STRONG`: 0.5 또는 0.618 되돌림 근접 → 강력 지지
- `FIBO_SUPPORT`: 되돌림 레벨 근접 → 지지
- `FIBO_RESISTANCE_STRONG`: 0.5 또는 0.618 되돌림 근접 → 강력 저항
- `FIBO_RESISTANCE`: 되돌림 레벨 근접 → 저항
- `FIBO_EXTENSION_TARGET`: 확장 목표가 도달
- `ABOVE_SWING_HIGH`: 스윙 고점 돌파
- `BELOW_SWING_LOW`: 스윙 저점 이탈

---

## 사용 방법

### 1단계: 초기 데이터 수집

```bash
# 전체 202종목 100일 데이터 수집
python collector_init_100days.py
```

**결과**
- `data/` 폴더에 202개 PKL 파일 생성
- 예: `005930_100days.pkl`, `000660_100days.pkl`, ...

---

### 2단계: 실시간 분석 (analyze_live.py)

```bash
python analyze_live.py
```

**실행 예시**
```
종목코드 입력: 005930,000660
수집 기간 (기본 500일): 500

→ 삼성전자(005930) 분석 중...
→ SK하이닉스(000660) 분석 중...
```

**출력 내용**
- 4대 엔진 분석 결과
- 최종 종합 신호
- 주요 지표 요약

---

### 3단계: 상세 분석 (analyze_backdata.py)

```bash
python analyze_backdata.py
```

**실행 예시**
```
분석할 종목코드: 005930
또는
분석할 종목코드: all  (전체 스캔)
```

**`all` 모드 기능**
1. 전체 202종목 스캔
2. 매수 후보군 추출 (삼위일체 2개 이상 또는 BUY 신호)
3. 매도/회피 후보군 추출
4. 상세 분석 선택 가능

**출력 내용 (개별 종목)**
- **70줄 이상 상세 리포트**
- 삼위일체 상태 및 해석
- 변곡일별 분석
- 패턴 상세 해석
- 지지/저항 레벨
- 피보나치 레벨
- **PIONA 점수 (0~100점)** 및 최종 매매 의견
- 손절가/목표가 제시

---

### 4단계: 일일 업데이트 (매일 실행)

```bash
python collector_update_daily.py
```

**권장 실행 시점**
- 매일 오후 4시 이후 (장 마감 후)

**자동화 방법 (Windows)**
1. Windows 작업 스케줄러 실행
2. 새 작업 만들기
   - 트리거: 매일 오후 4시 30분
   - 동작: `python C:\path\to\collector_update_daily.py`

---

## 데이터 구조

### PKL 파일 구조

```python
# data/005930_100days.pkl
pandas.DataFrame (100 rows × 12 columns)

Columns:
  date            datetime64
  code            object
  open            int64
  high            int64
  low             int64
  close           int64
  volume          int64
  amount          int64
  range           int64
  gap             int64
  frgn_net_buy    float64 (None for 지수)
  inst_net_buy    float64 (None for 지수)
```

### 예시 데이터

| date | code | open | high | low | close | volume | amount | range | gap | frgn_net_buy | inst_net_buy |
|------|------|------|------|-----|-------|--------|--------|-------|-----|--------------|--------------|
| 2024-08-01 | 005930 | 82000 | 83000 | 81500 | 82500 | 15000000 | 1230000000000 | 1500 | 200 | 500000 | -200000 |
| 2024-08-02 | 005930 | 82300 | 83500 | 82000 | 83200 | 18000000 | 1490000000000 | 1500 | 700 | 700000 | 100000 |

---

## 4대 엔진 종합 분석 프로세스

### analyze_backdata.py 실행 시 흐름

```
1. PKL 파일 로드
   └─> data/005930_100days.pkl

2. 엔진1 실행 (Inflection)
   ├─> 일목균형표 계산
   ├─> 삼위일체 체크
   ├─> 300일선 규칙 확인
   ├─> 변곡일 분석
   └─> 최종 신호: ULTIMATE_BUY

3. 엔진2 실행 (Pattern)
   ├─> 20개 패턴 탐지
   ├─> 더블보텀 발견 (85% 신뢰도)
   ├─> 골든크로스 발견 (80% 신뢰도)
   └─> 최종 신호: STRONG_BUY

4. 엔진3 실행 (S/R)
   ├─> Volume Profile 계산
   ├─> POC = 82000
   ├─> 지지선 = 80000
   ├─> 저항선 = 85000
   └─> 신호: uptrend_structure

5. 엔진4 실행 (Fibonacci)
   ├─> Swing High = 90000
   ├─> Swing Low = 75000
   ├─> 현재가 = 82500 (0.5 되돌림 근접)
   └─> 신호: FIBO_SUPPORT_STRONG

6. 종합 점수 계산
   ├─> 삼위일체 완성 +30점
   ├─> 후행스팬 관통 +10점
   ├─> 양운 형성 +5점
   ├─> 매수패턴 우세 +10점
   ├─> 피보나치 지지 +10점
   └─> 총점: 65/100 → "매수 유리"

7. 최종 리포트 생성
   ├─> 70줄 상세 분석
   ├─> 손절가: 78400 (지지선 -2%)
   ├─> 1차 목표: 85000
   ├─> 2차 목표: 99270 (피보 1.618)
   └─> 매매 의견 출력
```

---

## 주요 기능 요약

### 강점

1. **종합적 분석**
   - 4개 엔진이 각기 다른 관점에서 분석
   - 신창환 이론 (추세), 패턴 (심리), S/R (수급), 피보나치 (기술)

2. **자동화**
   - 초기 수집 자동화
   - 일일 업데이트 자동화
   - 전체 종목 스캔 기능

3. **상세한 리포트**
   - 70줄 이상 한글 해석
   - 점수화 (0~100점)
   - 구체적 매매 포인트 제시

4. **데이터 무결성**
   - 12개 컬럼 표준화
   - PKL 형식으로 빠른 로딩
   - 중복 수집 방지

### 활용 시나리오

**시나리오 1: 매일 아침 매수 후보 발굴**
```bash
python analyze_backdata.py
입력: all
→ 202종목 스캔
→ 삼위일체 종목 리스트 확인
→ 상세 분석으로 최종 확인
```

**시나리오 2: 특정 종목 깊이 분석**
```bash
python analyze_backdata.py
입력: 005930
→ 삼성전자 70줄 상세 리포트
→ 손절가/목표가 확인
→ 매매 의사 결정
```

**시나리오 3: 신규 종목 500일 데이터 분석**
```bash
python get_data_only.py
입력: 000660
입력: 500
→ 500일 데이터 수집

python analyze_live.py
입력: 000660
입력: 500
→ 장기 추세 분석
```

---

## 기술 스택

- **언어**: Python 3.x
- **주요 라이브러리**:
  - `win32com.client`: Creon API 연동
  - `pandas`: 데이터 처리
  - `numpy`: 수치 계산
  - `pythoncom`: COM 초기화

- **데이터 저장**: PKL (Pickle) 형식
- **API**: Creon (대신증권 HTS API)

---

## 주의사항

1. **Creon 로그인 필수**
   - 분석 전 Creon Plus 로그인 필요
   - 로그인 끊김 시 `크레온연결복구.bat` 실행

2. **API 제약**
   - 요청 간격 1.1초 (자동 처리됨)
   - 일일 조회 제한 있음 (과도한 반복 실행 주의)

3. **데이터 유효성**
   - 지수는 투자자별 데이터 없음 (frgn_net_buy, inst_net_buy = None)
   - 300일 미만 데이터는 일부 분석 제한

4. **백테스팅 한계**
   - 과거 데이터 기반 분석
   - 미래 수익 보장 불가
   - 참고용으로만 활용

---

## 향후 개선 방안

1. **실시간 자동 매매 연동** (현재 미지원)
2. **웹 대시보드 개발** (Flask/Django)
3. **알림 기능** (삼위일체 발생 시 카톡/이메일)
4. **백테스팅 시뮬레이터** (과거 신호 검증)
5. **ML 기반 신호 통합** (4대 엔진 결과를 학습)

---

## 문의 및 기여

본 시스템은 개인 투자 보조 목적으로 개발되었습니다.

**면책 조항**
- 본 시스템의 분석 결과는 투자 참고 자료일 뿐, 투자 권유가 아닙니다.
- 투자 손실에 대한 책임은 투자자 본인에게 있습니다.
- 실전 투자 전 충분한 검증과 학습을 권장합니다.

---

**작성일**: 2024-11-23
**버전**: 1.0
**시스템명**: PIONA_CREON
**분석 엔진**: 4대 엔진 (Inflection, Pattern, S/R, Fibonacci)
