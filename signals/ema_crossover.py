from __future__ import annotations
from signals.signal import Signal, SignalObj
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import TimeFrames
    from pandas import DataFrame


class EMACrossover(Signal):
    def __init__(self, name: str, ema_crossover_indicator_name: str, shift: int = 0) -> None:
        Signal.__init__(self, name)
        self.indicator_name = ema_crossover_indicator_name
        self.shift = shift

    def get_signal(self, symbol: str, timeframe: TimeFrames, dataframe: DataFrame) -> SignalObj:
        return self._ema_crossover(symbol, timeframe, dataframe, self.shift)

    def _ema_crossover(self, symbol: str, timeframe: TimeFrames, dataframe: DataFrame, shift) -> SignalObj:
        signal = dataframe[self.indicator_name].iloc[-(shift+1)]
        return SignalObj(
            name=self.name,
            symbol=symbol,
            timeframe=timeframe.value,
            value=signal
        )
