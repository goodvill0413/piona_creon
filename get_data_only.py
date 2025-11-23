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
days = int(days_input) if days_input.isdigit() else 500
days = min(days, 1000)

code_list = [c.strip() for c in codes.split(",") if c.strip()]

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