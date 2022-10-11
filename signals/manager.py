from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame
    from signals import Signal, SignalObj


class Manager:
    def __init__(self) -> None:
        self.signals: List[Signal] = []
        self.results: List[SignalObj] = []

    def add(self, signal: Signal) -> None:
        return self.signals.append(signal)

    def clear(self) -> None:
        self.signals.clear()
        self.results.clear()

    def compute_signals(self, symbol: str, timeframe: str, dataframe: DataFrame) -> List[SignalObj]:
        for signal in self.signals:
            self.results.append(signal.get_signal(symbol, timeframe, dataframe))
        return self.results
