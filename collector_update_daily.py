# collector_update_daily.py — 안정판
import os
import pandas as pd
from data_merger import DataMerger
from universe import UniverseManager

print("PIONA_CREON - Daily Updater")

um = UniverseManager()
symbols = um.get_symbols_only()

merger = DataMerger()
os.makedirs("data", exist_ok=True)

for code in symbols:
    print(f"\n[{code}] 최신 1일 업데이트 중...")

    save_path = f"data/{code}_100days.pkl"

    if not os.path.exists(save_path):
        print("기존 파일 없음 → Skip")
        continue

    df_old = pd.read_pickle(save_path)

    df_new = merger.get_full_data(code, days=2)
    if df_new.empty:
        print("오늘 데이터 없음 → Skip")
        continue

    last_date = df_old["date"].iloc[-1]
    new_rows = df_new[df_new["date"] > last_date]

    if len(new_rows) == 0:
        print("이미 최신임 → Skip")
        continue

    df_final = pd.concat([df_old, new_rows], ignore_index=True)
    df_final = df_final.tail(100)
    df_final.to_pickle(save_path)

    print(f"업데이트 완료 → 총 {len(df_final)}일")

print("\n모든 종목 업데이트 완료.")
input("엔터 누르면 종료...")
