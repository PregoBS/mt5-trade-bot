from __future__ import annotations
from indicators.indicator import Indicator
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


class ATR(Indicator):
    def __init__(self, name: str, period: int) -> None:
        Indicator.__init__(self, name)
        self.period = period

    def calculate(self, dataframe: DataFrame) -> DataFrame:
        return self._atr(dataframe)

    def _atr(self, dataframe: DataFrame) -> DataFrame:
        dataframe[self.name] = self._atr_values(dataframe, self.period)
        return dataframe

    def _average_true_range(self, data: DataFrame, period: int) -> list:
        high = data["High"].to_list()
        low = data["Low"].to_list()
        close = data["Close"].to_list()
        tr = data["TR"].to_list()
        atr = data["TR"].rolling(period).mean().to_list()
        atr_values = []
        for i in range(len(data)):
            if i < period:
                atr_values.append(0)
            elif i == period:
                atr_values.append(atr[i])
            else:
                tr[i] = max(high[i], close[i - 1]) - min(low[i], close[i - 1])
                atr_value = atr_values[i-1] + ((tr[i] - tr[i - period]) / period)
                atr_values.append(atr_value)
        return atr_values

    def _atr_values(self, data: DataFrame, period: int) -> list:
        df = data[['High', 'Low', 'Close']].copy()
        df["Closeshift"] = df["Close"].shift(1)
        df["Highshift"] = df["High"].shift(1)
        df["Lowshift"] = df["Low"].shift(1)
        df["TRmax"] = np.where(df["Close"] >= df["Highshift"], df["Close"], df["Highshift"])
        df["TRmin"] = np.where(df["Close"] <= df["Lowshift"], df["Close"], df["Lowshift"])
        df["TR"] = df["TRmax"] - df["TRmin"]
        df["ATR"] = self._average_true_range(df, period)
        return df["ATR"].to_list()
