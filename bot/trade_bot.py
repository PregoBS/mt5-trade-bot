from design_patterns.observer_pattern import Observer
from strategies.strategy import State


class TradeBot(Observer):
    def update(self, state: State) -> None:
        print(f"Trade BOT:\n    State Updated:\n        {state.strategy}")
        if state.is_buy:
            print(f"        É PARA COMPRAR: {state.symbol}")
        if state.is_sell:
            print(f"        É PARA VENDER: {state.symbol}")
        print(f"            TIPO: {state.order.type}")
        print(f"            PREÇO: {state.order.price}")
        print(f"            DIGITOS: {state.order.digits}")
        print(f"            STOP LOSS: {state.order.stop_loss}")
        print(f"            STOP GAIN: {state.order.stop_gain}")
        print(f"            SPREAD: {state.order.spread}")
