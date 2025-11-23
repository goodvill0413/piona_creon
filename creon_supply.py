# creon_supply.py — 13컬럼 안정판
import win32com.client
import pandas as pd

class CreonSupply:
    def __init__(self):
        self.inst = win32com.client.Dispatch("CpSysDib.CpSvr7244")

    def get_investor(self, code, days=100):
        try:
            self.inst.SetInputValue(0, code)
            self.inst.SetInputValue(1, ord('1'))  # 일별
            self.inst.SetInputValue(2, days)
            self.inst.BlockRequest()

            status = self.inst.GetDibStatus()
            if status != 0:
                return pd.DataFrame()

            cnt = self.inst.GetHeaderValue(1)
            rows = []
            for i in range(cnt):
                rows.append({
                    "date": self.inst.GetDataValue(0, i),
                    "frgn_net_buy": self.inst.GetDataValue(1, i),
                    "inst_net_buy": self.inst.GetDataValue(2, i),
                })
            return pd.DataFrame(rows)
        except Exception as e:
            print(f"[CreonSupply] Error: {e}")
            return pd.DataFrame()

    # strength, bid_ask_ratio 제거판
    def get_realtime(self, code):
        return {"strength": 0, "bid_ask_ratio": None}
