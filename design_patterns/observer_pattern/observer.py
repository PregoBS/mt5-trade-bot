from abc import ABC, abstractmethod


class Observer(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def update(self, state) -> None:
        pass
