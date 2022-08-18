from broker_account import BrokerAccount
from database import Database
from dataclasses import dataclass
from datetime import date
from design_patterns.observer_pattern import Observer, Subject
import pandas as pd
from strategies import StrategyState


@dataclass
class AccountRiskSettings:
    capital: float
    day_goal: float = 0.0
    day_stop: float = 0.0
    op_per_day: int = 0


class AccountRiskManager(Observer, Subject):
    def __init__(self, db: Database, account: BrokerAccount) -> None:
        super().__init__()
        self._db = db
        self._acc = account
        self._state: StrategyState or None = None
        self._settings: AccountRiskSettings or None = None

    @property
    def risk_settings(self) -> AccountRiskSettings:
        return self._settings

    @risk_settings.setter
    def risk_settings(self, settings: AccountRiskSettings) -> None:
        self._settings = settings

    def update(self, state: StrategyState) -> None:
        print(f"ACCOUNT RISK: Updating")
        if not self._can_open_trade(state):
            return None
        self._state = state
        return self.notify()

    def notify(self) -> None:
        if self._state is None:
            return None

        for ob in self.observers:
            ob.update(self._state)
        return None

    def _can_open_trade(self, state: StrategyState) -> bool:
        orders = self._get_db_orders(state.symbol, state.timeframe, state.strategy)
        positions = self._get_db_positions(state.symbol, state.timeframe, state.strategy)
        trades = self._get_db_trades()
        day_profit = trades["profit"].sum()

        if not state.settings.can_open_multiple_positions and (len(positions) + len(orders)) > 0:
            print("Já tem uma ordem ou posição aberta para esta estrategia")
            print("Não vamos seguir")
            return False

        if state.settings.can_open_multiple_positions:
            current_volume = 0
            for i in range(len(positions)):
                current_volume += positions["volume"].iloc[i]
            for i in range(len(orders)):
                current_volume += orders["volume"].iloc[i]

            if current_volume >= state.settings.max_volume:
                print("Já tem posições abertas ou ordens suficientes para esta estrategia")
                print("Não vamos seguir")
                return False

        if 0 < self.risk_settings.op_per_day <= len(trades) + len(positions):
            print("Já foram feitos trades demais por hoje")
            print("Não vamos seguir")
            return False

        if 0 < self.risk_settings.day_goal <= abs(day_profit):
            print("Já atingiu a meta ou stop de hoje")
            print("Não vamos seguir")
            return False

        return True

    def _get_db_trades(self) -> pd.DataFrame:
        trades = self._db.get_table("Trades")
        trades['open_time'] = pd.to_datetime(trades['open_time'], format="%Y-%m-%d %H:%M:%S")
        trades['open_day'] = [date(trade.year, trade.month, trade.day) for trade in trades['open_time'].to_list()]
        return trades[trades['open_day'] == date.today()]

    def _get_db_orders(self, symbol: str, timeframe: str, strategy: str) -> pd.DataFrame:
        orders = self._db.get_table("Orders")
        order_filter = ((orders["symbol"] == symbol) &
                        (orders["timeframe"] == timeframe) &
                        (orders["strategy"] == strategy))
        return orders[order_filter]

    def _get_db_positions(self, symbol: str, timeframe: str, strategy: str) -> pd.DataFrame:
        positions = self._db.get_table("Positions")
        position_filter = ((positions["symbol"] == symbol) &
                           (positions["timeframe"] == timeframe) &
                           (positions["strategy"] == strategy))
        return positions[position_filter]

