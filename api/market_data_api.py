from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from shared_data_structures import OrderExecution, OrderSendRequest, OrderSendResponse
from typing import Callable, List, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from pandas import DataFrame
    from shared_data_structures import OrderType


TradeActionExecutionFunction = Callable[[OrderSendRequest], OrderSendResponse]


@dataclass
class Credentials(Protocol):
    """Credentials from the broker API. Each API class has its own implementation"""
    pass


class TimeFrames(Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"


@dataclass
class TradeResult:
    open_time: str
    open_price: float
    close_time: str
    close_price: float
    ticket: int
    commission: float
    fee: float
    swap: float
    profit: float


@dataclass
class Attributes:
    symbol: str
    ask: float
    bid: float
    usd_profit_converter: float
    digits: int
    currency_base: str
    currency_profit: str
    tick: float
    contract_size: float
    spread: float
    volume_step: float
    volume_min: float
    volume_max: float


@dataclass
class Position:
    symbol: str
    timeframe: str
    strategy: str
    ticket: int
    price_open: float
    open_time: str
    type: OrderType
    volume: float
    profit: float
    stop_loss: float
    stop_gain: float
    magic: int


@dataclass
class Order:
    symbol: str
    ticket: int
    placed_time: str
    type: OrderType
    volume: float
    price_open: float
    price_stop_limit: float
    stop_loss: float
    stop_gain: float
    magic: int


class MarketDataAPI(ABC):
    """Abstract API Base Class to get market data."""
    DATAFRAME_COLUMNS = ["_Digits", "Open", "High", "Low", "Close", "Volume", "Trades", "Spread"]
    ORDER_EXECUTION: dict[OrderExecution, int or str]
    ORDER_TYPES: dict[OrderType, int or str]
    TIMEFRAMES: dict[TimeFrames, int or str]

    def __init__(self, delta_timezone: int) -> None:
        self.delta_timezone = delta_timezone

    @abstractmethod
    def connect(self, credentials: Credentials) -> bool:
        """Connect to the API and return true if it was successful"""
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """Disconnect from the API and return true if it was successful"""
        pass

    @abstractmethod
    def create_dataframe_from_bars(self, symbol: str, timeframe: str or int, start_position: int,
                                   bars: int) -> DataFrame or None:
        """Create a pandas DataFrame for a given symbol and timeframe based on the number of bars."""
        pass

    @abstractmethod
    def create_dataframe_from_date(self, symbol: str, timeframe: str or int, start_date: datetime,
                                   end_date: datetime) -> DataFrame or None:
        """Create a pandas DataFrame for a given symbol and timeframe between two date times."""
        pass

    @abstractmethod
    def _standardize_dataframe(self, dataframe: DataFrame, symbol: str) -> DataFrame:
        """Return the dataframe with standard column names"""
        pass

    @abstractmethod
    def get_symbol_attributes(self, symbol: str) -> Attributes:
        """Return the symbol attributes"""
        pass

    @abstractmethod
    def get_position(self, ticket: int) -> Position:
        """Return the account open position by ticket"""
        pass

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Return the account open positions"""
        pass

    @abstractmethod
    def get_orders(self) -> List[Order]:
        """Return the account placed orders"""
        pass

    @abstractmethod
    def format_timestamp(self, timestamp: int) -> str:
        """Return the timestamp data as formatted string"""
        pass

    @abstractmethod
    def get_trade_result(self, ticket: int) -> TradeResult:
        """Return the trade result for the current ticket"""
        pass

    def execute_action(self, action: OrderExecution) -> TradeActionExecutionFunction:
        """Selector to execute the correct action"""
        actions: dict[OrderExecution, TradeActionExecutionFunction] = {
            OrderExecution.OPEN_POSITION: self.open_position,
            OrderExecution.CLOSE_POSITION: self.close_position,
            OrderExecution.MODIFY_POSITION: self.modify_position,
            OrderExecution.SEND_PENDING_ORDER: self.send_pending_order_limit_stop,
            OrderExecution.MODIFY_PENDING_ORDER: self.modify_pending_order,
            OrderExecution.DELETE_PENDING_ORDER: self.delete_pending_order,
        }
        return actions.get(action)

    @abstractmethod
    def have_free_margin(self, order_type: OrderType, symbol: str, volume: float, price: float) -> bool:
        """Check if the account have free margin to open the position"""
        pass

    @abstractmethod
    def open_position(self, request: OrderSendRequest) -> OrderSendResponse or None:
        """Open a new position in the broker account"""
        pass

    @abstractmethod
    def close_position(self, request: OrderSendRequest) -> OrderSendResponse or None:
        """Close an opened position in the broker account"""
        pass

    @abstractmethod
    def modify_position(self, request: OrderSendRequest) -> OrderSendResponse or None:
        """Modify an opened position stop_loss or take_profit in the broker account"""
        pass

    @abstractmethod
    def send_pending_order_limit_stop(self, request: OrderSendRequest) -> OrderSendResponse or None:
        """Place an order limit or stop in the broker account"""
        pass

    @abstractmethod
    def modify_pending_order(self, request: OrderSendRequest) -> OrderSendResponse or None:
        """Modify a placed order in the broker account"""
        pass

    @abstractmethod
    def delete_pending_order(self, request: OrderSendRequest) -> OrderSendResponse or None:
        """Delete a placed order in the broker account"""
        pass
