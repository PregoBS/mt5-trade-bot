from database.database import Database
from dataclasses import dataclass
import pandas as pd


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
    def __init__(self, db_path: str) -> None:
        super().__init__(db_path)
        self._create_table_trades()
        self._create_table_positions()
        self._create_table_orders()

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
