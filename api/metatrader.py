from api.market_data_api import MarketDataAPI
from datetime import datetime, timedelta
from dotenv import load_dotenv
from enum import Enum
import MetaTrader5 as mt5
import numpy as np
import pandas as pd
import os


load_dotenv()


class TimeFrame(Enum):
    M1 = mt5.TIMEFRAME_M1
    M5 = mt5.TIMEFRAME_M5
    M15 = mt5.TIMEFRAME_M15
    H1 = mt5.TIMEFRAME_H1
    H4 = mt5.TIMEFRAME_H4
    D1 = mt5.TIMEFRAME_D1
    W1 = mt5.TIMEFRAME_W1
    MN1 = mt5.TIMEFRAME_MN1


class MetaTrader5API(MarketDataAPI):
    def connect(self) -> bool:
        """MT5 connection"""
        kwargs = dict(
            path=os.getenv("MT5_PATH") or "",
            login=int(os.getenv("MT5_LOGIN")) or 0,
            server=os.getenv("MT5_SERVER") or "",
            password=os.getenv("MT5_PASSWORD") or "",
        )
        if not mt5.initialize(**kwargs):
            print(f"MT5 Initialize Failed, error code = {mt5.last_error()}")
            return False
        else:
            return True

    def shutdown(self) -> bool:
        """MT5 connection shutdown"""
        return mt5.shutdown()

    def create_dataframe_from_bars(self, symbol: str, timeframe: TimeFrame, start_position: int,
                                   bars: int) -> pd.DataFrame or None:
        dataframe = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timeframe.value, start_position, bars))
        if not dataframe.empty:
            return self._standardize_dataframe(dataframe, symbol)
        return None

    def create_dataframe_from_date(self, symbol: str, timeframe: TimeFrame, start_date: datetime,
                                   end_date: datetime) -> pd.DataFrame or None:
        dataframe = pd.DataFrame(mt5.copy_rates_range(symbol, timeframe.value, start_date, end_date))
        if not dataframe.empty:
            return self._standardize_dataframe(dataframe, symbol)
        return None

    def _standardize_dataframe(self, dataframe: pd.DataFrame, symbol: str) -> pd.DataFrame:
        dataframe["time"] = pd.to_datetime(dataframe["time"], unit="s")
        dataframe["time"] = dataframe["time"] + timedelta(hours=self.delta_timezone)
        dataframe.rename(columns={"time": "Date"}, inplace=True)
        dataframe.set_index(dataframe["Date"], inplace=True)
        dataframe.rename(columns={"open": "Open",
                                  "high": "High",
                                  "low": "Low",
                                  "close": "Close",
                                  "tick_volume": "Trades",
                                  "real_volume": "Volume",
                                  "spread": "Spread"}, inplace=True)
        dataframe = dataframe.astype({
            "Open": np.float64,
            "High": np.float64,
            "Low": np.float64,
            "Close": np.float64,
            "Volume": np.int64,
            "Trades": np.int64,
            "Spread": np.int64
        })
        digits = mt5.symbol_info(symbol).digits
        dataframe['Close'] = round(dataframe['Close'], digits)
        del dataframe["Date"]
        return dataframe
