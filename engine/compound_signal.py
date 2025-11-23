# engine/compound_signal.py
# PIONA 종합 신호 엔진 - 모든 엔진을 통합하여 최종 신호 생성

from typing import Dict
from datetime import datetime

# 각 엔진 임포트
try:
    from .pattern_engine import ShinPatternEngine
    from .fibonacci_engine import CreonFibonacci
    from .support_resistance_engine import VolumeProfileSR
    from .inflection_engine import ShinInflectionEngine
except ImportError:
    # 상대 임포트 실패 시 절대 임포트 시도
    from pattern_engine import ShinPatternEngine
    from fibonacci_engine import CreonFibonacci
    from support_resistance_engine import VolumeProfileSR
    from inflection_engine import ShinInflectionEngine


class PIONA_CompoundSignal:
    """
    PIONA 종합 신호 엔진
    - 패턴 엔진 (ShinPatternEngine)
    - 피보나치 엔진 (CreonFibonacci)
    - 지지/저항 엔진 (VolumeProfileSR)
    - 변곡 엔진 (ShinInflectionEngine)
    를 모두 통합하여 최종 매매 신호를 생성합니다.
    """

    def __init__(self):
        self.pattern_engine = ShinPatternEngine()
        self.fibonacci_engine = CreonFibonacci()
        self.sr_engine = VolumeProfileSR()
        self.inflection_engine = ShinInflectionEngine()

    def analyze(self, df) -> Dict:
        """
        모든 엔진을 실행하고 종합 신호를 생성

        Args:
            df: OHLCV 데이터프레임 (columns: date, open, high, low, close, volume, code)

        Returns:
            Dict: 종합 분석 결과
        """
        if len(df) < 100:
            return {
                "error": "데이터 부족 (최소 100일 필요)",
                "data_length": len(df)
            }

        # 각 엔진 실행
        try:
            pattern_result = self.pattern_engine.run_all_patterns(df)
        except Exception as e:
            pattern_result = {"error": str(e)}

        try:
            fibonacci_result = self.fibonacci_engine.analyze(df)
        except Exception as e:
            fibonacci_result = {"error": str(e)}

        try:
            sr_result = self.sr_engine.analyze(df)
        except Exception as e:
            sr_result = {"error": str(e)}

        try:
            inflection_result = self.inflection_engine.analyze(df)
        except Exception as e:
            inflection_result = {"error": str(e)}

        # 신호 점수 계산
        buy_score = 0
        sell_score = 0
        confidence_sum = 0

        # 패턴 엔진 평가
        if "final_signal" in pattern_result:
            if "BUY" in pattern_result["final_signal"]:
                buy_score += pattern_result.get("buy_signals", 0) * 10
            elif "SELL" in pattern_result["final_signal"]:
                sell_score += pattern_result.get("sell_signals", 0) * 10
            confidence_sum += pattern_result.get("total_confidence", 0)

        # 피보나치 엔진 평가
        if "signal" in fibonacci_result and fibonacci_result["signal"] != "HOLD":
            if "지지" in fibonacci_result["signal"] or "확장" in fibonacci_result["signal"]:
                buy_score += 15
            confidence_sum += 50

        # 지지/저항 엔진 평가
        if "signal" in sr_result:
            if sr_result["signal"] == "uptrend_structure":
                buy_score += 20
            elif sr_result["signal"] == "downtrend_structure":
                sell_score += 20
            elif sr_result["signal"] == "near_support":
                buy_score += 10
            elif sr_result["signal"] == "near_resistance":
                sell_score += 10
            confidence_sum += 60

        # 변곡 엔진 평가 (가장 중요)
        if "final_signal" in inflection_result:
            signal = inflection_result["final_signal"]
            if signal == "ULTIMATE_BUY":
                buy_score += 100
            elif signal == "STRONG_BUY":
                buy_score += 80
            elif signal == "BUY":
                buy_score += 50
            elif signal == "ABSOLUTE_NO_BUY":
                sell_score += 100
                buy_score = 0  # 절대 금기
            confidence_sum += inflection_result.get("confidence", 0)

        # 최종 신호 결정
        total_score = buy_score + sell_score
        if total_score == 0:
            final_signal = "HOLD"
            final_confidence = 0
        else:
            if buy_score > sell_score * 2 and buy_score >= 100:
                final_signal = "STRONG_BUY"
                final_confidence = min(95, (buy_score / (buy_score + sell_score)) * 100)
            elif buy_score > sell_score:
                final_signal = "BUY"
                final_confidence = min(80, (buy_score / (buy_score + sell_score)) * 100)
            elif sell_score > buy_score * 2 and sell_score >= 100:
                final_signal = "STRONG_SELL"
                final_confidence = min(95, (sell_score / (buy_score + sell_score)) * 100)
            elif sell_score > buy_score:
                final_signal = "SELL"
                final_confidence = min(80, (sell_score / (buy_score + sell_score)) * 100)
            else:
                final_signal = "HOLD"
                final_confidence = 50

        # 절대 금기 체크
        if inflection_result.get("final_signal") == "ABSOLUTE_NO_BUY":
            final_signal = "ABSOLUTE_NO_BUY"
            final_confidence = 99

        return {
            "timestamp": datetime.now().isoformat(),
            "code": df['code'].iloc[0] if 'code' in df.columns else "UNKNOWN",
            "current_price": df['close'].iloc[-1],

            # 각 엔진 결과
            "pattern_analysis": pattern_result,
            "fibonacci_analysis": fibonacci_result,
            "support_resistance": sr_result,
            "inflection_analysis": inflection_result,

            # 종합 점수
            "buy_score": buy_score,
            "sell_score": sell_score,
            "confidence_sum": confidence_sum,

            # 최종 신호
            "final_signal": final_signal,
            "confidence": round(final_confidence, 2),

            # 요약
            "summary": self._generate_summary(
                pattern_result, fibonacci_result, sr_result,
                inflection_result, final_signal, final_confidence
            )
        }

    def _generate_summary(self, pattern_result: Dict, fibonacci_result: Dict,
                         sr_result: Dict, inflection_result: Dict,
                         final_signal: str, confidence: float) -> str:
        """
        분석 결과 요약 생성
        """
        summary_parts = []

        # 패턴 요약
        if "detected_patterns" in pattern_result and pattern_result["detected_patterns"]:
            patterns = [p["pattern"] for p in pattern_result["detected_patterns"][:3]]
            summary_parts.append(f"패턴: {', '.join(patterns)}")

        # 피보나치 요약
        if "signal" in fibonacci_result and fibonacci_result["signal"] != "HOLD":
            summary_parts.append(f"피보나치: {fibonacci_result['signal']}")

        # 지지/저항 요약
        if "signal" in sr_result:
            summary_parts.append(f"지지/저항: {sr_result['signal']}")

        # 변곡 요약
        if "trinity" in inflection_result:
            trinity = inflection_result["trinity"]
            if trinity.get("trinity_count", 0) >= 2:
                summary_parts.append(
                    f"변곡: {trinity['signal']} (삼위일체 {trinity['trinity_count']}/3)"
                )

        # 최종 신호
        summary_parts.append(f"최종: {final_signal} (신뢰도: {confidence}%)")

        return " | ".join(summary_parts)


if __name__ == "__main__":
    print("PIONA_CompoundSignal 테스트")
    print("사용법: compound = PIONA_CompoundSignal()")
    print("        result = compound.analyze(df)")
