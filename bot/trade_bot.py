from design_patterns.observer_pattern import Observer, Subject
import strategies
from typing import List


class TradeBot(Observer, Subject):
    def __init__(self) -> None:
        Observer.__init__(self)
        Subject.__init__(self)
        self._state = {}
        self.observers: List[Observer] = []

    def subscribe(self, ob: Observer) -> None:
        return self.observers.append(ob)

    def unsubscribe(self, ob: Observer) -> None:
        return self.observers.remove(ob)

    def notify(self) -> None:
        for observer in self.observers:
            observer.update(self._state)

    def update(self, state: strategies.State) -> None:
        print(f"\nTRADE BOT: Recebendo atualização\n{state.strategy}")
        if state.is_buy:
            print(f"É PARA COMPRAR: {state.symbol}")
        if state.is_sell:
            print(f"É PARA VENDER: {state.symbol}")
        print(f"TIPO: {state.order.type}")
        print(f"PREÇO: {state.order.price}")
        print(f"DIGITOS: {state.order.digits}")
        print(f"STOP LOSS: {state.order.stop_loss}")
        print(f"STOP GAIN: {state.order.stop_gain}")
        print(f"SPREAD: {state.order.spread}")
        print("\nTRADE BOT: Enviando atualização para Observers...")
        self._state = {
            "FROM": "AQUI É O TRADE BOT",
            "MESSAGE": "FIZ UM TRADE, SEGUE OS DADOS",
            "data": state
        }
        self.notify()
