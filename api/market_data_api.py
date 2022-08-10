from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pandas import DataFrame


@dataclass
class TimeFrame:
    M1: int or str
    M5: int or str
    M15: int or str
    H1: int or str
    H4: int or str
    D1: int or str
    W1: int or str
    MN1: int or str


class MarketDataAPI(ABC):
    DATAFRAME_COLUMNS = ["Open", "High", "Low", "Close", "Volume", "Trades", "Spread"]
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
