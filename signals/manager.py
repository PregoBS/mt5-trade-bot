from pandas import DataFrame
from signals.signal import Signal, SignalObj
from typing import List


class Manager:
    def __init__(self) -> None:
        self.signals: List[Signal] = []

    def get_results(self, symbol: str, timeframe: str, dataframe: DataFrame) -> dict:
        results = {}  # { "signal_name": SignalObj ... }
        for signal in self.signals:
            signal_obj: SignalObj = signal.get_signal(symbol, timeframe, dataframe)
            results[signal_obj.name] = signal_obj
        return results

    def add(self, signal: Signal) -> None:
        return self.signals.append(signal)
