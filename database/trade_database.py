from __future__ import annotations
from database import Database
from dataclasses import dataclass
from shared_data_structures import CanceledOrderDatabase, DeletePositionDatabase, NewPositionDatabase,\
    NewTradeDatabase, OrderType, PlacedOrderDatabase, WaitToCheckAgainState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from symbols_info import SymbolsInfo


@dataclass
class Order:
    symbol: str
    timeframe: str
    strategy: str
    ticket: int
    placed_time: str
    price: float
    volume: float
    order_type: str  # buy_stop or buy_limit or sell_stop or sell_limit
    stop_loss: float = 0
    stop_gain: float = 0
    magic: int = 0


@dataclass
class Position:
    symbol: str
    timeframe: str
    strategy: str
    ticket: int
    open_time: str
    open_price: float
    volume: float
    position_type: str  # buy or sell
    stop_loss: float = 0
    stop_gain: float = 0
    magic: int = 0


@dataclass
class Trade:
    symbol: str
    timeframe: str
    strategy: str
    ticket: int
    open_time: str
    close_time: str
    open_price: float
    close_price: float
    volume: float
    trade_type: str  # buy or sell
    profit: float
    stop_loss: float = 0
    stop_gain: float = 0
    commission: float = 0
    swap: float = 0
    fee: float = 0
    magic: int = 0


