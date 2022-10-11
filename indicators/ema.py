from __future__ import annotations
from indicators.indicator import Indicator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


class EMA(Indicator):
    def __init__(self, name: str, period: int) -> None:
        Indicator.__init__(self, name)
        self.period = period

    def calculate(self, dataframe: DataFrame) -> DataFrame:
        return self._ema(dataframe)

    def _ema(self, dataframe: DataFrame) -> DataFrame:
        dataframe[self.name] = dataframe["Close"].ewm(span=self.period, min_periods=self.period).mean()
        dataframe = dataframe.fillna(method="bfill")
        return dataframe
