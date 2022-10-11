from __future__ import annotations
from abc import abstractmethod
from design_patterns.observer_pattern import Subject
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from api import Attributes, MarketDataAPI, Position
    from pandas import DataFrame
    from risk_management import TradeRiskManager
    from shared_data_structures import StrategyState, StrategySettings
    from signals import SignalObj


class Strategy(Subject):
    def __init__(self, name: str, magic_number: int) -> None:
        super().__init__()
        self.name = name
        self.magic = magic_number
        self._is_to_protect_position: List[bool] = []
        self._is_to_close_position: List[bool] = []
        self._state: StrategyState or None = None
        self._settings: StrategySettings or None = None

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
    def check_new_position(self, symbol: str, timeframe: str, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        pass

    @abstractmethod
    def check_protect(self, position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager) -> None:
        pass

    @abstractmethod
    def check_close(self,  position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager) -> None:
        pass

    @abstractmethod
    def _check_signals(self, symbol: str, timeframe: str, signals: List[SignalObj]) -> None:
        pass

    @abstractmethod
    def _change_state_new_position(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        pass

    @abstractmethod
    def _change_state_protect(self, position: Position, symbol_attributes: Attributes) -> None:
        pass

    @abstractmethod
    def _change_state_close(self, position: Position, symbol_attributes: Attributes) -> None:
        pass