class TradeDatabase(Database):
    def __init__(self, db_path: str, symbols_info: SymbolsInfo) -> None:
        super().__init__(db_path)
        self._symbols_info = symbols_info
        self._comment = ""
        self._create_table_trades()
        self._create_table_positions()
        self._create_table_orders()

    def update(self, state: NewPositionDatabase or NewTradeDatabase or PlacedOrderDatabase or
                            CanceledOrderDatabase or DeletePositionDatabase) -> None:
        self._store_from_state(state)
        if isinstance(state, NewPositionDatabase) or isinstance(state, PlacedOrderDatabase):
            self._symbols_info.update(WaitToCheckAgainState(symbol=state.symbol,
                                                            timeframe=state.timeframe,
                                                            strategy=state.strategy))
        print(f"TRADE DATABASE: Updating.. --- COMMENT: {self._comment}")
        return None

    def _store_from_state(self, state: NewPositionDatabase or NewTradeDatabase or PlacedOrderDatabase or
                                       CanceledOrderDatabase) -> None:
        if isinstance(state, NewPositionDatabase):
            self._comment = f"Inserting New Position for {state.symbol}"
            return self._insert_position(Position(symbol=state.symbol,
                                                  timeframe=state.timeframe,
                                                  strategy=state.strategy,
                                                  ticket=state.ticket,
                                                  open_time=state.open_time,
                                                  open_price=state.open_price,
                                                  volume=state.volume,
                                                  position_type=state.position_type.value,
                                                  stop_loss=state.stop_loss,
                                                  stop_gain=state.stop_gain,
                                                  magic=state.magic))
        if isinstance(state, NewTradeDatabase):
            self._comment = f"Deleting Position and Inserting New Trade for {state.symbol}"
            self._delete_position(state.ticket)
            return self._insert_trade(Trade(symbol=state.symbol,
                                            timeframe=state.timeframe,
                                            strategy=state.strategy,
                                            ticket=state.ticket,
                                            open_time=state.open_time,
                                            close_time=state.close_time,
                                            open_price=state.open_price,
                                            close_price=state.close_price,
                                            volume=state.volume,
                                            trade_type=state.trade_type.value,
                                            profit=state.profit,
                                            stop_loss=state.stop_loss,
                                            stop_gain=state.stop_gain,
                                            commission=state.commission,
                                            swap=state.swap,
                                            fee=state.fee,
                                            magic=state.magic))
        if isinstance(state, PlacedOrderDatabase):
            self._comment = f"Inserting New Pending Order for {state.symbol}"
            return self._insert_order(Order(symbol=state.symbol,
                                            timeframe=state.timeframe,
                                            strategy=state.strategy,
                                            ticket=state.ticket,
                                            placed_time=state.placed_time,
                                            price=state.price,
                                            volume=state.volume,
                                            order_type=state.order_type.value,
                                            stop_loss=state.stop_loss,
                                            stop_gain=state.stop_gain,
                                            magic=state.magic))
        if isinstance(state, CanceledOrderDatabase):
            self._comment = f"Deleting Pending Order for ticket {state.ticket}"
            return self._delete_order(state.ticket)
        if isinstance(state, DeletePositionDatabase):
            self._comment = f"Deleting Position for ticket {state.ticket}"
            return self._delete_position(state.ticket)
        self._comment = f"Nothing to do"
        return None

    def _create_table_trades(self):
        columns = """
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol      TEXT    NOT NULL,
        timeframe   TEXT    NOT NULL,
        strategy    TEXT    NOT NULL,
        ticket      INT     NOT NULL,
        open_time   TEXT    NOT NULL,
        close_time  TEXT    NOT NULL,
        open_price  REAL    NOT NULL,
        close_price REAL    NOT NULL,
        volume      REAL    NOT NULL,
        type        TEXT    NOT NULL,
        profit      REAL    NOT NULL,
        stop_loss   REAL,
        stop_gain   REAL,
        commission  REAL,
        swap        REAL,
        fee         REAL,
        magic       INT
        """
        return self.create_table("Trades", columns)

    def _insert_trade(self, trade: Trade) -> None:
        columns = """
        symbol, timeframe, strategy, ticket, open_time, close_time, open_price, close_price, 
        volume, type, profit, stop_loss, stop_gain, commission, swap, fee, magic
        """
        values = f"""
        '{trade.symbol}', '{trade.timeframe}', '{trade.strategy}', {trade.ticket}, '{trade.open_time}',
        '{trade.close_time}', {trade.open_price}, {trade.close_price}, {trade.volume},'{trade.trade_type}',
        {trade.profit}, {trade.stop_loss}, {trade.stop_gain}, {trade.commission}, {trade.swap}, {trade.fee}, 
        {trade.magic}
        """
        return self.insert_into_table("Trades", columns, values)

    def _create_table_positions(self):
        columns = """
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol      TEXT    NOT NULL,
        timeframe   TEXT    NOT NULL,
        strategy    TEXT    NOT NULL,
        ticket      INT     NOT NULL,
        open_time   TEXT    NOT NULL,
        open_price  REAL    NOT NULL,
        volume      REAL    NOT NULL,
        type        TEXT    NOT NULL,
        stop_loss   REAL,
        stop_gain   REAL,
        magic       INT
        """
        return self.create_table("Positions", columns)

    def _insert_position(self, position: Position) -> None:
        columns = """
        symbol, timeframe, strategy, ticket, open_time, open_price, volume, type, stop_loss, stop_gain, magic
        """
        values = f"""
        '{position.symbol}', '{position.timeframe}', '{position.strategy}', {position.ticket}, '{position.open_time}',
        {position.open_price}, {position.volume},'{position.position_type}', {position.stop_loss}, 
        {position.stop_gain}, {position.magic}
        """
        return self.insert_into_table("Positions", columns, values)

    def _delete_position(self, ticket: int) -> None:
        return self.delete_from_table("Positions", "ticket", ticket)

    def _create_table_orders(self):
        columns = """
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol      TEXT    NOT NULL,
        timeframe   TEXT    NOT NULL,
        strategy    TEXT    NOT NULL,
        ticket      INT     NOT NULL,
        placed_time TEXT    NOT NULL,
        price       REAL    NOT NULL,
        volume      REAL    NOT NULL,
        type        TEXT    NOT NULL,
        stop_loss   REAL,
        stop_gain   REAL,
        magic       INT
        """
        return self.create_table("Orders", columns)

    def _insert_order(self, order: Order) -> None:
        columns = """
        symbol, timeframe, strategy, ticket, placed_time, price, volume, type, stop_loss, stop_gain, magic
        """
        values = f"""
        '{order.symbol}', '{order.timeframe}', '{order.strategy}', {order.ticket}, '{order.placed_time}',
        {order.price}, {order.volume},'{order.order_type}', {order.stop_loss}, {order.stop_gain}, {order.magic}
        """
        return self.insert_into_table("Orders", columns, values)

    def _delete_order(self, ticket: int) -> None:
        return self.delete_from_table("Orders", "ticket", ticket)
