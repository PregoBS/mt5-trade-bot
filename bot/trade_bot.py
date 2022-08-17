from design_patterns.observer_pattern import Observer, Subject
from strategies import StrategyState


class TradeBot(Observer, Subject):
    def __init__(self) -> None:
        super().__init__()
        self._state: dict or None = None

    def update(self, state: StrategyState) -> None:
        print(f"TRADE BOT: Updating")
        # EXECUTE THE TRADE
        self._state = state
        return self.notify()

    def notify(self) -> None:
        if self._state is None:
            return None
        for observer in self.observers:
            observer.update(self._state)
        return None
