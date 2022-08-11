from pandas import DataFrame
from signals.signal import Signal, SignalObj


class EMACrossover(Signal):
    def __init__(self, name: str, ema_crossover_indicator_name: str) -> None:
        Signal.__init__(self, name)
        self.indicator_name = ema_crossover_indicator_name

    def get_signal(self, symbol: str, timeframe: str, dataframe: DataFrame) -> SignalObj:
        return self._ema_crossover(symbol, timeframe, dataframe)

    def _ema_crossover(self, symbol: str, timeframe: str, dataframe: DataFrame) -> SignalObj:
        signal = dataframe[self.indicator_name].iloc[-1]
        return SignalObj(
            name=self.name,
            symbol=symbol,
            timeframe=timeframe,
            signal=signal
        )
