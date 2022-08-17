from database.database import Database, Order, Position, Trade


class TradeDatabase(Database):
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
