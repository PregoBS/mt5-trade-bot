from __future__ import annotations
from dataclasses import dataclass
from shared_data_structures import OrderRequestState, OrderSendRequest, WaitToCheckAgainState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import Attributes, TimeFrames
    from bot import TradeBot
    from shared_data_structures import OrderExecution, OrderType, StrategyState
    from symbols_info import SymbolsInfo


@dataclass
class TradeRiskSettings:
    timeframe: TimeFrames
    op_goal: float
    op_stop: float


class TradeRiskManager:
    def __init__(self, trade_bot: TradeBot, symbols_info: SymbolsInfo) -> None:
        self._bot = trade_bot
        self._symbols_info = symbols_info
        self._comment = ""
        self._volume = 0
        self._attr: Attributes or None = None
        self._state: OrderRequestState or None = None
        self._settings: TradeRiskSettings or None = None

    @property
    def risk_settings(self) -> TradeRiskSettings:
        return self._settings

    @risk_settings.setter
    def risk_settings(self, settings: TradeRiskSettings) -> None:
        self._settings = settings

    @property
    def symbol_attributes(self) -> Attributes:
        return self._attr

    @symbol_attributes.setter
    def symbol_attributes(self, attr: Attributes) -> None:
        self._attr = attr

    def update(self, state: StrategyState) -> None:
        self._volume = 0.0
        if self._is_new_trade(state.action):
            if not self._can_open_trade(state):
                print(f"TRADE RISK: Updating --- Comment: {self._comment}")
                self._symbols_info.update(WaitToCheckAgainState(symbol=state.symbol,
                                                                timeframe=state.timeframe,
                                                                strategy=state.strategy))
                return None
        self._set_state(state)
        print(f"TRADE RISK: Updating --- Comment: {self._comment}")
        if self._state is not None:
            self._bot.update(self._state)
        return None

    def spread_compensation(self, stop_loss: float, stop_gain: float, order_type: OrderType) -> None:
        if stop_loss > 0:
            stop_loss = stop_loss + self._attr.spread if "SELL" in order_type.value else stop_loss
        if stop_gain > 0:
            stop_gain = stop_gain + self._attr.spread if "SELL" in order_type.value else stop_gain
        return None

    def get_trade_volume(self, stop_loss: float, order_type: OrderType) -> float:
        # Delta between Price_open and Stop_loss
        delta = self._attr.ask - stop_loss if "BUY" in order_type.value else stop_loss - self._attr.bid

        volume = self.risk_settings.op_stop / (self._attr.contract_size * self._attr.usd_profit_converter * delta)
        volume = round(volume / self._attr.volume_step, 0) * self._attr.volume_step
        if volume >= self._attr.volume_min:
            return float(min(volume, self._attr.volume_max))
        return 0.0

    def _is_new_trade(self, action: OrderExecution) -> bool:
        if "OPEN_POSITION" in action.value or "SEND_PENDING_ORDER" in action.value:
            return True
        self._comment = "Not a new Trade"
        return False

    def _can_open_trade(self, state: StrategyState) -> bool:
        if self.risk_settings is None:
            self._comment = f"SET the Trade Risk Settings first or the Trade will not be executed!"
            return False

        if self.symbol_attributes is None:
            self._comment = f"SET the Symbol Attributes first or the Trade will not be executed!"
            return False

        self.spread_compensation(state.stop_loss, state.stop_gain, state.order_type)
        self._volume = self.get_trade_volume(state.stop_loss, state.order_type)
        if self._volume <= 0:
            self._comment = f"Volume is zero. The Trade will not be executed"
            return False
        self._comment = f"Allowed to open position on {state.symbol}. Volume is {self._volume}"
        return True

    def _set_state(self, state: StrategyState) -> None:
        self._state = OrderRequestState(timeframe=state.timeframe,
                                        strategy=state.strategy,
                                        action=state.action,
                                        order=OrderSendRequest(symbol=state.symbol,
                                                               action=state.action,
                                                               order_type=state.order_type,
                                                               volume=self._volume,
                                                               price=state.price,
                                                               sl=state.stop_loss,
                                                               tp=state.stop_gain,
                                                               magic=state.magic,
                                                               limit_price=state.limit_price,
                                                               stop_limit=state.stop_limit,
                                                               ticket=state.ticket,
                                                               deviation=20,
                                                               comment=f"{state.strategy} {state.timeframe}"))
        return None
