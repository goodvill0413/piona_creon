import sys
import os
from data_merger import DataMerger

print("=" * 60, flush=True)
print("    PIONA_CREON - Data Collector (15 columns)", flush=True)
print("=" * 60, flush=True)

codes = input("\nStock codes (comma separated, ex: 005930,000660): ").strip()
if not codes:
    print("No input -> Exit", flush=True)
    input("Press Enter to exit...")
    exit()

days_input = input("Days to collect (default 500, max 1000): ").strip()
if days_input.isdigit():
    days = max(1, min(int(days_input), 1000))  # 1-1000 범위로 제한
else:
    days = 500

code_list = [c.strip() for c in codes.split(",") if c.strip()]

# 종목 코드 검증
valid_codes = []
for code in code_list:
    # 6자리 숫자 또는 U로 시작하는 지수 코드
    if (code.isdigit() and len(code) == 6) or (code.startswith("U") and len(code) >= 4):
        valid_codes.append(code)
    else:
        print(f"Warning: Invalid code format '{code}' - skipped", flush=True)

if not valid_codes:
    print("No valid codes -> Exit", flush=True)
    input("Press Enter to exit...")
    exit()

code_list = valid_codes

print(f"\nTarget: {code_list}", flush=True)
print(f"Days: {days}", flush=True)
print("-" * 60, flush=True)

merger = DataMerger()

os.makedirs("data", exist_ok=True)

success_count = 0
fail_count = 0

for code in code_list:
    print(f"\n[{code}] Collecting...", flush=True)
    df = merger.get_full_data(code, days=days)
    if not df.empty:
        path = f"data/{code}_{days}days.pkl"
        df.to_pickle(path)
        print(f"Saved -> {path}", flush=True)
        print(f"  Days: {len(df)}, Cols: {len(df.columns)}", flush=True)
        success_count += 1
    else:
        print(f"Failed: {code}", flush=True)
        fail_count += 1

print("\n" + "=" * 60, flush=True)
print(f"    Done: Success {success_count} / Fail {fail_count}", flush=True)
print("=" * 60, flush=True)
input("\nPress Enter to exit...")