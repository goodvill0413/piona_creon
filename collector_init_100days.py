# collector_init_100days.py — 13컬럼 + skip logic
import os
import pandas as pd
from data_merger import DataMerger
from universe import UniverseManager

print("START merger")
print("=" * 60)
print("      PIONA_CREON - Initial 100-day Collector")
print("=" * 60)

um = UniverseManager()
symbols = um.get_symbols_only()

merger = DataMerger()
os.makedirs("data", exist_ok=True)

success = 0
fail = 0

for code in symbols:
    print(f"\n[{code}] 100일치 수집 중...")

    save_path = f"data/{code}_100days.pkl"

    # 이미 있으면 건너뛰기
    if os.path.exists(save_path):
        try:
            df_old = pd.read_pickle(save_path)
            if len(df_old) >= 100:
                print(f"건너뜀 → 이미 100일 있음")
                success += 1
                continue
        except:
            pass

    df = merger.get_full_data(code, days=100)

    if not df.empty:
        df.to_pickle(save_path)
        print(f"성공 → {save_path} ({len(df)}일)")
        success += 1
    else:
        print("실패")
        fail += 1

print("\n======================================================================")
print(f"           초기 데이터 수집 완료!")
print(f"           총 성공: {success}")
print(f"           총 실패: {fail}")
print("======================================================================")
input("엔터 누르면 종료...")
