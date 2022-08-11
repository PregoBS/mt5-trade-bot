from pandas import DataFrame
from signals.signal import Signal, SignalObj


class EMACrossover(Signal):
    def __init__(self, name: str, fast_ema_period: int, slow_ema_period: int) -> None:
        Signal.__init__(self, name)
        self.fast = fast_ema_period
        self.slow = slow_ema_period

    def get_signal(self, symbol: str, timeframe: str, dataframe: DataFrame) -> SignalObj:
        return self._ema_crossover(symbol, timeframe, dataframe)

    def _ema_crossover(self, symbol: str, timeframe: str, dataframe: DataFrame) -> SignalObj:
        signal = dataframe["EMACrossover17_34"].iloc[-1]
        return SignalObj(
            name=self.name,
            symbol=symbol,
            timeframe=timeframe,
            signal=signal
        )
