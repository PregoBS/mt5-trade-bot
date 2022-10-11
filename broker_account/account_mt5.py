from __future__ import annotations
from broker_account import BrokerAccount
from shared_data_structures import NewTradeDatabase, CanceledOrderDatabase
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from api import Position, TradeResult, Order


class BrokerAccountMT5(BrokerAccount):
    def get_orders(self) -> List[Order]:
        return self._api.get_orders()

    def get_positions(self) -> List[Position]:
        return self._api.get_positions()

    def get_positions_by(self, magic: int) -> List[Position]:
        return [position for position in self._api.get_positions() if position.magic == magic]

    def get_trade(self, ticket: int) -> TradeResult:
        return self._api.get_trade_result(ticket)

    def sync_db(self) -> None:
        self._sync_db_positions()
        self._sync_db_orders()
        return None

    def _sync_db_positions(self) -> None:
        acc_positions = self.get_positions()
        acc_tickets = [position.ticket for position in acc_positions]
        db_positions = self._db.get_table("Positions")
        db_tickets = db_positions["ticket"].to_list()
        for ticket in db_tickets:
            if ticket in acc_tickets:
                continue
            trade_result = self.get_trade(ticket)
            db_ticket_row = db_positions[db_positions["ticket"] == ticket].to_dict(orient="records")[0]
            self._db.update(NewTradeDatabase(symbol=db_ticket_row["symbol"],
                                             timeframe=db_ticket_row["timeframe"],
                                             strategy=db_ticket_row["strategy"],
                                             open_time=trade_result.open_time,
                                             close_time=trade_result.close_time,
                                             open_price=trade_result.open_price,
                                             close_price=trade_result.close_price,
                                             volume=db_ticket_row["volume"],
                                             trade_type=db_ticket_row["type"],
                                             profit=trade_result.profit,
                                             stop_loss=db_ticket_row["stop_loss"],
                                             stop_gain=db_ticket_row["stop_gain"],
                                             commission=trade_result.commission,
                                             swap=trade_result.swap,
                                             fee=trade_result.fee,
                                             magic=db_ticket_row["magic"],
                                             ticket=trade_result.ticket))

    def _sync_db_orders(self) -> None:
        acc_orders = self.get_orders()
        db_orders = self._db.get_table("Orders")
        acc_tickets = [order.ticket for order in acc_orders]
        db_tickets = db_orders["ticket"].to_list()
        for ticket in db_tickets:
            if ticket in acc_tickets:
                continue
            self._db.update(CanceledOrderDatabase(ticket=ticket))
