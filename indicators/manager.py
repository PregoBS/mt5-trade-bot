from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from indicators import Indicator
    from pandas import DataFrame


class Manager:
    def __init__(self) -> None:
        self._indicators: List[Indicator] = []

    def add(self, indicator: Indicator) -> None:
        return self._indicators.append(indicator)

    def clear(self) -> None:
        self._indicators.clear()

    def compute_all(self, dataframe: DataFrame) -> DataFrame:
        for indicator in self._indicators:
            dataframe = indicator.calculate(dataframe)
        return dataframe
