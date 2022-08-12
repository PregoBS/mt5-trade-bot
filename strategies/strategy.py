from abc import abstractmethod
from dataclasses import dataclass
from design_patterns.observer_pattern import Subject, Observer
from pandas import DataFrame
from signals.signal import SignalObj
from typing import List


@dataclass
class Order:
    type: str  # PENDING or AT_MARKET
    price: float
    spread: float
    digits: int
    stop_loss: float = 0.0
    stop_gain: float = 0.0


@dataclass
class State:
    strategy: str
    symbol: str
    timeframe: str
    order: Order
    is_buy: bool = False
    is_sell: bool = False


class Strategy(Subject):
    def __init__(self, name: str) -> None:
        Subject.__init__(self)
        self.name = name
        self._state: State or None = None
        self._is_buy: bool = False
        self._is_sell: bool = False

    def subscribe(self, ob: Observer) -> None:
        return self.observers.append(ob)

    def unsubscribe(self, ob: Observer) -> None:
        return self.observers.remove(ob)

    def notify(self) -> None:
        if self._state is None:
            return None
        for ob in self.observers:
            ob.update(self._state)
        return None

    def _get_specific_signal(self, name: str, symbol: str, timeframe: str, signals: List[SignalObj]) -> SignalObj or None:
        for signal in signals:
            if signal.name == name and signal.symbol == symbol and signal.timeframe == timeframe:
                return signal
        return None

    @abstractmethod
    def verify(self, symbol: str, timeframe: str, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        pass

    @abstractmethod
    def _check_signals(self, symbol: str, timeframe: str, signals: List[SignalObj]) -> None:
        pass

    @abstractmethod
    def _change_state(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        pass
