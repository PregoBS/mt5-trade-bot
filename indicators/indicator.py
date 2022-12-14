from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


class Indicator(ABC):
    """Calculate an indicator on a pandas DataFrame"""
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def calculate(self, dataframe: DataFrame) -> DataFrame:
        pass
