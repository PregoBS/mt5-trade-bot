from dataclasses import dataclass


@dataclass
class Order:
    type: str  # PENDING or AT_MARKET
    price: float
    spread: float
    stop_loss: float = 0.0
    stop_gain: float = 0.0


@dataclass
class State:
    symbol: str
    timeframe: str
    strategy: str
    order: Order
    is_buy: bool = False
    is_sell: bool = False
