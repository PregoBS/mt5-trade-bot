from indicators.indicator import Indicator
from pandas import DataFrame
from typing import List


class Manager:
    def __init__(self) -> None:
        self.indicators: List[Indicator] = []

    def add(self, indicator: Indicator) -> None:
        return self.indicators.append(indicator)

    def calculate_all(self, dataframe: DataFrame) -> DataFrame:
        for indicator in self.indicators:
            dataframe = indicator.calculate(dataframe)
        return dataframe
