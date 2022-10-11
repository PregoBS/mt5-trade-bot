from __future__ import annotations
from shared_data_structures.structures import StrategySettings, StrategyState, OrderType, OrderExecution
from strategies.strategy import Strategy
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from api import Attributes, MarketDataAPI, Position
    from pandas import DataFrame
    from risk_management import TradeRiskManager
    from signals import SignalObj


class EMACrossover(Strategy):
    def __init__(self, name: str, magic_number: int) -> None:
        super().__init__(name, magic_number)
        self._is_buy = False
        self._is_sell = False
        self._set_strategy_settings(StrategySettings(max_volume=1.0,
                                                     can_open_multiple_positions=False))

    def check_new_position(self, symbol: str, timeframe: str, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        self._state = None
        self._is_buy = False
        self._is_sell = False
        self._check_signals(symbol, timeframe, signals)
        self._change_state_new_position(symbol, timeframe, dataframe)
        self.notify()

    def _check_signals(self, symbol: str, timeframe: str, signals: List[SignalObj]) -> None:
        ema_crossover = self._get_specific_signal("EMACrossover", symbol, timeframe, signals)
        if ema_crossover.value == 1:
            self._is_buy = True
        if ema_crossover.value == -1:
            self._is_sell = True
        return None

    def _change_state_new_position(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        if self._is_buy:
            self._set_buy_state(symbol, timeframe, dataframe)
        if self._is_sell:
            self._set_sell_state(symbol, timeframe, dataframe)
        return None

    def _set_buy_state(self, symbol: str, timeframe: str, dataframe: DataFrame):
        action = OrderExecution.OPEN_POSITION
        order_type = OrderType.BUY
        price_open = dataframe["Close"].iloc[-1]
        spread = dataframe["Spread"].iloc[-1]
        digits = dataframe["_Digits"].iloc[-1]
        stop_loss = dataframe["Low"].iloc[-2] - dataframe["ATR20"].iloc[-1] * 0.5
        self._set_state(symbol, timeframe, action, order_type, price_open, spread, digits, stop_loss, 0.0, 0.0, 0.0, 0)
        return None

    def _set_sell_state(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        action = OrderExecution.OPEN_POSITION
        order_type = OrderType.SELL
        price_open = dataframe["Close"].iloc[-1]
        spread = dataframe["Spread"].iloc[-1]
        digits = dataframe["_Digits"].iloc[-1]
        stop_loss = dataframe["High"].iloc[-2] + dataframe["ATR20"].iloc[-1] * 0.5
        self._set_state(symbol, timeframe, action, order_type, price_open, spread, digits, stop_loss, 0.0, 0.0, 0.0, 0)
        return None

    def check_protect(self, position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager) -> None:
        symbol_attr = api.get_symbol_attributes(position.symbol)
        stop_loss = position.price_open
        if position.stop_loss == round(stop_loss, symbol_attr.digits):
            return None
        if not self._is_to_protect(position, trade_risk):
            return None
        self._change_state_protect(position, symbol_attr)
        self.notify()

    def _is_to_protect(self, position: Position, trade_risk: TradeRiskManager) -> bool:
        settings = trade_risk.risk_settings

        if position.magic != self.magic or position.timeframe != settings.timeframe:
            return False

        if position.profit >= settings.op_goal / 3:
            print(f"{position.symbol} - Lucro de {position.profit:.2f}, protegendo trade!")
            return True
        return False

    def _change_state_protect(self, position: Position, symbol_attributes: Attributes) -> None:
        # TODO Refactor this position type == 0 to use enum class in comparison
        if position.type == 0:
            order_type = OrderType.BUY
        else:
            order_type = OrderType.SELL

        symbol = symbol_attributes.symbol
        timeframe = "NA"
        action = OrderExecution.MODIFY_POSITION
        spread = symbol_attributes.spread
        digits = symbol_attributes.digits
        stop_loss = position.price_open
        ticket = position.ticket
        self._set_state(symbol, timeframe, action, order_type, 0.0, spread, digits, stop_loss, 0.0, 0.0, 0.0, ticket)
        return None

    def check_close(self, position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager) -> None:
        if not self._is_to_close(position, trade_risk):
            return None
        symbol_attr = api.get_symbol_attributes(position.symbol)
        self._change_state_close(position, symbol_attr)
        self.notify()

    def _is_to_close(self, position: Position, trade_risk: TradeRiskManager) -> bool:
        settings = trade_risk.risk_settings

        if position.magic != self.magic or position.timeframe != settings.timeframe:
            return False

        if position.profit >= settings.op_goal:
            print(f"{position.symbol} - check close: goal: ${settings.op_goal:.2f} | current profit: ${position.profit}")
            return True
        return False

    def _change_state_close(self, position: Position, symbol_attributes: Attributes) -> None:
        # TODO Refactor this position type == 0 to use enum class in comparison
        if position.type == 0:
            order_type = OrderType.BUY
        else:
            order_type = OrderType.SELL

        symbol = symbol_attributes.symbol
        timeframe = "NA"
        action = OrderExecution.CLOSE_POSITION
        spread = symbol_attributes.spread
        digits = symbol_attributes.digits
        ticket = position.ticket
        self._set_state(symbol, timeframe, action, order_type, 0.0, spread, digits, 0.0, 0.0, 0.0, 0.0, ticket)
        return None

    def _set_state(self, symbol: str, timeframe: str, action: OrderExecution, order_type: OrderType, price_open: float,
                   spread: float, digits: int, stop_loss: float, stop_gain: float, limit_price: float,
                   stop_limit: float, ticket: int) -> None:
        self._state = StrategyState(symbol=symbol,
                                    timeframe=timeframe,
                                    strategy=self.name,
                                    magic=self.magic,
                                    action=action,
                                    settings=self._settings,
                                    order_type=order_type,
                                    price=price_open,
                                    spread=spread,
                                    digits=digits,
                                    stop_loss=stop_loss,
                                    stop_gain=stop_gain,
                                    limit_price=limit_price,
                                    stop_limit=stop_limit,
                                    ticket=ticket)
