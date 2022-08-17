from abc import abstractmethod
from dataclasses import dataclass
from design_patterns.observer_pattern import Subject, Observer
from pandas import DataFrame
from signals.signal import SignalObj
from typing import List


@dataclass
class StrategyOrder:
    type: str  # PENDING or AT_MARKET
    price: float
    volume: float
    spread: float
    digits: int
    stop_loss: float = 0.0
    stop_gain: float = 0.0


@dataclass
class StrategySettings:
    can_open_multiple_positions: bool
    max_volume: float


@dataclass
class StrategyState:
    strategy: str
    symbol: str
    timeframe: str
    order: StrategyOrder
    settings: StrategySettings
    magic: int = 0
    is_buy: bool = False
    is_sell: bool = False


class Strategy(Subject):
    def __init__(self, name: str, magic_number: int) -> None:
        super().__init__()
        self.name = name
        self.magic = magic_number
        self._state: StrategyState or None = None
        self._settings: StrategySettings or None = None
        self._is_buy: bool = False
        self._is_sell: bool = False

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

    def _set_strategy_settings(self, settings: StrategySettings) -> None:
        self._settings = settings

    @abstractmethod
    def verify(self, symbol: str, timeframe: str, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        pass

    @abstractmethod
    def _check_signals(self, symbol: str, timeframe: str, signals: List[SignalObj]) -> None:
        pass

    @abstractmethod
    def _change_state(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        pass
