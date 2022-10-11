from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from api import MarketDataAPI, Position
    from design_patterns.observer_pattern import Observer
    from pandas import DataFrame
    from risk_management import TradeRiskManager
    from signals import SignalObj
    from strategies import Strategy


class Manager:
    def __init__(self) -> None:
        self.strategies: List[Strategy] = []

    def add(self, strategy: Strategy) -> None:
        return self.strategies.append(strategy)

    def clear(self) -> None:
        self.strategies.clear()

    def subscribe(self, observer: Observer) -> None:
        for strategy in self.strategies:
            strategy.subscribe(observer)
        return None

    def check_for_new_position(self, symbol: str, timeframe: str, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        for strategy in self.strategies:
            strategy.check_new_position(symbol, timeframe, dataframe, signals)

    def check_for_protect(self, position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager) -> None:
        for strategy in self.strategies:
            if strategy.magic != position.magic:
                continue
            strategy.check_protect(position, api, trade_risk)

    def check_for_close(self, position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager) -> None:
        for strategy in self.strategies:
            if strategy.magic != position.magic:
                continue
            strategy.check_close(position, api, trade_risk)
