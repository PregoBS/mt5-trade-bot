from pandas import DataFrame
from strategies.strategy import Strategy, StrategyState, StrategyOrder, StrategySettings
from signals.signal import SignalObj
from typing import List


class EMACrossover(Strategy):
    def __init__(self, name: str, magic_number: int) -> None:
        super().__init__(name, magic_number)
        self._set_strategy_settings(StrategySettings(max_volume=0,
                                                     can_open_multiple_positions=False))

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
        price_open = dataframe["Close"].iloc[-1]
        spread = dataframe["Spread"].iloc[-1]
        stop_loss = dataframe["Close"].iloc[-1] * 0.99
        digits = dataframe["_Digits"].iloc[-1]
        self._set_state(symbol, timeframe, price_open, spread, stop_loss, digits, is_buy=True)
        return None

    def _set_sell_state(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        price_open = dataframe["Close"].iloc[-1]
        spread = dataframe["Spread"].iloc[-1]
        stop_loss = dataframe["Close"].iloc[-1] * 1.01
        digits = dataframe["_Digits"].iloc[-1]
        self._set_state(symbol, timeframe, price_open, spread, stop_loss, digits, is_sell=True)
        return None

    def _set_state(self, symbol: str, timeframe: str, price_open: float, spread: float, stop_loss: float, digits: int,
                   is_buy: bool = False, is_sell: bool = False) -> None:
        order = StrategyOrder(type="AT_MARKET",
                              price=price_open,
                              volume=0,
                              spread=spread,
                              digits=digits,
                              stop_loss=stop_loss,
                              stop_gain=0.0)
        self._state = StrategyState(strategy=self.name,
                                    symbol=symbol,
                                    timeframe=timeframe,
                                    order=order,
                                    settings=self._settings,
                                    magic=self.magic,
                                    is_buy=is_buy,
                                    is_sell=is_sell)
