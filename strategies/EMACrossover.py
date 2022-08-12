from pandas import DataFrame
from strategies.strategy import Strategy, State, Order
from signals.signal import SignalObj
from typing import List


class EMACrossover(Strategy):
    def verify(self, symbol: str, timeframe: str, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        self._check_signals(symbol, timeframe, signals)
        self._change_state(symbol, timeframe, dataframe)
        self.notify()
        return None

    def _check_signals(self, symbol: str, timeframe: str, signals: List[SignalObj]) -> None:
        ema_crossover = self._get_specific_signal("EMACrossover", symbol, timeframe, signals)
        if ema_crossover.value == 1:
            self._is_buy = True
        if ema_crossover.value == -1:
            self._is_sell = True
        return None

    def _change_state(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        if self._is_buy:
            self._set_buy_state(symbol, timeframe, dataframe)
        if self._is_sell:
            self._set_sell_state(symbol, timeframe, dataframe)
        return None

    def _set_buy_state(self, symbol: str, timeframe: str, dataframe: DataFrame):
        stop_loss = dataframe["Close"].iloc[-1] * 0.99
        order = Order(type="AT_MARKET",
                      price=0,
                      spread=dataframe["Spread"].iloc[-1],
                      digits=dataframe["_Digits"].iloc[-1],
                      stop_loss=stop_loss,
                      stop_gain=0.0)
        self._state = State(strategy=self.name, symbol=symbol, timeframe=timeframe, order=order, is_buy=True)
        return None

    def _set_sell_state(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        stop_loss = dataframe["Close"].iloc[-1] * 1.01
        order = Order(type="AT_MARKET",
                      price=dataframe["Close"].iloc[-1],
                      spread=dataframe["Spread"].iloc[-1],
                      digits=dataframe["_Digits"].iloc[-1],
                      stop_loss=stop_loss,
                      stop_gain=0.0)
        self._state = State(strategy=self.name, symbol=symbol, timeframe=timeframe, order=order, is_sell=True)
        return None
