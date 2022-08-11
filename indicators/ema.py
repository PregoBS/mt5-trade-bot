from indicators.indicator import Indicator
import pandas as pd


class EMA(Indicator):
    def __init__(self, name: str, period: int) -> None:
        Indicator.__init__(self, name)
        self.period = period

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return self._ema(dataframe)

    def _ema(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe[self.name] = dataframe["Close"].ewm(span=self.period, min_periods=self.period).mean()
        dataframe = dataframe.fillna(method="bfill")
        return dataframe
