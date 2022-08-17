from design_patterns.observer_pattern import Observer
from pandas import DataFrame
from signals.signal import SignalObj
from strategies.strategy import Strategy
from typing import List


class Manager:
    def __init__(self) -> None:
        self.strategies: List[Strategy] = []

    def add(self, strategy: Strategy) -> None:
        return self.strategies.append(strategy)

    def subscribe(self, observer: Observer) -> None:
        for strategy in self.strategies:
            strategy.subscribe(observer)
        return None

    def verify_all(self, symbol: str, timeframe: str, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        for strategy in self.strategies:
            strategy.verify(symbol, timeframe, dataframe, signals)
