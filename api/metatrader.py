from api.market_data_api import MarketDataAPI
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import numpy as np
import pandas as pd


class MetaTrader5API(MarketDataAPI):
    def create_dataframe_from_bars(self, symbol: str, timeframe: str, start_position: int, bars: int) -> pd.DataFrame or None:
        tf = self._switch_timeframe(timeframe)
        if tf is not None:
            dataframe = pd.DataFrame(mt5.copy_rates_from_pos(symbol, tf, start_position, bars))
            if not dataframe.empty:
                return self._standardize_dataframe(dataframe, symbol)
        return None

    def create_dataframe_from_date(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> pd.DataFrame or None:
        tf = self._switch_timeframe(timeframe)
        if tf is not None:
            dataframe = pd.DataFrame(mt5.copy_rates_range(symbol, tf, start_date, end_date))
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

    def _switch_timeframe(self, timeframe: str) -> str or int or None:
        switcher = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }
        return switcher.get(timeframe, None)
