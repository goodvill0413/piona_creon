# PIONA 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### 1단계: 환경 확인

```bash
# Python 버전 확인 (3.7 이상)
python --version

# 필수 라이브러리 설치
pip install pandas numpy pythoncom pywin32
```

### 2단계: Creon 로그인

1. Creon Plus 실행
2. 로그인 완료 확인

### 3단계: 초기 데이터 수집 (최초 1회만)

```bash
python collector_init_100days.py
```

**예상 소요 시간**: 5~10분
**결과**: data/ 폴더에 202개 PKL 파일 생성

### 4단계: 시스템 테스트

```bash
python test_system.py
```

**예상 결과**:
```
✓ 데이터 로딩: 통과
✓ CREON 엔진: 통과
✓ ML 엔진: 통과
✓ AI 엔진: 통과
✓ 점수 계산: 통과
✓ 매매 시스템: 통과

총 6/6 테스트 통과
✓ 모든 테스트 통과! 시스템 정상 작동
```

### 5단계: 자동매매 실행

```bash
python piona_main.py
```

---

## 📖 주요 명령어

### 데이터 수집

```bash
# 초기 100일 데이터 수집 (최초 1회)
python collector_init_100days.py

# 일일 업데이트 (매일 오후 4시 이후)
python collector_update_daily.py

# 개별 종목 데이터 수집
python get_data_only.py
# → 종목코드 입력: 005930
```

### 분석 실행

```bash
# 실시간 분석 (Creon API 사용)
python analyze_live.py

# 저장된 데이터 분석
python analyze_backdata.py
# → 종목코드 입력: all (전체 스캔)
# → 종목코드 입력: 005930 (개별 분석)
```

### 자동매매 실행

```bash
# 통합 자동매매 실행
python piona_main.py
```

---

## 🎯 실행 모드

### 모의매매 모드 (기본)

```python
# piona_main.py 수정
piona = PIONASystem(mode='simulation')
```

- 실제 주문 없음
- 매매 이력 JSON 저장
- 학습 데이터 축적

### 실전매매 모드 (향후 구현)

```python
# piona_main.py 수정
piona = PIONASystem(mode='real')
```

- 실제 Creon API 주문
- 실전 매매 실행

---

## 📊 결과 확인

### 1) 콘솔 출력

```
============================================================
PIONA 자동매매 시작
시간: 2025-11-23 16:00:00
============================================================

[1/202] 005930 분석 중...
✓ CREON 점수: 35
✓ ML 점수: 23
✓ AI 점수: 50
✓ 총합 점수: 108
✓ 매매 모드: swing
✓ 최종 신호: STRONG_BUY

[매수 실행] 005930
현재가: 82,500
손절가: 79,000
목표가1: 85,000
목표가2: 88,000

실행 결과: SUCCESS
액션: BUY

============================================================
[성과 분석]
============================================================
총 거래: 15회
승률: 60.0%
평균 수익률: 3.2%
```

### 2) JSON 파일

**database/positions.json** (현재 보유 종목)
```json
{
  "005930": {
    "buy_price": 82500,
    "buy_date": "2025-11-23T16:00:00",
    "trading_mode": "swing",
    "stop_loss": 79000,
    "target_1": 85000,
    "target_2": 88000
  }
}
```

**database/trading_history.json** (매매 이력)
```json
[
  {
    "code": "005930",
    "buy_price": 80000,
    "sell_price": 83000,
    "profit_pct": 3.75,
    "trading_mode": "swing",
    "reason": "TAKE_PROFIT"
  }
]
```

**models/pattern_stats.json** (패턴별 통계)
```json
{
  "trinity_complete": {
    "win_rate": 0.65,
    "avg_return": 8.5,
    "count": 12
  },
  "double_bottom": {
    "win_rate": 0.60,
    "avg_return": 7.2,
    "count": 8
  }
}
```

---

## 🔧 커스터마이징

