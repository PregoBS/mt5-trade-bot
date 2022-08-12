from abc import ABC, abstractmethod
from design_patterns.observer_pattern.observer import Observer
from typing import List


class Subject(ABC):
    def __init__(self) -> None:
        self.observers: List[Observer] = []

    @abstractmethod
    def subscribe(self, ob: Observer) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, ob: Observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass
