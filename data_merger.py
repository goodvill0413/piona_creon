# data_merger.py — 12컬럼 통합 수집기 (Margin 제외)
import win32com.client
import pythoncom
import time
import pandas as pd

print("START merger", flush=True)

_last_request = 0.0

def _rate_limit():
    global _last_request
    now = time.time()
    elapsed = now - _last_request
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    _last_request = time.time()


class CreonOHLCV:
    """OHLCV 데이터 수집"""
    def __init__(self):
        self.connected = False
        self._connect()

    def _connect(self):
        try:
            pythoncom.CoInitialize()
            cp = win32com.client.Dispatch("CpUtil.CpCybos")
            if cp.IsConnect == 1:
                self.connected = True
            else:
                print("[OHLCV] CREON not connected", flush=True)
        except Exception as e:
            print(f"[OHLCV] Error: {e}", flush=True)

    def get_data(self, code, days=100):
        if not self.connected:
            return pd.DataFrame()
        obj = win32com.client.Dispatch("CpSysDib.StockChart")
        _rate_limit()
        # 지수는 U로 시작, 종목은 A 붙임
        if code.startswith("U"):
            full_code = code  # U001, U201 그대로
        else:
            full_code = "A" + code
        obj.SetInputValue(0, full_code)
        obj.SetInputValue(1, ord('2'))
        obj.SetInputValue(4, days)
        obj.SetInputValue(5, (0, 2, 3, 4, 5, 8, 9))
        obj.SetInputValue(6, ord('D'))
        obj.SetInputValue(9, ord('1'))
        obj.BlockRequest()
        count = obj.GetHeaderValue(3)
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
        return df


class CreonSupply:
    """투자자별 매매동향 수집"""
    def __init__(self):
        self.connected = False
        self._connect()

    def _connect(self):
        try:
            pythoncom.CoInitialize()
            cp = win32com.client.Dispatch("CpUtil.CpCybos")
            if cp.IsConnect == 1:
                self.connected = True
        except Exception as e:
            print(f"[Supply] Connection error: {e}", flush=True)

    def get_investor(self, code, days=100):
        if not self.connected:
            return pd.DataFrame()
        try:
            obj = win32com.client.Dispatch("CpSysDib.CpSvr7254")
            _rate_limit()
            obj.SetInputValue(0, "A" + code)
            obj.SetInputValue(1, 6)  # 일별
            obj.SetInputValue(2, days)
            obj.SetInputValue(3, 0)  # 순매수
            obj.BlockRequest()
            count = obj.GetHeaderValue(1)
            if count == 0:
                return pd.DataFrame()
            rows = []
            for i in range(count):
                rows.append({
                    "date": obj.GetDataValue(0, i),
                    "frgn_net_buy": obj.GetDataValue(2, i),
                    "inst_net_buy": obj.GetDataValue(1, i),
                })
            df = pd.DataFrame(rows)
            df = df.iloc[::-1].reset_index(drop=True)
            df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
            return df
        except Exception as e:
            print(f"[Supply] Error getting investor data: {e}", flush=True)
            return pd.DataFrame()


class DataMerger:
    """OHLCV + Supply 통합 (12컬럼)"""
    def __init__(self):
        print("[Merger] Initializing...", flush=True)
        self.ohlcv = CreonOHLCV()
        self.supply = CreonSupply()
        if self.ohlcv.connected:
            print("[Merger] CREON connected", flush=True)
        else:
            print("[Merger] CREON not connected!", flush=True)

    def get_full_data(self, code, days=100):
        """12컬럼 통합 데이터 반환"""
        # 1) OHLCV (기본)
        try:
            df = self.ohlcv.get_data(code, days)
        except Exception as e:
            print(f"[Merger] {code} OHLCV 오류: {e}", flush=True)
            return pd.DataFrame()
        if df.empty:
            print(f"[Merger] {code} OHLCV 실패", flush=True)
            return pd.DataFrame()

        # 2) Investor (외인/기관) - 지수는 스킵
        if not code.startswith("U"):
            try:
                inv_df = self.supply.get_investor(code, days)
                if not inv_df.empty:
                    df = pd.merge(df, inv_df, on="date", how="left")
                else:
                    df["frgn_net_buy"] = None
                    df["inst_net_buy"] = None
            except Exception as e:
                print(f"  [Investor 실패: {e}]", flush=True)
                df["frgn_net_buy"] = None
                df["inst_net_buy"] = None
        else:
            # 지수는 투자자 데이터 없음
            df["frgn_net_buy"] = None
            df["inst_net_buy"] = None

        # 컬럼 순서 정리 (12개)
        cols = ["date", "code", "open", "high", "low", "close", "volume", "amount",
                "range", "gap", "frgn_net_buy", "inst_net_buy"]
        for c in cols:
            if c not in df.columns:
                df[c] = None
        df = df[cols]

        print(f"[Merger] {code} 완료 → {len(df)}일, {len(df.columns)}컬럼", flush=True)
        return df


if __name__ == "__main__":
    merger = DataMerger()
    df = merger.get_full_data("005930", 10)
    if not df.empty:
        print(df.tail())
        print(f"컬럼 ({len(df.columns)}개): {list(df.columns)}")
