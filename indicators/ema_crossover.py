from __future__ import annotations
import numpy as np
from indicators.indicator import Indicator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


class EMACrossover(Indicator):
    def __init__(self, name: str, fast_period: int, slow_period: int) -> None:
        Indicator.__init__(self, name)
        self.fast = fast_period
        self.slow = slow_period

    def calculate(self, dataframe: DataFrame) -> DataFrame:
        return self._ema_crossover(dataframe)

    def _ema_crossover(self, dataframe: DataFrame) -> DataFrame:
        try:
            dataframe[f"EMA{self.fast}_Shift"] = dataframe[f"EMA{self.fast}"].shift()
            dataframe[f"EMA{self.slow}_Shift"] = dataframe[f"EMA{self.slow}"].shift()
        except KeyError:
            print("Indicator not in dataframe, first compute the Fast and Slow EMA's")
            raise KeyError

        condition1_up = dataframe[f"EMA{self.fast}"].to_numpy() > dataframe[f"EMA{self.slow}"].to_numpy()
        condition2_up = dataframe[f"EMA{self.fast}_Shift"].to_numpy() < dataframe[f"EMA{self.slow}_Shift"].to_numpy()
        cross_up = np.logical_and(condition1_up, condition2_up)

        condition1_down = dataframe[f"EMA{self.fast}"].to_numpy() < dataframe[f"EMA{self.slow}"].to_numpy()
        condition2_down = dataframe[f"EMA{self.fast}_Shift"].to_numpy() > dataframe[f"EMA{self.slow}_Shift"].to_numpy()
        cross_down = np.logical_and(condition1_down, condition2_down)

        dataframe[self.name] = np.where(cross_up, 1, np.where(cross_down, -1, 0))

        del dataframe[f"EMA{self.fast}_Shift"]
        del dataframe[f"EMA{self.slow}_Shift"]
        return dataframe
