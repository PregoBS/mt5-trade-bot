from abc import ABC, abstractmethod
from api import MarketDataAPI
from dataclasses import dataclass


@dataclass
class AccountState:
    orders: list
    positions: list


class AccountListener(ABC):
    def __init__(self, api: MarketDataAPI) -> None:
        super().__init__()
        self._api = api
        self._state: AccountState or None = None

    @abstractmethod
    def listen_for_changes(self) -> None:
        pass

    @abstractmethod
    def get_current_state(self) -> None:
        pass


