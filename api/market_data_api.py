from abc import ABC, abstractmethod
from datetime import datetime
from pandas import DataFrame


class MarketDataAPI(ABC):
    """Abstract API Class to get market data."""
    def __init__(self, delta_timezone: int) -> None:
        self.delta_timezone = delta_timezone
        self.dataframe_columns = ["Open", "High", "Low", "Close", "Volume", "Trades", "Spread"]

    @abstractmethod
    def create_dataframe_from_bars(self, symbol: str, timeframe: str, start_position: int, bars: int) -> DataFrame or None:
        """Create a pandas DataFrame for a given symbol and timeframe based on the number of bars."""
        pass

    @abstractmethod
    def create_dataframe_from_date(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> DataFrame or None:
        """Create a pandas DataFrame for a given symbol and timeframe between two date times."""
        pass

    @abstractmethod
    def _standardize_dataframe(self, dataframe: DataFrame, symbol: str) -> DataFrame:
        """Return the dataframe with standard column names"""
        pass

    @abstractmethod
    def _switch_timeframe(self, timeframe: str) -> str or int or None:
        """Switch the timeframe string to a value that the API read"""
        pass

    def _validate_dataframe(self, dataframe: DataFrame) -> bool:
        return dataframe.columns == self.dataframe_columns
