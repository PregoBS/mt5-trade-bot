from abc import ABC, abstractmethod
from design_patterns.observer_pattern.state import State


class Observer(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def update(self, state: State) -> None:
        pass
