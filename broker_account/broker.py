from abc import ABC, abstractmethod
from api import MarketDataAPI, Order, Position
from dataclasses import dataclass
from typing import List


@dataclass
class AccountState:
    orders: List[Order]
    positions: List[Position]


class BrokerAccount(ABC):
    def __init__(self, api: MarketDataAPI) -> None:
        super().__init__()
        self._api = api
        self._state: AccountState or None = None

    @abstractmethod
    def get_acc_state(self) -> AccountState:
        pass


