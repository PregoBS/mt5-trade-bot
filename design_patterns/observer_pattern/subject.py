from abc import ABC, abstractmethod
from design_patterns.observer_pattern.observer import Observer
from typing import List


class Subject(ABC):
    def __init__(self) -> None:
        self.observers: List[Observer] = []

    def subscribe(self, ob: Observer) -> None:
        if ob not in self.observers:
            self.observers.append(ob)

    def unsubscribe(self, ob: Observer) -> None:
        if ob in self.observers:
            self.observers.remove(ob)

    @abstractmethod
    def notify(self) -> None:
        pass
