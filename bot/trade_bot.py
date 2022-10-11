from __future__ import annotations
from shared_data_structures import NewPositionDatabase, NewTradeDatabase, OrderExecution, OrderSendRequest, \
    OrderSendResponse, PlacedOrderDatabase, CanceledOrderDatabase, WaitToCheckAgainState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import MarketDataAPI, TradeResult
    from database import Database
    from shared_data_structures import OrderRequestState
    from symbols_info import SymbolsInfo


class TradeBot:
    def __init__(self, api: MarketDataAPI, db: Database, symbols_info: SymbolsInfo) -> None:
        self._api = api
        self._db = db
        self._symbols_info = symbols_info
        self._trade_result: TradeResult or None = None
        self._state: NewPositionDatabase or NewTradeDatabase or \
                     PlacedOrderDatabase or CanceledOrderDatabase or None = None

    def update(self, state: OrderRequestState) -> None:
        print(f"TRADE BOT: Updating --- {state.order.order_type.value} - {state.action.value}")
        self._trade_result = None
        self._state = None

        order_request = self._create_order_send_request(state)
        response: OrderSendResponse = self._api.execute_action(state.action)(order_request)

        if self.check_result(response):
            self._set_state(state)
            self._db.update(self._state)
        else:
            self._symbols_info.update(WaitToCheckAgainState(symbol=state.order.symbol,
                                                            timeframe=state.timeframe,
                                                            strategy=state.strategy))
        return None

    def _create_order_send_request(self, state: OrderRequestState) -> OrderSendRequest:
        return OrderSendRequest(symbol=state.order.symbol,
                                action=state.action,
                                magic=state.order.magic,
                                volume=state.order.volume,
                                price=state.order.price,
                                order_type=state.order.order_type,
                                ticket=state.order.ticket,
                                limit_price=state.order.limit_price,
                                stop_limit=state.order.stop_limit,
                                sl=state.order.sl,
                                tp=state.order.tp,
                                deviation=state.order.deviation,
                                comment=state.order.comment)

    def check_result(self, result: OrderSendResponse) -> bool:
        if result is None:
            return False
        symbol = result.symbol
        if result.status:
            print(f"{symbol} - {result.action.value} - SUCCESS - RETCODE: {result.code} - COMMENT: {result.comment}")
            self._set_trade_result(result.ticket)
        else:
            print(f"{symbol} - {result.action.value} - FAILED - RETCODE: {result.code} - COMMENT: {result.comment}")
        return result.status

    def _set_trade_result(self, ticket: int) -> None:
        self._trade_result = self._api.get_trade_result(ticket)
        return None

    def _set_state(self, state: OrderRequestState) -> None:
        if self._trade_result is None:
            return None
        actions = {
            OrderExecution.OPEN_POSITION: self._create_new_position_database(state),
            OrderExecution.CLOSE_POSITION: self._create_new_trade_database(state),
            OrderExecution.SEND_PENDING_ORDER: self._create_placed_order_database(state),
            OrderExecution.DELETE_PENDING_ORDER: self._create_canceled_order_database(),
        }
        self._state = actions.get(state.action)
        return None

    def _create_new_position_database(self, state: OrderRequestState) -> NewPositionDatabase:
        return NewPositionDatabase(symbol=state.order.symbol,
                                   timeframe=state.timeframe,
                                   strategy=state.strategy,
                                   open_time=self._trade_result.open_time,
                                   open_price=self._trade_result.open_price,
                                   volume=state.order.volume,
                                   position_type=state.order.order_type,
                                   stop_loss=state.order.sl,
                                   stop_gain=state.order.tp,
                                   magic=state.order.magic,
                                   ticket=self._trade_result.ticket)

    def _create_new_trade_database(self, state: OrderRequestState) -> NewTradeDatabase:
        return NewTradeDatabase(symbol=state.order.symbol,
                                timeframe=state.timeframe,
                                strategy=state.strategy,
                                open_time=self._trade_result.open_time,
                                close_time=self._trade_result.close_time,
                                open_price=self._trade_result.open_price,
                                close_price=self._trade_result.close_price,
                                volume=state.order.volume,
                                trade_type=state.order.order_type,
                                profit=self._trade_result.profit,
                                stop_loss=state.order.sl,
                                stop_gain=state.order.tp,
                                commission=self._trade_result.commission,
                                swap=self._trade_result.swap,
                                fee=self._trade_result.fee,
                                magic=state.order.magic,
                                ticket=self._trade_result.ticket)

    def _create_placed_order_database(self, state: OrderRequestState) -> PlacedOrderDatabase:
        return PlacedOrderDatabase(symbol=state.order.symbol,
                                   timeframe=state.timeframe,
                                   strategy=state.strategy,
                                   placed_time=self._trade_result.open_time,
                                   price=self._trade_result.open_price,
                                   volume=state.order.volume,
                                   order_type=state.order.order_type,
                                   stop_loss=state.order.sl,
                                   stop_gain=state.order.tp,
                                   magic=state.order.magic,
                                   ticket=self._trade_result.ticket)

    def _create_canceled_order_database(self) -> CanceledOrderDatabase:
        return CanceledOrderDatabase(ticket=self._trade_result.ticket)
