from __future__ import annotations
from shared_data_structures.structures import StrategyState, OrderType, OrderExecution
from strategies.strategy import Strategy
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from api import Attributes, MarketDataAPI, Position, TimeFrames
    from pandas import DataFrame
    from risk_management import TradeRiskManager
    from signals import SignalObj


class EMACrossover(Strategy):
    def check_new_position(self, symbol: str, timeframe: TimeFrames, dataframe: DataFrame, signals: List[SignalObj]) -> None:
        self._reset_state()
        self._check_signals(symbol, timeframe.value, signals)
        self._change_state_new_position(symbol, timeframe.value, dataframe)
        self._notify()

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
        self._state = StrategyState(symbol=symbol,
                                    timeframe=timeframe,
                                    strategy=self.name,
                                    magic=self.magic,
                                    action=OrderExecution.OPEN_POSITION,
                                    settings=self._settings,
                                    order_type=OrderType.BUY,
                                    price=dataframe["Close"].iloc[-1],
                                    spread=dataframe["Spread"].iloc[-1],
                                    digits=dataframe["_Digits"].iloc[-1],
                                    stop_loss=dataframe["Low"].iloc[-2] - dataframe["ATR20"].iloc[-1] * 0.5,
                                    stop_gain=0.0,
                                    limit_price=0.0,
                                    stop_limit=0.0,
                                    ticket=0)

    def _set_sell_state(self, symbol: str, timeframe: str, dataframe: DataFrame) -> None:
        self._state = StrategyState(symbol=symbol,
                                    timeframe=timeframe,
                                    strategy=self.name,
                                    magic=self.magic,
                                    action=OrderExecution.OPEN_POSITION,
                                    settings=self._settings,
                                    order_type=OrderType.SELL,
                                    price=dataframe["Close"].iloc[-1],
                                    spread=dataframe["Spread"].iloc[-1],
                                    digits=dataframe["_Digits"].iloc[-1],
                                    stop_loss=dataframe["High"].iloc[-2] + dataframe["ATR20"].iloc[-1] * 0.5,
                                    stop_gain=0.0,
                                    limit_price=0.0,
                                    stop_limit=0.0,
                                    ticket=0)

    def check_protect(self, position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager, dataframe: DataFrame) -> None:
        self._reset_state()
        symbol_attr = api.get_symbol_attributes(position.symbol)
        stop_loss = position.price_open
        if position.stop_loss == round(stop_loss, symbol_attr.digits):
            return None
        if not self._is_to_protect(position, trade_risk):
            return None
        self._change_state_protect(position, symbol_attr)
        self._notify()

    def _is_to_protect(self, position: Position, trade_risk: TradeRiskManager) -> bool:
        settings = trade_risk.risk_settings

        if not self._is_the_right_position(position):
            return False

        # BELOW ALL CONDITIONS TO PROTECT THE POSITION
        # THE ORDER MATTERS. THE LAST TRUE CONDITION WILL BE STORED AS PROTECT_STATE
        if position.profit >= settings.op_goal / 3:
            print(f"{position.symbol} - Lucro de {position.profit:.2f}, protegendo trade!")
            return True

        return False

    def _protection_01(self) -> None:
        pass

    def _change_state_protect(self, position: Position, symbol_attributes: Attributes) -> None:
        self._state = StrategyState(symbol=symbol_attributes.symbol,
                                    timeframe="NA",
                                    strategy=self.name,
                                    magic=self.magic,
                                    action=OrderExecution.MODIFY_POSITION,
                                    settings=self._settings,
                                    order_type=position.type,
                                    price=0.0,
                                    spread=symbol_attributes.spread,
                                    digits=symbol_attributes.digits,
                                    stop_loss=position.price_open,
                                    stop_gain=0.0,
                                    limit_price=0.0,
                                    stop_limit=0.0,
                                    ticket=position.ticket)
        return None

    def check_close(self, position: Position, api: MarketDataAPI, trade_risk: TradeRiskManager, dataframe: DataFrame) -> None:
        self._reset_state()
        if not self._is_to_close(position, trade_risk):
            return None
        symbol_attr = api.get_symbol_attributes(position.symbol)
        self._change_state_close(position, symbol_attr)
        self._notify()

    def _is_to_close(self, position: Position, trade_risk: TradeRiskManager) -> bool:
        settings = trade_risk.risk_settings

        if not self._is_the_right_position(position):
            return False

        # BELOW ALL THE CONDITIONS TO CLOSE THE CURRENT POSITION
        # THE ORDER DOES NOT MATTER. THE FIRST TRUE CONDITION WILL CLOSE THE POSITION
        if position.profit >= settings.op_goal:
            print(f"{position.symbol} - check close: goal: ${settings.op_goal:.2f} | current profit: ${position.profit}")
            return True

        return False

    def _is_the_right_position(self, position: Position) -> bool:
        return position.magic == self.magic and position.timeframe == self._settings.timeframe

    def _change_state_close(self, position: Position, symbol_attributes: Attributes) -> None:
        self._state = StrategyState(symbol=symbol_attributes.symbol,
                                    timeframe="NA",
                                    strategy=self.name,
                                    magic=self.magic,
                                    action=OrderExecution.CLOSE_POSITION,
                                    settings=self._settings,
                                    order_type=position.type,
                                    price=0.0,
                                    spread=symbol_attributes.spread,
                                    digits=symbol_attributes.digits,
                                    stop_loss=0.0,
                                    stop_gain=0.0,
                                    limit_price=0.0,
                                    stop_limit=0.0,
                                    ticket=position.ticket)
        return None
