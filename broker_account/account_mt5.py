from broker_account import BrokerAccount, AccountState


class BrokerAccountMT5(BrokerAccount):
    def get_acc_state(self) -> AccountState:
        positions = self._api.get_positions()
        orders = self._api.get_orders()
        self._state = AccountState(orders=orders, positions=positions)
        return self._state
