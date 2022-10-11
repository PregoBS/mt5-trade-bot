from __future__ import annotations
from dataclasses import dataclass
from design_patterns.observer_pattern import Observer
from datetime import datetime
from shared_data_structures import WaitToCheckAgainState
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from strategies import Strategy


@dataclass
class SymbolStrategyConfig:
    timeframe: str
    capital: float
    day_goal: float
    day_stop: float
    op_per_day: int
    op_goal: float
    op_stop: float
    wait_to_check: int
    last_check: datetime = datetime(2022, 1, 1)


class SymbolStrategyInfo:
    def __init__(self, symbol: str, strategy: Strategy, configs: List[SymbolStrategyConfig]) -> None:
        self.symbol = symbol
        self.strategy = strategy
        self.configs = configs

    def update(self, state) -> None:
        if isinstance(state, WaitToCheckAgainState):
            if state.symbol != self.symbol or state.strategy != self.strategy.name:
                return None
            for config in self.configs:
                if config.timeframe == state.timeframe:
                    config.last_check = datetime.today()
                    print(f"Updating SYMBOL STRATEGY INFO Last Check --- {self.symbol}")


class SymbolsInfo(Observer):
    def __init__(self) -> None:
        Observer.__init__(self)
        self.symbols: List[str] = []
        self.strategies: List[Strategy] = []
        self.info: dict = {}

    def add(self, info: SymbolStrategyInfo) -> None:
        if info.strategy not in self.strategies:
            self.strategies.append(info.strategy)
        if info.symbol not in self.symbols:
            self.symbols.append(info.symbol)
            self.info[info.symbol] = []

        self.info[info.symbol].append(info)
        return None

    def update(self, state) -> None:
        for symbol in self.info.keys():
            for info in self.info[symbol]:
                info.update(state)
