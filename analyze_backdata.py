# analyze_backdata.py — 저장된 pkl 데이터로 4대 엔진 상세 분석
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), "engine"))

from inflection_engine import ShinInflectionEngine
from pattern_engine import ShinPatternEngine
from support_resistance_engine import VolumeProfileSR
from fibonacci_engine import CreonFibonacci

def fmt_num(val):
    if val is None or val == 'N/A':
        return 'N/A'
    try:
        return f"{val:,.0f}"
    except:
        return str(val)

def fmt_pct(val):
    if val is None:
        return 'N/A'
    try:
        return f"{val:+.1f}%"
    except:
        return str(val)

def generate_interpretation(code, price, inf, pat, sr, fib):
    """4대 엔진 결과를 종합해서 상세 해석 생성"""
    lines = []
    
    # === 1. 종합 판단 ===
    signals = []
    if inf.get('final_signal') in ['ULTIMATE_BUY', 'STRONG_BUY', 'BUY']:
        signals.append(('INF', 'BUY'))
    elif inf.get('final_signal') == 'ABSOLUTE_NO_BUY':
        signals.append(('INF', 'NO_BUY'))
    
    if pat.get('final_signal') == 'BUY':
        signals.append(('PAT', 'BUY'))
    elif pat.get('final_signal') == 'SELL':
        signals.append(('PAT', 'SELL'))
    
    if 'SUPPORT' in str(fib.get('signal', '')):
        signals.append(('FIB', 'SUPPORT'))
    elif 'RESISTANCE' in str(fib.get('signal', '')):
        signals.append(('FIB', 'RESISTANCE'))
    
    buy_count = sum(1 for s in signals if s[1] in ['BUY', 'SUPPORT'])
    sell_count = sum(1 for s in signals if s[1] in ['SELL', 'RESISTANCE', 'NO_BUY'])
    
    lines.append("=" * 70)
    lines.append(f"    [{code}] PIONA 4대 엔진 종합 리포트")
    lines.append("=" * 70)
    lines.append(f"현재가: {fmt_num(price)}원")
    lines.append("")
    
    # === 2. 변곡 엔진 상세 ===
    lines.append("-" * 70)
    lines.append("[1] 신창환 변곡이론 분석")
    lines.append("-" * 70)
    
    trinity = inf.get('trinity', {})
    ichimoku = inf.get('ichimoku', {})
    lagging = inf.get('lagging_penetration', {})
    ss2 = inf.get('ss2_slope', {})
    ma300 = inf.get('ma300_rule', {})
    conv_base = inf.get('conv_base_width', {})
    
    # 삼위일체 상태
    trinity_count = trinity.get('trinity_count', 0)
    lines.append(f"")
    lines.append(f"@ 삼위일체 상태: {trinity_count}/3 충족")
    lines.append(f"   +-- 후행스팬 관통: {'v 완료' if trinity.get('lagging_ok') else 'x 미관통'}")
    lines.append(f"   +-- 구름 색상: {'v 양운(붉은구름)' if trinity.get('cloud_ok') else 'x 음운(검은구름)'}")
    lines.append(f"   +-- 51/77 대변곡: {'v 발생' if trinity.get('major_inflection_ok') else 'x 미발생'}")
    lines.append(f"   +-- SS2 상승빗각: {'v 상승' if trinity.get('ss2_ok') else 'x 하락/횡보'}")
    
    # 삼위일체 해석
    if trinity_count == 3:
        lines.append(f"")
        lines.append(f"   *** 삼위일체 완성! 강력 매수 신호 ***")
        lines.append(f"   -> 후행스팬이 26일전 캔들을 관통하고, 양운 속에서 대변곡 발생")
        lines.append(f"   -> 신창환: '이 조건이면 무조건 산다'")
    elif trinity_count == 2:
        lines.append(f"")
        lines.append(f"   ** 2요소 충족 - 매수 검토 구간")
        missing = []
        if not trinity.get('lagging_ok'):
            missing.append("후행스팬 관통")
        if not trinity.get('cloud_ok'):
            missing.append("양운 전환")
        if not trinity.get('major_inflection_ok'):
            missing.append("51/77 변곡")
        lines.append(f"   -> 부족 요소: {', '.join(missing)}")
    elif trinity_count == 1:
        lines.append(f"")
        lines.append(f"   * 1요소만 충족 - 관망 권장")
    else:
        lines.append(f"")
        lines.append(f"   o 미충족 - 매수 대기")
    
    # 일목균형표 현황
    lines.append(f"")
    lines.append(f"@ 일목균형표 현황")
    lines.append(f"   +-- 전환선(9일): {fmt_num(ichimoku.get('conversion'))}")
    lines.append(f"   +-- 기준선(26일): {fmt_num(ichimoku.get('base'))}")
    lines.append(f"   +-- 선행1: {fmt_num(ichimoku.get('lead1'))} / 선행2: {fmt_num(ichimoku.get('lead2'))}")
    lines.append(f"   +-- 구름: {ichimoku.get('cloud_color', 'N/A')}")
    
    # 전환선/기준선 해석
    if conv_base.get('conv_above_base'):
        lines.append(f"   -> 전환선 > 기준선: 단기 상승 추세")
    else:
        lines.append(f"   -> 전환선 < 기준선: 단기 하락 추세")
    
    width_pct = conv_base.get('width_pct', 0)
    if width_pct and width_pct < 1.0:
        lines.append(f"   -> 전환/기준 폭 {width_pct}%: 매우 좁음 -> 강력 지지 형성")
    elif width_pct and width_pct < 2.0:
        lines.append(f"   -> 전환/기준 폭 {width_pct}%: 좁음 -> 지지 형성 중")
    elif width_pct and width_pct > 4.0:
        lines.append(f"   -> 전환/기준 폭 {width_pct}%: 넓음 -> 저항 강함")
    
    # 후행스팬 상세
    lines.append(f"")
    lines.append(f"@ 후행스팬 분석")
    lines.append(f"   +-- {lagging.get('signal', 'N/A')}")
    if lagging.get('penetrated'):
        lines.append(f"   -> 현재 종가가 26일전 고가를 돌파 -> 매수 신호")
        if lagging.get('above_ma10'):
            lines.append(f"   -> 10일 이평 위에서 관통 -> 수익률 1.6배 기대 (신창환)")
    else:
        lines.append(f"   -> 아직 26일전 캔들을 넘지 못함 -> 대기")
    
    # SS2 빗각
    lines.append(f"")
    lines.append(f"@ 선행스팬2 빗각 (77일 추세)")
    slope = ss2.get('slope', 0)
    if slope and slope > 0:
        lines.append(f"   +-- 상승 빗각 ({slope:+.2f}) -> 26일 후 구름 상승 예상")
        if ss2.get('new_52_high'):
            lines.append(f"   -> 52일 신고가 근접! 강력 상승 추세")
    elif slope and slope < 0:
        lines.append(f"   +-- 하락 빗각 ({slope:+.2f}) -> 26일 후 구름 하락 예상")
        if ss2.get('new_52_low'):
            lines.append(f"   -> 52일 신저가 근접! 급락 위험")
    else:
        lines.append(f"   +-- 횡보 중")
    
    # 300일선 체크
    lines.append(f"")
    lines.append(f"@ 300일 이평선 규칙")
    ma300_sig = ma300.get('signal', '')
    if '절대금기' in ma300_sig:
        lines.append(f"   +-- [경고] 절대 금기! 300일선 아래 + 음운")
        lines.append(f"   -> 신창환: '이 조건에서 매수하면 99% 손실'")
    elif ma300.get('above_ma300'):
        lines.append(f"   +-- [OK] 300일선 위 (거리: {fmt_pct(ma300.get('distance_pct'))})")
        lines.append(f"   -> 장기 상승 추세 유지")
    elif ma300.get('ma300'):
        lines.append(f"   +-- [주의] 300일선 아래 (거리: {fmt_pct(ma300.get('distance_pct'))})")
        lines.append(f"   -> 장기 하락 추세, 주의 필요")
    else:
        lines.append(f"   +-- 데이터 부족 (300일 미만)")
    
    # 변곡일 분석
    inflections = inf.get('inflections', [])
    if inflections:
        lines.append(f"")
        lines.append(f"@ 주요 변곡일 체크")
        for infl in inflections[:5]:
            days = infl.get('days', 0)
            node = infl.get('node_type', '')
            change = infl.get('change_pct', 0)
            desc = infl.get('description', '')
            strength = infl.get('strength', '')
            
            marker = "*" if strength else "-"
            lines.append(f"   {marker} {days}일전 ({node}): {fmt_pct(change)} | {desc}")
            if strength:
                lines.append(f"     -> {strength}")
            if infl.get('warning'):
                lines.append(f"     [!] {infl['warning']}")
    
    # === 3. 패턴 엔진 상세 ===
    lines.append(f"")
    lines.append("-" * 70)
    lines.append("[2] 차트 패턴 분석")
    lines.append("-" * 70)
    
    detected = pat.get('detected_patterns', [])
    buy_sigs = pat.get('buy_signals', 0)
    sell_sigs = pat.get('sell_signals', 0)
    
    lines.append(f"")
    lines.append(f"@ 패턴 감지 현황: {len(detected)}개")
    lines.append(f"   +-- 매수 신호: {buy_sigs}개")
    lines.append(f"   +-- 매도 신호: {sell_sigs}개")
    
    if detected:
        lines.append(f"")
        lines.append(f"@ 감지된 패턴 상세")
        for p in detected:
            pname = p.get('pattern', 'unknown')
            conf = p.get('confidence', 0)
            sig = p.get('signal', '')
            
            # 패턴별 해석
            interpretation = ""
            if pname == 'double_top':
                interpretation = "쌍봉 형성 -> 하락 반전 가능성"
            elif pname == 'double_bottom':
                interpretation = "쌍바닥 형성 -> 상승 반전 가능성"
            elif pname == 'head_shoulders':
                interpretation = "헤드앤숄더 -> 강력한 하락 신호"
            elif pname == 'inv_head_shoulders':
                interpretation = "역헤드앤숄더 -> 강력한 상승 신호"
            elif pname == 'golden_cross':
                interpretation = "골든크로스 -> 중장기 상승 시작"
            elif pname == 'death_cross':
                interpretation = "데드크로스 -> 중장기 하락 시작"
            elif pname == 'gap_up':
                interpretation = "갭상승 -> 강한 매수세 유입"
            elif pname == 'gap_down':
                interpretation = "갭하락 -> 매도 압력 증가"
            elif pname == 'bullish_engulfing':
                interpretation = "상승장악형 -> 단기 반등 신호"
            elif pname == 'bearish_engulfing':
                interpretation = "하락장악형 -> 단기 하락 신호"
            elif pname == 'morning_star':
                interpretation = "샛별형 -> 바닥 반전 신호"
            elif pname == 'evening_star':
                interpretation = "석별형 -> 천장 반전 신호"
            elif pname == 'hammer':
                interpretation = "망치형 -> 하락 추세 끝, 반등 예상"
            elif pname == 'shooting_star':
                interpretation = "유성형 -> 상승 추세 끝, 하락 예상"
            elif pname == 'doji':
                interpretation = "도지 -> 추세 전환 가능성"
            else:
                interpretation = sig
            
            icon = "[SELL]" if 'SELL' in sig or 'WEAK' in sig else "[BUY]" if 'BUY' in sig or 'STRONG' in sig else "[--]"
            lines.append(f"   {icon} {pname} (신뢰도 {conf}%)")
            lines.append(f"      -> {interpretation}")
    else:
        lines.append(f"")
        lines.append(f"   특별한 패턴 미감지")
    
    # === 4. 지지/저항 엔진 상세 ===
    lines.append(f"")
    lines.append("-" * 70)
    lines.append("[3] 지지/저항 분석 (Volume Profile)")
    lines.append("-" * 70)
    
    poc = sr.get('poc', 0)
    va = sr.get('value_area', [0, 0])
    atr = sr.get('atr', 0)
    nearest_sup = sr.get('nearest_support', 0)
    nearest_res = sr.get('nearest_resistance', 0)
    sup_dist = sr.get('support_distance_pct', 0)
    res_dist = sr.get('resistance_distance_pct', 0)
    
    lines.append(f"")
    lines.append(f"@ 핵심 가격대")
    lines.append(f"   +-- POC (최다거래가): {fmt_num(poc)}")
    lines.append(f"   +-- Value Area: {fmt_num(va[0])} ~ {fmt_num(va[1])}")
    
    # POC 대비 현재가 위치
    if price and poc:
        if price > poc * 1.1:
            lines.append(f"   -> 현재가가 POC 대비 10%+ 위 -> 과매수 주의")
        elif price > poc:
            lines.append(f"   -> 현재가가 POC 위 -> 상승 구조 유지")
        elif price < poc * 0.9:
            lines.append(f"   -> 현재가가 POC 대비 10%+ 아래 -> 과매도 구간")
        else:
            lines.append(f"   -> 현재가가 POC 근처 -> 방향 탐색 중")
    
    lines.append(f"")
    lines.append(f"@ 가까운 지지/저항")
    lines.append(f"   +-- 지지선: {fmt_num(nearest_sup)} ({sup_dist:.1f}% 아래)")
    lines.append(f"   +-- 저항선: {fmt_num(nearest_res)} ({res_dist:.1f}% 위)")
    
    # 거리 기반 해석
    if sup_dist < 2:
        lines.append(f"   [!] 지지선 임박! 이탈 시 추가 하락 주의")
    if res_dist < 2:
        lines.append(f"   [+] 저항선 임박! 돌파 시 상승 가속")
    
    # 지지/저항 레벨 상세
    supports = sr.get('strong_supports', [])
    resistances = sr.get('strong_resistances', [])
    
    if supports:
        lines.append(f"")
        lines.append(f"@ 주요 지지선")
        for s in supports[:3]:
            lines.append(f"   - {fmt_num(s['level'])} ({s['strength']}, {s['type']})")
    
    if resistances:
        lines.append(f"")
        lines.append(f"@ 주요 저항선")
        for r in resistances[:3]:
            lines.append(f"   - {fmt_num(r['level'])} ({r['strength']}, {r['type']})")
    
    lines.append(f"")
    lines.append(f"@ ATR (평균진폭): {fmt_num(atr)}")
    if price and atr:
        atr_pct = (atr / price) * 100
        lines.append(f"   -> 일일 변동성 약 {atr_pct:.1f}%")
    
    # === 5. 피보나치 엔진 상세 ===
    lines.append(f"")
    lines.append("-" * 70)
    lines.append("[4] 피보나치 분석")
    lines.append("-" * 70)
    
    swing_high = fib.get('swing_high', 0)
    swing_low = fib.get('swing_low', 0)
    trend = fib.get('trend', 'N/A')
    fib_sig = fib.get('signal', 'N/A')
    near_levels = fib.get('near_levels', [])
    ret_levels = fib.get('retracement_levels', {})
    ext_levels = fib.get('extension_levels', {})
    
    lines.append(f"")
    lines.append(f"@ 스윙 포인트")
    lines.append(f"   +-- 스윙 고점: {fmt_num(swing_high)}")
    lines.append(f"   +-- 스윙 저점: {fmt_num(swing_low)}")
    lines.append(f"   +-- 추세: {trend}")
    
    # 현재가 위치
    if price and swing_high and swing_low:
        swing_range = swing_high - swing_low
        if swing_range > 0:
            position = (price - swing_low) / swing_range * 100
            lines.append(f"   -> 현재가 위치: 스윙 범위의 {position:.0f}%")
    
    lines.append(f"")
    lines.append(f"@ 피보나치 신호: {fib_sig}")
    
    # 신호 해석
    if 'SUPPORT_STRONG' in fib_sig:
        lines.append(f"   -> 0.5 또는 0.618 되돌림 지지! 강력 반등 구간")
    elif 'SUPPORT' in fib_sig:
        lines.append(f"   -> 피보나치 되돌림 지지선 근처")
    elif 'RESISTANCE_STRONG' in fib_sig:
        lines.append(f"   -> 0.5 또는 0.618 되돌림 저항! 하락 반전 주의")
    elif 'RESISTANCE' in fib_sig:
        lines.append(f"   -> 피보나치 되돌림 저항선 근처")
    elif 'EXTENSION' in fib_sig:
        lines.append(f"   -> 확장 목표가 도달 구간")
    elif 'ABOVE_SWING_HIGH' in fib_sig:
        lines.append(f"   -> 스윙 고점 돌파! 신고가 영역")
    elif 'BELOW_SWING_LOW' in fib_sig:
        lines.append(f"   -> 스윙 저점 이탈! 신저가 영역")
    
    if near_levels:
        lines.append(f"")
        lines.append(f"@ 근접 피보나치 레벨")
        for lvl in near_levels[:3]:
            lines.append(f"   - {lvl}")
    
    # 되돌림 레벨
    if ret_levels:
        lines.append(f"")
        lines.append(f"@ 되돌림 레벨 (지지선 후보)")
        for k, v in list(ret_levels.items())[:5]:
            marker = " <-- 현재가 근접" if price and abs(price - v) / price < 0.02 else ""
            lines.append(f"   - {k}: {fmt_num(v)}{marker}")
    
    # 확장 레벨
    if ext_levels:
        lines.append(f"")
        lines.append(f"@ 확장 레벨 (목표가 후보)")
        for k, v in list(ext_levels.items())[:4]:
            marker = " <-- 현재가 근접" if price and abs(price - v) / price < 0.02 else ""
            lines.append(f"   - {k}: {fmt_num(v)}{marker}")
    
    # === 6. 종합 의견 ===
    lines.append(f"")
    lines.append("=" * 70)
    lines.append("[종합 의견]")
    lines.append("=" * 70)
    
    # 점수 계산
    score = 50  # 기본 중립
    reasons = []
    
    # 변곡 점수
    if trinity_count >= 3:
        score += 30
        reasons.append("삼위일체 완성 (+30)")
    elif trinity_count == 2:
        score += 15
        reasons.append("삼위일체 2요소 (+15)")
    
    if trinity.get('lagging_ok'):
        score += 10
        reasons.append("후행스팬 관통 (+10)")
    
    if trinity.get('cloud_ok'):
        score += 5
        reasons.append("양운 형성 (+5)")
    
    if ma300.get('signal', '').startswith('절대금기'):
        score -= 40
        reasons.append("300일선 절대금기 (-40)")
    elif ma300.get('above_ma300'):
        score += 5
        reasons.append("300일선 위 (+5)")
    
    # 패턴 점수
    if buy_sigs > sell_sigs:
        score += (buy_sigs - sell_sigs) * 5
        reasons.append(f"매수패턴 우세 (+{(buy_sigs - sell_sigs) * 5})")
    elif sell_sigs > buy_sigs:
        score -= (sell_sigs - buy_sigs) * 5
        reasons.append(f"매도패턴 우세 (-{(sell_sigs - buy_sigs) * 5})")
    
    # 피보나치 점수
    if 'SUPPORT' in fib_sig:
        score += 10
        reasons.append("피보나치 지지 (+10)")
    elif 'RESISTANCE' in fib_sig:
        score -= 10
        reasons.append("피보나치 저항 (-10)")
    
    # S/R 점수
    if sup_dist < 2:
        score -= 5
        reasons.append("지지선 임박 (-5)")
    if res_dist < 2 and price and nearest_res and price < nearest_res:
        score += 5
        reasons.append("저항 돌파 임박 (+5)")
    
    # 최종 판정
    lines.append(f"")
    lines.append(f"@ PIONA 점수: {score}/100")
    lines.append(f"")
    
    for r in reasons:
        lines.append(f"   - {r}")
    
    lines.append(f"")
    if score >= 80:
        lines.append(f"   ***** 강력 매수 추천")
        lines.append(f"   -> 삼위일체 또는 다중 매수 신호 확인")
        lines.append(f"   -> 적극적 포지션 구축 고려")
    elif score >= 65:
        lines.append(f"   ****- 매수 유리")
        lines.append(f"   -> 대부분의 지표가 긍정적")
        lines.append(f"   -> 분할 매수 전략 권장")
    elif score >= 50:
        lines.append(f"   ***-- 중립/관망")
        lines.append(f"   -> 혼조세, 추가 신호 대기")
        lines.append(f"   -> 기존 포지션 유지")
    elif score >= 35:
        lines.append(f"   **--- 매도 우위")
        lines.append(f"   -> 하락 신호 다수 감지")
        lines.append(f"   -> 비중 축소 또는 손절 고려")
    else:
        lines.append(f"   *---- 강력 매도/회피")
        lines.append(f"   -> 절대금기 또는 다중 매도 신호")
        lines.append(f"   -> 즉시 청산 권장")
    
    # 핵심 매매 포인트
    lines.append(f"")
    lines.append(f"@ 핵심 매매 포인트")
    if nearest_sup:
        lines.append(f"   - 손절가: {fmt_num(int(nearest_sup * 0.98))} (지지선 -2%)")
    if nearest_res:
        lines.append(f"   - 1차 목표: {fmt_num(nearest_res)}")
    if ext_levels:
        ext_161 = ext_levels.get('ext_1.618')
        if ext_161:
            lines.append(f"   - 2차 목표: {fmt_num(ext_161)} (피보 1.618)")
    
    lines.append(f"")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def run_analysis(code, simple=False):
    # pkl 파일에서 데이터 로드
    pkl_path = f"data/{code}_100days.pkl"
    if not os.path.exists(pkl_path):
        print(f"파일 없음: {pkl_path}")
        return None
    
    df = pd.read_pickle(pkl_path)
    if df.empty:
        print("데이터 없음")
        return None
    
    price = df['close'].iloc[-1]
    
    # 4대 엔진 실행
    try:
        inf = ShinInflectionEngine().analyze(df)
    except Exception as e:
        inf = {"error": str(e)}
    
    try:
        pat = ShinPatternEngine().run_all_patterns(df)
    except Exception as e:
        pat = {}
    
    try:
        sr = VolumeProfileSR().analyze(df)
    except Exception as e:
        sr = {}
    
    try:
        fib = CreonFibonacci().analyze(df)
    except Exception as e:
        fib = {}
    
    if simple:
        # 간단 출력 (all 모드용)
        inf_sig = inf.get('final_signal', 'N/A')
        pat_sig = pat.get('final_signal', 'N/A')
        fib_sig = fib.get('signal', 'N/A')
        trinity = inf.get('trinity', {}).get('trinity_count', 0)
        return {
            "code": code,
            "price": price,
            "inflection": inf_sig,
            "pattern": pat_sig,
            "fib": fib_sig,
            "trinity": trinity,
            "inf": inf,
            "pat": pat,
            "sr": sr,
            "fib_full": fib
        }
    
    # 상세 리포트 출력
    report = generate_interpretation(code, price, inf, pat, sr, fib)
    print(report)
    
    return {"code": code, "inflection": inf, "pattern": pat, "sr": sr, "fib": fib}


