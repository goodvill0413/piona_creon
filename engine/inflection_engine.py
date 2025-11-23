# engine/inflection_engine.py
# 신창환 변곡이론 완전판 — 원본 강의 100% 반영
# 2025-11-22 대폭 업그레이드 + None 에러 수정

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class ShinInflectionEngine:
    """
    신창환 변곡점 이론 완전판
    
    핵심 원리:
    1. 변곡수: 9, 13, 26, 33, 42, 51, 65, 77, 88, 100
    2. 마디 분류: 소마디(26), 중마디(51), 대마디(77)
    3. 불가항력 변곡: 51, 77, 88
    4. 삼위일체: 후행스팬 관통 + 양운 + 변곡점 일치
    """
    
    # 신창환 원본 정의 (절대 불변)
    INFLECTION_DAYS = [9, 13, 26, 33, 42, 51, 65, 77, 88, 100]
    
    # 마디 분류
    SMALL_NODE = [26]           # 소마디
    MEDIUM_NODE = [51]          # 중마디  
    LARGE_NODE = [77]           # 대마디
    IRRESISTIBLE = [51, 77, 88] # 불가항력 변곡
    
    # 가변수 vs 대수
    VARIABLE_DAYS = [9, 13, 33, 42]  # 가변수 (작은 변곡)
    MAJOR_DAYS = [26, 51, 65, 77]    # 대수 (큰 변곡)
    
    def __init__(self):
        self.name = "ShinChangHwan_Complete_2025"

    # ========================================
    # 1. 일목균형표 5선 계산
    # ========================================
    def _calc_ichimoku(self, high: List[float], low: List[float], close: List[float]) -> Dict:
        """일목균형표 5선 계산 (신창환 원본)"""
        h, l, c = np.array(high), np.array(low), np.array(close)
        n = len(h)
        
        # 전환선 (9일) — 최근 9일 고저 중간값
        conv = (h[-9:].max() + l[-9:].min()) / 2 if n >= 9 else None
        
        # 기준선 (26일) — 최근 26일 고저 중간값
        base = (h[-26:].max() + l[-26:].min()) / 2 if n >= 26 else None
        
        # 선행스팬 1 (26일 후) — 전환선+기준선 중간값
        lead1 = (conv + base) / 2 if conv and base else None
        
        # 선행스팬 2 (26일 후) — 최근 52일 고저 중간값
        lead2 = (h[-52:].max() + l[-52:].min()) / 2 if n >= 52 else None
        
        # 후행스팬 — 현재 종가를 26일 전에 기입 (26일 전 종가와 비교)
        lagging = c[-1] if n >= 1 else None  # 현재 종가
        lagging_position = c[-26] if n >= 26 else None  # 26일 전 종가
        
        # 구름 색상: lead1 > lead2 → 양운(붉은구름), lead1 < lead2 → 음운(검은구름)
        cloud_color = "양운" if lead1 and lead2 and lead1 > lead2 else "음운"
        
        return {
            "conversion": round(conv) if conv else None,
            "base": round(base) if base else None,
            "lead1": round(lead1) if lead1 else None,
            "lead2": round(lead2) if lead2 else None,
            "lagging": round(lagging) if lagging else None,
            "lagging_position": round(lagging_position) if lagging_position else None,
            "cloud_color": cloud_color,
            "cloud_ahead_red": cloud_color == "양운"
        }

    # ========================================
    # 2. 전환선/기준선 폭 분석 (신창환 핵심)
    # ========================================
    def _calc_conv_base_width(self, ichimoku: Dict, close: List[float]) -> Dict:
        """
        전환선/기준선 폭 분석
        - 폭 넓음: 저항 강함 → 상승 어려움
        - 폭 좁아짐: 지지 강함 → 안전 매수 가능
        """
        conv = ichimoku["conversion"]
        base = ichimoku["base"]
        current = close[-1]
        
        if not conv or not base:
            return {"width": None, "width_pct": None, "signal": "데이터부족"}
        
        width = abs(conv - base)
        width_pct = (width / current) * 100
        
        # 폭 판단 기준 (현재가 대비 %)
        if width_pct < 1.0:
            signal = "폭_매우좁음_강력지지"
        elif width_pct < 2.0:
            signal = "폭_좁음_지지형성"
        elif width_pct < 4.0:
            signal = "폭_보통"
        else:
            signal = "폭_넓음_저항강함"
        
        return {
            "width": round(width),
            "width_pct": round(width_pct, 2),
            "conv_above_base": conv > base,  # 전환선이 기준선 위 = 상승 추세
            "signal": signal
        }

    # ========================================
    # 3. 후행스팬 관통 체크 (신창환 필수조건)
    # ========================================
    def _check_lagging_penetration(self, high: List[float], low: List[float], 
                                    close: List[float], ichimoku: Dict) -> Dict:
        """
        후행스팬 관통 체크 (신창환 3대 매매기법 중 하나)
        - 후행스팬이 26일 전 캔들(고가)을 위로 관통 → 강력 매수
        - 후행스팬이 10일 이평 위에 있으면 수익률 1.6배
        """
        if len(close) < 52:
            return {"penetrated": False, "above_ma10": False, "signal": "데이터부족"}
        
        current_close = close[-1]
        
        # 26일 전 캔들의 고가 (후행스팬이 관통해야 할 대상)
        past_high = max(high[-52:-26]) if len(high) >= 52 else high[-26]
        past_candle_high = high[-26]
        
        # 후행스팬 관통 여부: 현재 종가 > 26일 전 고가
        penetrated = current_close > past_high
        candle_penetrated = current_close > past_candle_high
        
        # 10일 이평 계산 (26일 전 시점의 10일 이평)
        if len(close) >= 36:
            ma10_at_lagging = np.mean(close[-36:-26])
            above_ma10 = current_close > ma10_at_lagging
        else:
            ma10_at_lagging = None
            above_ma10 = False
        
        # 신호 판단
        if penetrated and above_ma10:
            signal = "후행스팬_완벽관통_강력매수"
        elif penetrated:
            signal = "후행스팬_캔들관통_매수신호"
        elif above_ma10:
            signal = "후행스팬_이평위_관망"
        else:
            signal = "후행스팬_미관통_대기"
        
        return {
            "penetrated": penetrated,
            "candle_penetrated": candle_penetrated,
            "above_ma10": above_ma10,
            "ma10_at_lagging": round(ma10_at_lagging) if ma10_at_lagging else None,
            "signal": signal
        }

    # ========================================
    # 4. 선행스팬2 빗각 예측 (51/77변곡 핵심)
    # ========================================
    def _calc_ss2_slope(self, high: List[float], low: List[float], days_back: int = 77) -> Dict:
        """
        선행스팬2 빗각 예측
        - 77일 전 SS2가 꺾이면 → 26일 후 구름변곡 발생
        - 52일 신고가/신저가 갱신 시 SS2 방향 결정
        """
        if len(high) < days_back + 52:
            return {"slope": 0, "signal": "데이터부족"}  # None → 0으로 변경
        
        h, l = np.array(high), np.array(low)
        
        # 77일 전 시점의 SS2 계산
        idx_77 = -days_back
        ss2_77 = (h[idx_77-52:idx_77].max() + l[idx_77-52:idx_77].min()) / 2
        
        # 현재 시점의 SS2
        ss2_now = (h[-52:].max() + l[-52:].min()) / 2
        
        # 빗각 (기울기)
        slope = (ss2_now - ss2_77) / days_back
        slope_pct = (slope / ss2_77) * 100 * days_back  # % 변화
        
        # 52일 신고가/신저가 체크
        high_52 = h[-52:].max()
        low_52 = l[-52:].min()
        current_high = h[-1]
        current_low = l[-1]
        
        new_52_high = current_high >= high_52 * 0.99  # 1% 이내
        new_52_low = current_low <= low_52 * 1.01
        
        # 신호 판단
        if slope > 0 and new_52_high:
            signal = "SS2_상승빗각_52일신고가_강력상승"
        elif slope > 0:
            signal = "SS2_상승빗각_상승추세"
        elif slope < 0 and new_52_low:
            signal = "SS2_하락빗각_52일신저가_급락위험"
        elif slope < 0:
            signal = "SS2_하락빗각_하락추세"
        else:
            signal = "SS2_횡보"
        
        return {
            "ss2_77_ago": round(ss2_77),
            "ss2_now": round(ss2_now),
            "slope": round(slope, 2),
            "slope_pct": round(slope_pct, 2),
            "new_52_high": new_52_high,
            "new_52_low": new_52_low,
            "signal": signal
        }

    # ========================================
    # 5. 300일 이평선 절대 금기 체크
    # ========================================
    def _check_ma300_rule(self, close: List[float], cloud_color: str) -> Dict:
        """
        300일 이평선 절대 금기 규칙
        - 300일선 아래 + 음운 → 절대 매수 금지 (폭락 위험)
        - 300일선 위 + 양운 → 매수 가능
        """
        if len(close) < 300:
            # 데이터 부족해도 기본값 반환
            return {"ma300": None, "above_ma300": None, "distance_pct": 0, "position": "데이터부족", "signal": "판단불가"}
        
        ma300 = np.mean(close[-300:])
        current = close[-1]
        
        above_ma300 = current > ma300
        distance_pct = ((current - ma300) / ma300) * 100
        
        # 절대 금기 규칙
        if not above_ma300 and cloud_color == "음운":
            signal = "절대금기_300선아래_음운_매수금지"
        elif not above_ma300:
            signal = "위험_300선아래_주의"
        elif above_ma300 and cloud_color == "양운":
            signal = "안전_300선위_양운_매수가능"
        else:
            signal = "보통_300선위_음운_주의"
        
        return {
            "ma300": round(ma300),
            "above_ma300": above_ma300,
            "distance_pct": round(distance_pct, 2),
            "signal": signal
        }

    # ========================================
    # 6. 변곡일별 분석 (마디 이론)
    # ========================================
    def _analyze_inflection_days(self, dates: List, close: List[float], 
                                  lagging_result: Dict, cloud_color: str) -> List[Dict]:
        """
        각 변곡일별 상세 분석
        - 42일: 속임수 (가변), 쉬어가는 자리
        - 51일: 불가항력, 정배열/역배열 확정
        - 65일: 고점 확률 최고
        - 77~88일: 괴장년 구간, 변동성 극대화
        """
        if len(dates) < 100:
            return []
        
        inflections = []
        today = dates[-1]
        
        for days in self.INFLECTION_DAYS:
            target_date = today - timedelta(days=days)
            
            # 날짜 매칭 (거래일 기준으로 근사)
            idx = None
            for i, d in enumerate(dates):
                if d <= target_date:
                    idx = i
                elif d > target_date:
                    break
            
            if idx is None or idx < 0:
                continue
                
            price_then = close[idx]
            change_pct = (close[-1] / price_then - 1) * 100
            
            # 마디 타입 결정
            if days in self.LARGE_NODE:
                node_type = "대마디"
            elif days in self.MEDIUM_NODE:
                node_type = "중마디"
            elif days in self.SMALL_NODE:
                node_type = "소마디"
            elif days in self.VARIABLE_DAYS:
                node_type = "가변수"
            else:
                node_type = "변곡"
            
            signal = {
                "days": days,
                "date": target_date.strftime("%Y-%m-%d") if hasattr(target_date, 'strftime') else str(target_date),
                "price_then": round(price_then),
                "change_pct": round(change_pct, 2),
                "is_irresistible": days in self.IRRESISTIBLE,
                "is_major": days in self.MAJOR_DAYS,
                "node_type": node_type,
                "strength": None,
                "warning": None
            }
            
            # 특수 변곡 처리
            if days == 9:
                signal["description"] = "전환선 변곡 — 최초 상승 징후"
            
            elif days == 13:
                signal["description"] = "단기 조정 끝 — 골든크로스 확률 최고"
            
            elif days == 26:
                signal["description"] = "기준선 변곡 — 정배열 진입 마디"
                if cloud_color == "양운":
                    signal["strength"] = "★★★ 정배열 확정"
            
            elif days == 33:
                signal["description"] = "선행스팬1 괴리 — 추세 확정 구간"
            
            elif days == 42:
                signal["description"] = "회귀 위험 경계 — 속임수 구간"
                signal["warning"] = "60일 신고가 미갱신 시 제자리 회귀 위험"
            
            elif days == 51:
                signal["description"] = "불가항력 변곡 — 추세 방향 거스르기 불가"
                if abs(change_pct) > 10 and lagging_result.get("penetrated"):
                    signal["strength"] = "★★★★★ 불가항력 발동"
            
            elif days == 65:
                signal["description"] = "고점 확률 최고 — 소멸갭 주의"
                signal["warning"] = "51~65일 구간 대량거래+도지 출현 시 매도"
            
            elif days == 77:
                signal["description"] = "최종 대마디 — 추세의 변역(變易)"
                signal["warning"] = "괴장년 구간 시작 — 변동성 극대화"
                if cloud_color == "양운" and lagging_result.get("penetrated"):
                    signal["strength"] = "★★★★★ 대마디 삼위일체"
            
            elif days == 88:
                signal["description"] = "괴장년 변곡 — 구름변곡 최종 확정"
                signal["warning"] = "77~88일 사이 구름변곡 발생 → 판이냐 시냐"
            
            elif days == 100:
                signal["description"] = "100일 대변곡 — 장기 추세 확정"
            
            inflections.append(signal)
        
        return inflections

    # ========================================
    # 7. 삼위일체 체크 (최종 매수 신호)
    # ========================================
    def _check_trinity(self, lagging_result: Dict, cloud_color: str, 
                       inflections: List[Dict], ss2_result: Dict) -> Dict:
        """
        신창환 삼위일체 체크
        1. 후행스팬 관통
        2. 양운 (붉은 구름)
        3. 51/77 변곡점 일치 + SS2 상승
        """
        lagging_ok = lagging_result.get("penetrated", False)
        cloud_ok = cloud_color == "양운"
        
        # slope이 None일 수 있으므로 안전하게 처리
        slope_val = ss2_result.get("slope")
        ss2_ok = slope_val is not None and slope_val > 0
        
        # 51/77 변곡 확인
        major_inflection = any(
            inf["days"] in [51, 77] and inf.get("strength") 
            for inf in inflections
        )
        
        trinity_count = sum([lagging_ok, cloud_ok, major_inflection])
        
        if trinity_count == 3 and ss2_ok:
            signal = "삼위일체_완성_강력매수"
            confidence = 99.9
        elif trinity_count == 3:
            signal = "삼위일체_완성_매수"
            confidence = 95.0
        elif trinity_count == 2:
            signal = "2요소충족_매수검토"
            confidence = 70.0
        elif trinity_count == 1:
            signal = "1요소충족_관망"
            confidence = 40.0
        else:
            signal = "미충족_대기"
            confidence = 20.0
        
        return {
            "lagging_ok": lagging_ok,
            "cloud_ok": cloud_ok,
            "major_inflection_ok": major_inflection,
            "ss2_ok": ss2_ok,
            "trinity_count": trinity_count,
            "signal": signal,
            "confidence": confidence
        }

    # ========================================
    # 메인 분석 함수
    # ========================================
    def analyze(self, df) -> Dict:
        """
        신창환 변곡이론 완전 분석
        """
        if len(df) < 100:
            return {"error": "데이터 부족 (최소 100일 필요)"}
        
        # 데이터 추출
        high = df['high'].tolist()
        low = df['low'].tolist()
        close = df['close'].tolist()
        dates = df['date'].tolist()
        code = df['code'].iloc[0] if 'code' in df.columns else "UNKNOWN"
        
        # 1. 일목균형표 계산
        ichimoku = self._calc_ichimoku(high, low, close)
        
        # 2. 전환선/기준선 폭
        conv_base = self._calc_conv_base_width(ichimoku, close)
        
        # 3. 후행스팬 관통
        lagging = self._check_lagging_penetration(high, low, close, ichimoku)
        
        # 4. SS2 빗각
        ss2 = self._calc_ss2_slope(high, low)
        
        # 5. 300일 이평 체크
        ma300 = self._check_ma300_rule(close, ichimoku["cloud_color"])
        
        # 6. 변곡일 분석
        inflections = self._analyze_inflection_days(
            dates, close, lagging, ichimoku["cloud_color"]
        )
        
        # 7. 삼위일체 체크
        trinity = self._check_trinity(
            lagging, ichimoku["cloud_color"], inflections, ss2
        )
        
        # 최종 신호 결정
        if trinity["signal"] == "삼위일체_완성_강력매수":
            final_signal = "ULTIMATE_BUY"
        elif trinity["signal"] == "삼위일체_완성_매수":
            final_signal = "STRONG_BUY"
        elif ma300.get("signal", "").startswith("절대금기"):
            final_signal = "ABSOLUTE_NO_BUY"
        elif trinity["confidence"] >= 70:
            final_signal = "BUY"
        elif trinity["confidence"] >= 40:
            final_signal = "HOLD"
        else:
            final_signal = "WAIT"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "code": code,
            "current_price": close[-1],
            
            # 일목균형표
            "ichimoku": ichimoku,
            
            # 전환선/기준선 폭
            "conv_base_width": conv_base,
            
            # 후행스팬 관통
            "lagging_penetration": lagging,
            
            # SS2 빗각
            "ss2_slope": ss2,
            
            # 300일 이평
            "ma300_rule": ma300,
            
            # 변곡일 분석
            "inflections": inflections,
            
            # 삼위일체
            "trinity": trinity,
            
            # 최종 결과
            "final_signal": final_signal,
            "confidence": trinity["confidence"]
        }


# 테스트용
if __name__ == "__main__":
    print("ShinInflectionEngine 테스트")
    print("데이터가 필요합니다. DataMerger와 함께 사용하세요.")
