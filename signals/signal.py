from abc import ABC, abstractmethod
from dataclasses import dataclass
from pandas import DataFrame


@dataclass
class SignalObj:
    name: str
    symbol: str
    timeframe: str
    value: int


class Signal(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_signal(self, symbol: str, timeframe: str, dataframe: DataFrame) -> SignalObj:
        pass
