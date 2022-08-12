from dataclasses import dataclass
from design_patterns.observer_pattern import Observer
import pandas as pd
import sqlite3
from sqlite3 import Cursor


@dataclass
class Order:
    symbol: str
    timeframe: str
    strategy: str
    ticket: int
    placed_time: str
    price: float
    order_type: str  # buy_stop or buy_limit or sell_stop or sell_limit
    stop_loss: float = 0
    stop_gain: float = 0


@dataclass
class Position:
    symbol: str
    timeframe: str
    strategy: str
    ticket: int
    open_time: str
    open_price: float
    position_type: str  # buy or sell
    stop_loss: float = 0
    stop_gain: float = 0


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
    trade_type: str  # buy or sell
    profit: float
    stop_loss: float = 0
    stop_gain: float = 0
    commission: float = 0
    swap: float = 0
    fee: float = 0


class Database(Observer):
    def __init__(self, db_path: str) -> None:
        Observer.__init__(self)
        self.path = db_path
        self._create_table_trades()
        self._create_table_positions()
        self._create_table_orders()

    def update(self, state) -> None:
        print("DATABASE: Recebendo atualização do Subject")
        print(state)
        print("DATABASE: Okay, vou salvar tudo!")

    def get_table(self, table_name: str) -> pd.DataFrame:
        with sqlite3.connect(self.path) as db:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", db)
        return df

    def print_table(self, table_name: str) -> None:
        df = self.get_table(table_name)
        if df.empty:
            print(f"Empty Table: {table_name}", end="\n\n")
        else:
            print(f"Table: {table_name}\n{df}", end='\n\n')
        return None

    def create_table(self, name: str, columns: str) -> None:
        query = f"CREATE TABLE IF NOT EXISTS {name} ({columns});"
        self._execute(query)
        return None

    def insert_into_table(self, name: str, columns: str, values: str) -> None:
        query = f"INSERT INTO {name} ({columns}) VALUES ({values});"
        self._execute(query)
        return None

    def drop_table(self, table_name: str) -> None:
        self._execute(f"DROP TABLE {table_name};")
        return None

    def _execute(self, query: str) -> None:
        with sqlite3.connect(self.path) as db:
            c: Cursor = db.cursor()
            c.execute(query)
            c.close()
            db.commit()
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
        type        TEXT    NOT NULL,
        profit      REAL    NOT NULL,
        stop_loss   REAL,
        stop_gain   REAL,
        commission  REAL,
        swap        REAL,
        fee         REAL
        """
        return self.create_table("Trades", columns)

    def _insert_trade(self, trade: Trade) -> None:
        columns = """
        symbol, timeframe, strategy, ticket, open_time, close_time, open_price, 
        close_price, type, profit, stop_loss, stop_gain, commission, swap, fee
        """
        values = f"""
        '{trade.symbol}', '{trade.timeframe}', '{trade.strategy}', {trade.ticket}, '{trade.open_time}',
        '{trade.close_time}', {trade.open_price}, {trade.close_price}, '{trade.trade_type}', {trade.profit},
        {trade.stop_loss}, {trade.stop_gain}, {trade.commission}, {trade.swap}, {trade.fee}
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
        type        TEXT    NOT NULL,
        stop_loss   REAL,
        stop_gain   REAL
        """
        return self.create_table("Positions", columns)

    def _insert_position(self, position: Position) -> None:
        columns = """
        symbol, timeframe, strategy, ticket, open_time, open_price, type, stop_loss, stop_gain
        """
        values = f"""
        '{position.symbol}', '{position.timeframe}', '{position.strategy}', {position.ticket}, '{position.open_time}',
        {position.open_price}, '{position.position_type}', {position.stop_loss}, {position.stop_gain}
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
        type        TEXT    NOT NULL,
        stop_loss   REAL,
        stop_gain   REAL
        """
        return self.create_table("Orders", columns)

    def _insert_order(self, order: Order) -> None:
        columns = """
        symbol, timeframe, strategy, ticket, placed_time, price, type, stop_loss, stop_gain
        """
        values = f"""
        '{order.symbol}', '{order.timeframe}', '{order.strategy}', {order.ticket}, '{order.placed_time}',
        {order.price}, '{order.order_type}', {order.stop_loss}, {order.stop_gain}
        """
        return self.insert_into_table("Orders", columns, values)