### 매매 종목 수 조정

```python
# piona_main.py 의 run_auto_trading() 메서드
for candidate in buy_candidates[:5]:  # 상위 5개만
    # → 원하는 숫자로 변경
```

### 점수 임계값 조정

```python
# trading_system/score_calculator.py
if total_score >= 50:  # STRONG_BUY
    # → 원하는 값으로 조정
```

### 손절/익절 비율 조정

```python
# piona_ml/volatility_engine.py
stop_loss = current_price - (2 * current_atr)  # 2배
target_1 = current_price + (1.5 * current_atr)  # 1.5배
# → 배수 조정
```

---

## ⚠️ 문제 해결

### 1. "Creon 연결 실패"

**해결책**:
1. Creon Plus 로그인 확인
2. `크레온연결복구.bat` 실행
3. Python 32bit 사용 (Creon은 32bit만 지원)

### 2. "데이터 없음"

**해결책**:
```bash
python collector_init_100days.py
```

### 3. "모듈 없음" 오류

**해결책**:
```bash
pip install pandas numpy pythoncom pywin32
```

### 4. "테스트 실패"

**해결책**:
```bash
# 더미 데이터로 테스트 재실행
python test_system.py
```

---

## 📅 일일 운영

### 매일 오후 4시 이후

```bash
# 1) 데이터 업데이트
python collector_update_daily.py

# 2) 자동매매 실행
python piona_main.py
```

### Windows 작업 스케줄러 등록

1. **작업 스케줄러** 실행
2. **기본 작업 만들기** 클릭
3. 트리거: **매일 오후 4:30**
4. 동작: **프로그램 시작**
   - 프로그램: `python.exe`
   - 인수: `C:\path\to\piona_main.py`
   - 시작 위치: `C:\path\to\piona_creon`

---

## 📈 성과 향상 팁

### 1. 충분한 학습 데이터 확보

- 최소 50회 이상 매매 이력 축적
- 다양한 시장 환경에서 테스트

### 2. 점수 임계값 조정

- 승률이 낮으면 → 임계값 상향
- 기회가 적으면 → 임계값 하향

### 3. 패턴별 승률 확인

```python
from trading_system.learning_system import LearningSystem

learning = LearningSystem()
best = learning.get_best_patterns()

# 승률 높은 패턴 위주로 매매
```

### 4. 종목별 특성 파악

```json
// models/stock_profile.json
{
  "005930": {
    "trading_modes": {
      "swing": {
        "count": 10,
        "wins": 7,
        "avg_return": 4.5  // 스윙 유리
      },
      "scalp": {
        "count": 5,
        "wins": 2,
        "avg_return": -1.2  // 단타 불리
      }
    }
  }
}
```

---

## 🎓 학습 자료

### 시스템 이해

1. `SYSTEM_DOCUMENTATION.md` - PIONA_CREON 상세 문서
2. `README.md` - 통합 시스템 전체 문서
3. `QUICKSTART.md` - 이 문서

### 코드 분석

1. `piona_main.py` - 전체 흐름 파악
2. `engine/` - 4대 기술분석 로직
3. `piona_ml/` - 6대 시장분석 로직
4. `trading_system/` - 매매 실행 로직

---

## ✅ 체크리스트

### 시작 전

- [ ] Python 3.7 이상 설치
- [ ] 필수 라이브러리 설치
- [ ] Creon Plus 로그인
- [ ] collector_init_100days.py 실행 완료
- [ ] test_system.py 통과

### 매일

- [ ] Creon 로그인 확인
- [ ] collector_update_daily.py 실행
- [ ] piona_main.py 실행
- [ ] 성과 확인

### 주말

- [ ] 학습 데이터 백업
- [ ] 성과 분석
- [ ] 전략 조정

---

**작성일**: 2025-11-23
**버전**: 1.0

더 자세한 내용은 `README.md`를 참고하세요.
