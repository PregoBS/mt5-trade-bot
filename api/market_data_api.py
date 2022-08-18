from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pandas import DataFrame
from typing import List


@dataclass
class TimeFrame:
    M1: str
    M5: str
    M15: str
    H1: str
    H4: str
    D1: str
    W1: str
    MN1: str


@dataclass
class Attributes:
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
    ticket: int
    open_time: str
    type: str
    volume: float
    stop_loss: float
    stop_gain: float
    magic: int


@dataclass
class Order:
    symbol: str
    ticket: int
    placed_time: str
    type: str
    volume: float
    price_open: float
    price_stop_limit: float
    stop_loss: float
    stop_gain: float
    magic: int


class MarketDataAPI(ABC):
    DATAFRAME_COLUMNS = ["_Digits", "Open", "High", "Low", "Close", "Volume", "Trades", "Spread"]
    TIMEFRAME: TimeFrame
    """Abstract API Class to get market data."""
    def __init__(self, delta_timezone: int) -> None:
        self.delta_timezone = delta_timezone

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the API and return true if it was successful"""
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """Disconnect from the API and return true if it was successful"""
        pass

    @abstractmethod
    def create_dataframe_from_bars(self, symbol: str, timeframe: str or int, start_position: int, bars: int) -> DataFrame or None:
        """Create a pandas DataFrame for a given symbol and timeframe based on the number of bars."""
        pass

    @abstractmethod
    def create_dataframe_from_date(self, symbol: str, timeframe: str or int, start_date: datetime, end_date: datetime) -> DataFrame or None:
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
    def get_positions(self) -> List[Position]:
        """Return the account open positions"""
        pass

    @abstractmethod
    def get_orders(self) -> List[Order]:
        """Return the account placed orders"""
        pass
