from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
from design_patterns.observer_pattern import Subject
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from api import MarketDataAPI, Position, TimeFrames
    from pandas import DataFrame
    from risk_management import TradeRiskManager
    from shared_data_structures import StrategyState, StrategySettings
    from signals import SignalObj


@dataclass
class ProtectState:
    pass


@dataclass
class CloseState:
    pass


class Strategy(Subject):
    def __init__(self, name: str, magic_number: int) -> None:
        super().__init__()
        self.name = name
        self.magic = magic_number
        self._is_buy = False
        self._is_sell = False
        self._is_to_protect_position: List[bool] = []
        self._is_to_close_position: List[bool] = []
        self._state: StrategyState or None = None
        self._protect_state: ProtectState or None = None
        self._close_state: CloseState or None = None
        self._settings: StrategySettings or None = None

    def _notify(self) -> None:
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

    def set_strategy_settings(self, settings: StrategySettings) -> None:
        self._settings = settings

    def _reset_state(self) -> None:
        self._is_buy = False
        self._is_sell = False
        self._is_to_protect_position.clear()
        self._is_to_close_position.clear()
        self._state = None

    @abstractmethod
    def check_new_position(self, symbol: str, timeframe: TimeFrames, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        pass

    @abstractmethod
    def check_protect(self, position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager, dataframe: DataFrame) -> None:
        pass

    @abstractmethod
    def check_close(self,  position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager, dataframe: DataFrame) -> None:
        pass
