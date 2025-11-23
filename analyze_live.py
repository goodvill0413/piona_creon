import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "engine"))

from data_merger import DataMerger
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

def run_analysis(code, days=500):
    print(f"\n{'='*70}", flush=True)
    print(f"    [{code}] PIONA 4-Engine Analysis", flush=True)
    print(f"{'='*70}", flush=True)
    
    print("\n[1/5] Collecting data...", flush=True)
    merger = DataMerger()
    df = merger.get_full_data(code, days=days)
    if df.empty:
        print("Data collection failed", flush=True)
        return None
    print(f"Done: {len(df)} days", flush=True)
    
    print("\n[2/5] Inflection analysis...", flush=True)
    try:
        inf = ShinInflectionEngine().analyze(df)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        inf = {}
    
    print("\n[3/5] Pattern analysis...", flush=True)
    try:
        pat = ShinPatternEngine().run_all_patterns(df)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        pat = {}
    
    print("\n[4/5] Support/Resistance...", flush=True)
    try:
        sr = VolumeProfileSR().analyze(df)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        sr = {}
    
    print("\n[5/5] Fibonacci...", flush=True)
    try:
        fib = CreonFibonacci().analyze(df)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        fib = {}
    
    print(f"\n{'='*70}", flush=True)
    print(f"    [{code}] PIONA Final Report", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"Current Price: {df['close'].iloc[-1]:,}", flush=True)
    print(f"{'='*70}", flush=True)
    
    print(f"\n[1] Inflection Analysis (Shin Chang-hwan)", flush=True)
    print(f"-" * 50, flush=True)
    if inf.get("error"):
        print(f"  Error: {inf['error']}", flush=True)
    else:
        print(f"  Final Signal: {inf.get('final_signal', 'N/A')}", flush=True)
        print(f"  Confidence: {inf.get('confidence', 0)}%", flush=True)
        trinity = inf.get('trinity', {})
        print(f"  Trinity Check:", flush=True)
        print(f"    - Lagging Penetration: {'Yes' if trinity.get('lagging_ok') else 'No'}", flush=True)
        print(f"    - Cloud Color (Yang): {'Yes' if trinity.get('cloud_ok') else 'No'}", flush=True)
        print(f"    - Major Inflection: {'Yes' if trinity.get('major_inflection_ok') else 'No'}", flush=True)
        print(f"    - SS2 Slope Up: {'Yes' if trinity.get('ss2_ok') else 'No'}", flush=True)
        ichimoku = inf.get('ichimoku', {})
        print(f"  Ichimoku:", flush=True)
        print(f"    - Conversion: {fmt_num(ichimoku.get('conversion'))}", flush=True)
        print(f"    - Base: {fmt_num(ichimoku.get('base'))}", flush=True)
        print(f"    - Cloud: {ichimoku.get('cloud_color', 'N/A')}", flush=True)
        ma300 = inf.get('ma300_rule', {})
        print(f"  MA300 Rule: {ma300.get('signal', 'N/A')}", flush=True)
        inflections = inf.get('inflections', [])
        if inflections:
            print(f"  Key Inflection Points:", flush=True)
            for infl in inflections[:5]:
                days_ago = infl.get('days', 0)
                node = infl.get('node_type', '')
                change = infl.get('change_pct', 0)
                desc = infl.get('description', '')
                print(f"    - {days_ago}D ({node}): {change:+.1f}% | {desc}", flush=True)
    
    print(f"\n[2] Pattern Analysis", flush=True)
    print(f"-" * 50, flush=True)
    detected = pat.get('detected_patterns', [])
    print(f"  Final Signal: {pat.get('final_signal', 'N/A')}", flush=True)
    print(f"  Buy Signals: {pat.get('buy_signals', 0)}", flush=True)
    print(f"  Sell Signals: {pat.get('sell_signals', 0)}", flush=True)
    print(f"  Total Confidence: {pat.get('total_confidence', 0)}", flush=True)
    if detected:
        print(f"  Detected Patterns:", flush=True)
        for p in detected:
            pname = p.get('pattern', 'unknown')
            conf = p.get('confidence', 0)
            sig = p.get('signal', '')
            print(f"    - {pname}: confidence {conf}%, signal {sig}", flush=True)
    else:
        print(f"  Detected Patterns: None", flush=True)
    
    print(f"\n[3] Support/Resistance Analysis", flush=True)
    print(f"-" * 50, flush=True)
    print(f"  Signal: {sr.get('signal', 'N/A')}", flush=True)
    print(f"  POC (Point of Control): {fmt_num(sr.get('poc'))}", flush=True)
    va = sr.get('value_area', [0, 0])
    print(f"  Value Area: {fmt_num(va[0])} ~ {fmt_num(va[1])}", flush=True)
    print(f"  ATR: {fmt_num(sr.get('atr'))}", flush=True)
    print(f"  Nearest Support: {fmt_num(sr.get('nearest_support'))} ({sr.get('support_distance_pct', 0):.1f}% below)", flush=True)
    print(f"  Nearest Resistance: {fmt_num(sr.get('nearest_resistance'))} ({sr.get('resistance_distance_pct', 0):.1f}% above)", flush=True)
    supports = sr.get('strong_supports', [])
    if supports:
        print(f"  Support Levels:", flush=True)
        for s in supports[:3]:
            print(f"    - {fmt_num(s['level'])} ({s['strength']}, {s['type']})", flush=True)
    resistances = sr.get('strong_resistances', [])
    if resistances:
        print(f"  Resistance Levels:", flush=True)
        for r in resistances[:3]:
            print(f"    - {fmt_num(r['level'])} ({r['strength']}, {r['type']})", flush=True)
    
    print(f"\n[4] Fibonacci Analysis", flush=True)
    print(f"-" * 50, flush=True)
    print(f"  Signal: {fib.get('signal', 'N/A')}", flush=True)
    print(f"  Trend: {fib.get('trend', 'N/A')}", flush=True)
    print(f"  Swing High: {fmt_num(fib.get('swing_high'))}", flush=True)
    print(f"  Swing Low: {fmt_num(fib.get('swing_low'))}", flush=True)
    near = fib.get('near_levels', [])
    if near:
        print(f"  Near Fibo Levels:", flush=True)
        for lvl in near:
            print(f"    - {lvl}", flush=True)
    else:
        print(f"  Near Fibo Levels: None (not near any key level)", flush=True)
    ret_levels = fib.get('retracement_levels', {})
    if ret_levels:
        print(f"  Retracement Levels:", flush=True)
        for k, v in ret_levels.items():
            print(f"    - {k}: {fmt_num(v)}", flush=True)
    ext_levels = fib.get('extension_levels', {})
    if ext_levels:
        print(f"  Extension Levels:", flush=True)
        for k, v in list(ext_levels.items())[:4]:
            print(f"    - {k}: {fmt_num(v)}", flush=True)
    
    print(f"\n{'='*70}", flush=True)
    print(f"    SUMMARY", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"  Inflection: {inf.get('final_signal', 'N/A')} ({inf.get('confidence', 0)}%)", flush=True)
    print(f"  Pattern: {pat.get('final_signal', 'N/A')} (patterns: {len(detected)})", flush=True)
    print(f"  S/R: {sr.get('signal', 'N/A')}", flush=True)
    print(f"  Fibonacci: {fib.get('signal', 'N/A')}", flush=True)
    print(f"{'='*70}", flush=True)
    
    return {"code": code, "inflection": inf, "pattern": pat, "sr": sr, "fib": fib}

def main():
    print("=" * 70, flush=True)
    print("    PIONA_CREON Live Analyzer", flush=True)
    print("=" * 70, flush=True)
    
    codes = input("\nStock codes (ex: 005930,000660): ").strip()
    if not codes:
        print("No input -> Exit", flush=True)
        input("Press Enter...")
        return
    
    days_input = input("Days (default 500): ").strip()
    days = int(days_input) if days_input.isdigit() else 500
    
    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    
    for code in code_list:
        run_analysis(code, days)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()