import sys
import win32com.client
import pythoncom
import time
import pandas as pd

print("START", flush=True)

_last_request = 0.0

def _rate_limit():
    global _last_request
    now = time.time()
    elapsed = now - _last_request
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    _last_request = time.time()

class CreonOHLCV:
    def __init__(self):
        self.connected = False
        self._connect()

    def _connect(self):
        try:
            pythoncom.CoInitialize()
            cp = win32com.client.Dispatch("CpUtil.CpCybos")
            if cp.IsConnect == 1:
                print("[OHLCV] CREON connected", flush=True)
                self.connected = True
            else:
                print("[OHLCV] CREON not connected", flush=True)
        except Exception as e:
            print(f"[OHLCV] Error: {e}", flush=True)

    def get_data(self, code, days=500):
        if not self.connected:
            return pd.DataFrame()
        obj = win32com.client.Dispatch("CpSysDib.StockChart")
        _rate_limit()
        obj.SetInputValue(0, "A" + code)
        obj.SetInputValue(1, ord('2'))
        obj.SetInputValue(4, days)
        obj.SetInputValue(5, (0, 2, 3, 4, 5, 8, 9))
        obj.SetInputValue(6, ord('D'))
        obj.SetInputValue(9, ord('1'))
        obj.BlockRequest()
        status = obj.GetDibStatus()
        print(f"status: {status}", flush=True)
        count = obj.GetHeaderValue(3)
        print(f"count: {count}", flush=True)
        if count == 0:
            return pd.DataFrame()
        rows = []
        for i in range(count):
            rows.append([
                obj.GetDataValue(0, i),
                obj.GetDataValue(1, i),
                obj.GetDataValue(2, i),
                obj.GetDataValue(3, i),
                obj.GetDataValue(4, i),
                obj.GetDataValue(5, i),
                obj.GetDataValue(6, i)
            ])
        df = pd.DataFrame(rows, columns=["date","open","high","low","close","volume","amount"])
        df = df.iloc[::-1].reset_index(drop=True)
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df["code"] = code
        df["range"] = df["high"] - df["low"]
        df["gap"] = df["open"] - df["close"].shift(1)
        df["gap"] = df["gap"].fillna(0).astype(int)
        print(f"[OHLCV] {code} done -> {len(df)} days", flush=True)
        return df

if __name__ == "__main__":
    api = CreonOHLCV()
    if api.connected:
        df = api.get_data("005930", 100)
        print(df.tail(), flush=True)