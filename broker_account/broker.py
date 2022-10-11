from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from api import MarketDataAPI, Position, Order
    from database import Database


class BrokerAccount(ABC):
    def __init__(self, api: MarketDataAPI, db: Database) -> None:
        super().__init__()
        self._api = api
        self._db = db

    @abstractmethod
    def get_positions(self) -> List[Position]:
        pass

    @abstractmethod
    def get_positions_by(self, magic: int) -> List[Position]:
        pass

    @abstractmethod
    def get_trade(self, ticket: int):
        pass

    @abstractmethod
    def get_orders(self) -> List[Order]:
        pass

    @abstractmethod
    def sync_db(self):
        pass
