from dataclasses import dataclass
from design_patterns.observer_pattern import Observer, Subject
from strategies import StrategyState
from api import Attributes


@dataclass
class TradeRiskSettings:
    op_goal: float
    op_stop: float


class TradeRiskManager(Observer, Subject):
    def __init__(self, symbol_attributes: Attributes) -> None:
        super().__init__()
        self._attr = symbol_attributes
        self._state: StrategyState or None = None
        self._settings: TradeRiskSettings or None = None

    @property
    def risk_settings(self) -> TradeRiskSettings:
        return self._settings

    @risk_settings.setter
    def risk_settings(self, settings: TradeRiskSettings) -> None:
        self._settings = settings

    def update(self, state: StrategyState) -> None:
        print(f"TRADE RISK: Updating")
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

    def get_trade_volume(self, attr: Attributes, stop_loss: float, is_buy: bool) -> float:
        if self.risk_settings is None:
            print("SET the Trade Risk Settings first or the Trade will not be executed!")
            return 0.0

        # Delta between Price_open and Stop_loss
        delta = attr.ask - stop_loss + attr.spread if is_buy else stop_loss - attr.bid

        volume = self.risk_settings.op_stop / (attr.contract_size * attr.usd_profit_converter * delta)

        volume = round(volume / attr.volume_step, 0) * attr.volume_step
        if volume >= attr.volume_min:
            return float(min(volume, attr.volume_max))
        return 0.0

    def _can_open_trade(self, state: StrategyState) -> bool:
        volume = self.get_trade_volume(self._attr, state.order.stop_loss, state.is_buy)
        if volume <= 0:
            print("Volume zero!")
            print("Não vamos seguir")
            return False

        state.order.volume = volume
        return True