def main():
    print("=" * 70)
    print("    PIONA 4대 엔진 분석기 (상세 리포트)")
    print("=" * 70)
    
    # data 폴더의 pkl 파일 목록
    if not os.path.exists("data"):
        print("data 폴더가 없습니다!")
        input("Press Enter...")
        return
    
    pkl_files = [f for f in os.listdir("data") if f.endswith("_100days.pkl")]
    print(f"\n수집된 데이터: {len(pkl_files)}종목")
    
    codes = input("\n분석할 종목코드 (ex: 005930,000660 또는 all): ").strip()
    if not codes:
        print("입력 없음 -> 종료")
        input("Press Enter...")
        return
    
    if codes.lower() == "all":
        code_list = [f.replace("_100days.pkl", "") for f in pkl_files]
        
        # 전체 스캔 모드
        print(f"\n{len(code_list)}종목 스캔 중...")
        results = []
        for i, code in enumerate(code_list):
            if (i+1) % 20 == 0:
                print(f"  {i+1}/{len(code_list)} 완료...")
            result = run_analysis(code, simple=True)
            if result:
                results.append(result)
        
        # 결과 정렬 (삼위일체 수, BUY 신호 우선)
        buy_list = [r for r in results if r['trinity'] >= 2 or 'BUY' in str(r['inflection'])]
        sell_list = [r for r in results if 'SELL' in str(r['pattern']) or 'NO_BUY' in str(r['inflection'])]
        
        print(f"\n{'='*70}")
        print(f"    전체 {len(results)}종목 스캔 결과")
        print(f"{'='*70}")
        
        print(f"\n@ 매수 후보 ({len(buy_list)}종목)")
        print("-" * 50)
        for r in sorted(buy_list, key=lambda x: x['trinity'], reverse=True)[:10]:
            print(f"  {r['code']} | {r['price']:>10,}원 | 삼위일체:{r['trinity']}/3 | {r['inflection']}")
        
        print(f"\n@ 매도/회피 후보 ({len(sell_list)}종목)")
        print("-" * 50)
        for r in sell_list[:10]:
            print(f"  {r['code']} | {r['price']:>10,}원 | {r['inflection']} | {r['pattern']}")
        
        # 상세 분석 선택
        detail = input(f"\n상세 분석할 종목코드 (엔터=종료): ").strip()
        if detail:
            run_analysis(detail, simple=False)
    
    else:
        code_list = [c.strip() for c in codes.split(",") if c.strip()]
        for code in code_list:
            run_analysis(code, simple=False)
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
