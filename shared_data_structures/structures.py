from dataclasses import dataclass
from enum import Enum


class OrderExecution(Enum):
    OPEN_POSITION = "OPEN_POSITION"
    CLOSE_POSITION = "CLOSE_POSITION"
    MODIFY_POSITION = "MODIFY_POSITION"
    SEND_PENDING_ORDER = "SEND_PENDING_ORDER"
    MODIFY_PENDING_ORDER = "MODIFY_PENDING_ORDER"
    DELETE_PENDING_ORDER = "DELETE_PENDING_ORDER"


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    BUY_STOP = "BUY_STOP"
    BUY_STOP_LIMIT = "BUY_STOP_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    SELL_STOP = "SELL_STOP"
    SELL_STOP_LIMIT = "SELL_STOP_LIMIT"
    NONE = "NONE"


@dataclass
class StrategySettings:
    can_open_multiple_positions: bool
    max_volume: float


@dataclass
class StrategyState:
    symbol: str
    timeframe: str
    strategy: str
    magic: int
    action: OrderExecution
    settings: StrategySettings
    order_type: OrderType
    price: float
    spread: float
    digits: int
    stop_loss: float
    stop_gain: float
    limit_price: float
    stop_limit: float
    ticket: int


@dataclass
class OrderSendResponse:
    symbol: str
    action: OrderExecution
    order_type: OrderType
    status: bool
    ticket: int
    code: int
    comment: str


@dataclass
class OrderSendRequest:
    symbol: str
    action: OrderExecution
    order_type: OrderType
    volume: float
    price: float
    sl: float
    tp: float
    magic: int
    limit_price: float = 0.0
    stop_limit: float = 0.0
    ticket: int = 0
    deviation: int = 20
    comment: str = ""


@dataclass
class OrderRequestState:
    timeframe: str
    strategy: str
    action: OrderExecution
    order: OrderSendRequest


@dataclass
class NewPositionDatabase:
    symbol: str
    timeframe: str
    strategy: str
    open_time: str
    open_price: float
    volume: float
    position_type: OrderType
    stop_loss: float
    stop_gain: float
    magic: int
    ticket: int


@dataclass
class NewTradeDatabase:
    symbol: str
    timeframe: str
    strategy: str
    open_time: str
    close_time: str
    open_price: float
    close_price: float
    volume: float
    trade_type: OrderType
    profit: float
    stop_loss: float
    stop_gain: float
    commission: float
    swap: float
    fee: float
    magic: int
    ticket: int


@dataclass
class PlacedOrderDatabase:
    symbol: str
    timeframe: str
    strategy: str
    placed_time: str
    price: float
    volume: float
    order_type: OrderType
    stop_loss: float
    stop_gain: float
    magic: int
    ticket: int


@dataclass
class CanceledOrderDatabase:
    ticket: int


@dataclass
class DeletePositionDatabase:
    ticket: int


@dataclass
class WaitToCheckAgainState:
    symbol: str
    timeframe: str
    strategy: str
