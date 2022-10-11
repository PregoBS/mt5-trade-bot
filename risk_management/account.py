from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from design_patterns.observer_pattern import Observer
import pandas as pd
from shared_data_structures import WaitToCheckAgainState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database import Database
    from pandas import DataFrame
    from risk_management import TradeRiskManager
    from shared_data_structures import StrategyState, OrderExecution
    from symbols_info import SymbolsInfo


@dataclass
class AccountRiskSettings:
    capital: float
    day_goal: float = 0.0
    day_stop: float = 0.0
    op_per_day: int = 0


class AccountRiskManager(Observer):
    def __init__(self, db: Database, trade_risk: TradeRiskManager, symbols_info: SymbolsInfo) -> None:
        self._trade_risk = trade_risk
        self._symbols_info = symbols_info
        self._comment = ""
        self._db = db
        self._settings: AccountRiskSettings or None = None

    @property
    def risk_settings(self) -> AccountRiskSettings:
        return self._settings

    @risk_settings.setter
    def risk_settings(self, settings: AccountRiskSettings) -> None:
        self._settings = settings

    def update(self, state: StrategyState) -> None:
        if self._is_new_trade(state.action):
            if not self._can_open_trade(state):
                print(f"ACCOUNT RISK: Updating --- COMMENT: {self._comment}")
                self._symbols_info.update(WaitToCheckAgainState(symbol=state.symbol,
                                                                timeframe=state.timeframe,
                                                                strategy=state.strategy))
                return None
        print(f"ACCOUNT RISK: Updating --- COMMENT: {self._comment}")
        self._trade_risk.update(state)
        return None

    def _is_new_trade(self, action: OrderExecution) -> bool:
        if "OPEN_POSITION" in action.value or "SEND_PENDING_ORDER" in action.value:
            return True
        self._comment = "Not a new Trade"
        return False

    def _can_open_trade(self, state: StrategyState) -> bool:
        orders = self._get_db_orders(state.symbol, state.timeframe, state.strategy)
        positions = self._get_db_positions(state.symbol, state.timeframe, state.strategy)
        trades = self._get_db_trades_of_today()
        today_profit = trades["profit"].sum()

        if not state.settings.can_open_multiple_positions and (len(positions) + len(orders)) > 0:
            self._comment = f"Cannot open multiple positions on {state.symbol}"
            return False

        if state.settings.can_open_multiple_positions:
            current_volume = 0
            for i in range(len(positions)):
                current_volume += positions["volume"].iloc[i]
            for i in range(len(orders)):
                current_volume += orders["volume"].iloc[i]

            if current_volume >= state.settings.max_volume:
                self._comment = f"Already have positions or pending orders enough on {state.symbol}"
                return False

        if 0 < self.risk_settings.op_per_day <= len(trades) + len(positions):
            self._comment = f"Too many trades for today on {state.symbol}"
            return False

        if 0 < self.risk_settings.day_goal <= abs(today_profit):
            self._comment = f"Hit the Stop Loss or the Stop Gain for today on {state.symbol}"
            return False
        self._comment = f"Allowed to open position on {state.symbol}"
        return True

    def _get_db_trades_of_today(self) -> DataFrame:
        trades = self._db.get_table("Trades")
        trades['open_time'] = pd.to_datetime(trades['open_time'], format="%Y-%m-%d %H:%M:%S")
        trades['open_day'] = [date(trade.year, trade.month, trade.day) for trade in trades['open_time'].to_list()]
        return trades[trades['open_day'] == date.today()]

    def _get_db_orders(self, symbol: str, timeframe: str, strategy: str) -> DataFrame:
        orders = self._db.get_table("Orders")
        order_filter = ((orders["symbol"] == symbol) &
                        (orders["timeframe"] == timeframe) &
                        (orders["strategy"] == strategy))
        return orders[order_filter]

    def _get_db_positions(self, symbol: str, timeframe: str, strategy: str) -> DataFrame:
        positions = self._db.get_table("Positions")
        position_filter = ((positions["symbol"] == symbol) &
                           (positions["timeframe"] == timeframe) &
                           (positions["strategy"] == strategy))
        return positions[position_filter]
