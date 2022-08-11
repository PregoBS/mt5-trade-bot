from pandas import DataFrame
from signals.signal import Signal, SignalObj
from typing import List


class Manager:
    def __init__(self) -> None:
        self.signals: List[Signal] = []
        self.results: List[SignalObj] = []

    def add(self, signal: Signal) -> None:
        return self.signals.append(signal)

    def get_results(self, symbol: str, timeframe: str, dataframe: DataFrame) -> List[SignalObj]:
        for signal in self.signals:
            self.results.append(signal.get_signal(symbol, timeframe, dataframe))
        return self.results
