from __future__ import annotations
from api import Attributes, MarketDataAPI, Order, Position, TimeFrames, TradeResult
from dataclasses import dataclass
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from shared_data_structures import OrderType, OrderExecution, OrderSendResponse
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from shared_data_structures import OrderSendRequest


@dataclass
class MT5Credentials:
    path: str
    login: int
    server: str
    password: str


class MetaTrader5API(MarketDataAPI):
    ORDER_EXECUTION: dict[OrderExecution, int] = {
        OrderExecution.OPEN_POSITION.value: mt5.TRADE_ACTION_DEAL,
        OrderExecution.CLOSE_POSITION.value: mt5.TRADE_ACTION_DEAL,
        OrderExecution.MODIFY_POSITION.value: mt5.TRADE_ACTION_SLTP,
        OrderExecution.SEND_PENDING_ORDER.value: mt5.TRADE_ACTION_PENDING,
        OrderExecution.MODIFY_PENDING_ORDER.value: mt5.TRADE_ACTION_MODIFY,
        OrderExecution.DELETE_PENDING_ORDER.value: mt5.TRADE_ACTION_REMOVE
    }

    ORDER_TYPES: dict[OrderType, int] = {
        OrderType.BUY.value: mt5.ORDER_TYPE_BUY,
        OrderType.SELL.value: mt5.ORDER_TYPE_SELL,
        OrderType.BUY_LIMIT.value: mt5.ORDER_TYPE_BUY_LIMIT,
        OrderType.BUY_STOP.value: mt5.ORDER_TYPE_BUY_STOP,
        OrderType.BUY_STOP_LIMIT.value: mt5.ORDER_TYPE_BUY_STOP_LIMIT,
        OrderType.SELL_LIMIT.value: mt5.ORDER_TYPE_SELL_LIMIT,
        OrderType.SELL_STOP.value: mt5.ORDER_TYPE_SELL_STOP,
        OrderType.SELL_STOP_LIMIT.value: mt5.ORDER_TYPE_SELL_STOP_LIMIT
    }

    TIMEFRAMES: dict[TimeFrames, int] = {
        TimeFrames.M1: mt5.TIMEFRAME_M1,
        TimeFrames.M5: mt5.TIMEFRAME_M5,
        TimeFrames.M15: mt5.TIMEFRAME_M15,
        TimeFrames.H1: mt5.TIMEFRAME_H1,
        TimeFrames.H4: mt5.TIMEFRAME_H4,
        TimeFrames.D1: mt5.TIMEFRAME_D1,
        TimeFrames.W1: mt5.TIMEFRAME_W1,
        TimeFrames.MN1: mt5.TIMEFRAME_MN1,
    }

    POSITION_TYPES: dict[int, OrderType] = {
        mt5.POSITION_TYPE_BUY: OrderType.BUY,
        mt5.POSITION_TYPE_SELL: OrderType.SELL
    }

    def connect(self, credentials: MT5Credentials) -> bool:
        """MT5 connection"""
        if not mt5.initialize(**credentials.__dict__):
            print(f"MT5 Initialize Failed, error code = {mt5.last_error()}")
            return False
        return True

    def shutdown(self) -> bool:
        """MT5 connection shutdown"""
        return mt5.shutdown()

    def create_dataframe_from_bars(self, symbol: str, timeframe: TimeFrames, start_position: int,
                                   bars: int) -> pd.DataFrame or None:
        tf = self.TIMEFRAMES[timeframe]
        dataframe = pd.DataFrame(mt5.copy_rates_from_pos(symbol, tf, start_position, bars))
        if not dataframe.empty:
            return self._standardize_dataframe(dataframe, symbol)
        return None

    def create_dataframe_from_date(self, symbol: str, timeframe: TimeFrames, start_date: datetime,
                                   end_date: datetime) -> pd.DataFrame or None:
        tf = self.TIMEFRAMES[timeframe]
        dataframe = pd.DataFrame(mt5.copy_rates_range(symbol, tf, start_date, end_date))
        if not dataframe.empty:
            return self._standardize_dataframe(dataframe, symbol)
        return None

    def _standardize_dataframe(self, dataframe: pd.DataFrame, symbol: str) -> pd.DataFrame:
        dataframe["time"] = pd.to_datetime(dataframe["time"], unit="s")
        dataframe["time"] = dataframe["time"] + timedelta(hours=self.delta_timezone)
        dataframe.rename(columns={"time": "Date"}, inplace=True)
        dataframe.set_index(dataframe["Date"], inplace=True)
        dataframe.rename(columns={"open": "Open",
                                  "high": "High",
                                  "low": "Low",
                                  "close": "Close",
                                  "tick_volume": "Trades",
                                  "real_volume": "Volume",
                                  "spread": "Spread"}, inplace=True)
        dataframe = dataframe.astype({
            "Open": np.float64,
            "High": np.float64,
            "Low": np.float64,
            "Close": np.float64,
            "Volume": np.int64,
            "Trades": np.int64,
            "Spread": np.int64
        })
        digits = mt5.symbol_info(symbol).digits
        dataframe["Open"] = round(dataframe["Open"], digits)
        dataframe["High"] = round(dataframe["High"], digits)
        dataframe["Low"] = round(dataframe["Low"], digits)
        dataframe["Close"] = round(dataframe["Close"], digits)
        dataframe["_Digits"] = digits
        del dataframe["Date"]
        return dataframe

    def get_symbol_attributes(self, symbol: str) -> Attributes:
        symbol_info = mt5.symbol_info(symbol)
        converter = self._usd_profit_converter(str(symbol_info.currency_profit))
        return Attributes(symbol=symbol,
                          ask=round(symbol_info.ask, symbol_info.digits),
                          bid=round(symbol_info.bid, symbol_info.digits),
                          usd_profit_converter=converter,
                          spread=round(abs(symbol_info.ask - symbol_info.bid), symbol_info.digits),
                          digits=symbol_info.digits,
                          tick=symbol_info.trade_tick_size,
                          contract_size=symbol_info.trade_contract_size,
                          currency_base=str(symbol_info.currency_base),
                          currency_profit=str(symbol_info.currency_profit),
                          volume_max=symbol_info.volume_max,
                          volume_min=symbol_info.volume_min,
                          volume_step=symbol_info.volume_step)

    def _usd_profit_converter(self, currency_profit: str) -> float:
        """
        EX: the currency profit is USD then the converter is 1.0
        EX: the currency profit is GBP
        try to find the price of USDGBP then use the LASTPRICE as the CONVERTER
        if USDGBP is not found, try the reverse, GBPUSD, and then use (1 / LASTPRICE) as the CONVERTER
        otherwise the CONVERTER is 0.0
        """
        if currency_profit == "USD":
            return 1.0
        try:
            return mt5.symbol_info(f"USD{currency_profit}").ask
        except AttributeError:
            try:
                return mt5.symbol_info(f"{currency_profit}USD").ask
            except AttributeError:
                return 0.0

    def get_positions(self) -> List[Position]:
        positions = []
        mt5positions = mt5.positions_get()
        if mt5positions is None:
            return positions

        for position in mt5positions:
            comment = position.comment.split(" ")
            timeframe = comment[1] if len(comment) > 0 else ""
            strategy = comment[0] if len(comment) > 0 else ""
            time_string = self.format_timestamp(position.time)
            positions.append(Position(symbol=position.symbol,
                                      timeframe=timeframe,
                                      strategy=strategy,
                                      ticket=position.ticket,
                                      price_open=position.price_open,
                                      open_time=time_string,
                                      type=self.POSITION_TYPES[position.type],
                                      volume=position.volume,
                                      stop_loss=position.sl,
                                      stop_gain=position.tp,
                                      magic=position.magic,
                                      profit=position.profit))
        return positions

    def get_position(self, ticket: int) -> Position:
        mt5positions = mt5.positions_get()

        for position in mt5positions:
            if position.ticket == ticket:
                comment = position.comment.split(" ")
                timeframe = comment[1] if len(comment) > 1 else ""
                strategy = comment[0] if len(comment) > 0 else ""
                datetime_string = self.format_timestamp(position.time)
                return Position(symbol=position.symbol,
                                timeframe=timeframe,
                                strategy=strategy,
                                ticket=position.ticket,
                                price_open=position.price_open,
                                open_time=datetime_string,
                                type=self.POSITION_TYPES[position.type],
                                volume=position.volume,
                                stop_loss=position.sl,
                                stop_gain=position.tp,
                                magic=position.magic,
                                profit=position.profit)

    def format_timestamp(self, timestamp: int) -> str:
        return str(datetime.utcfromtimestamp(float(timestamp + self.delta_timezone * 3.6e3)))

    def get_orders(self) -> List[Order]:
        mt5orders = mt5.orders_get()
        orders = []
        # ONLY PENDING ORDERS
        for order in mt5orders:
            if order.type_filling != 2:  # NOT PENDING ORDER
                continue
            datetime_string = self.format_timestamp(order.time_setup)
            orders.append(Order(symbol=order.symbol,
                                ticket=order.ticket,
                                placed_time=datetime_string,
                                type=order.type,
                                volume=order.volume_current,
                                price_open=order.price_open,
                                price_stop_limit=order.price_stoplimit,
                                stop_loss=order.sl,
                                stop_gain=order.tp,
                                magic=order.magic))
        return orders

    def get_trade_result(self, ticket: int) -> TradeResult:
        commission, swap, fee, profit = 0, 0, 0, 0
        deals = mt5.history_deals_get(position=ticket)
        for deal in deals:
            commission += deal.commission
            swap += deal.swap
            fee += deal.fee
            profit += deal.profit
        open_time = self.format_timestamp(deals[0].time)
        open_price = deals[0].price
        close_time = self.format_timestamp(deals[1].time) if len(deals) > 1 else ""
        close_price = deals[1].price if len(deals) > 1 else 0.0
        return TradeResult(open_time=open_time,
                           open_price=open_price,
                           close_time=close_time,
                           close_price=close_price,
                           ticket=ticket,
                           commission=commission,
                           fee=fee,
                           swap=swap,
                           profit=profit)

    def have_free_margin(self, order_type: OrderType, symbol: str, volume: float, price: float) -> bool:
        margin_free = mt5.account_info().margin_free
        margin_needed = mt5.order_calc_margin(self.ORDER_TYPES[order_type], symbol, volume, price)
        return margin_free > margin_needed or False

    def _is_buy_or_sell_order(self, order_type: OrderType) -> bool:
        return (self.ORDER_TYPES[order_type] == self.ORDER_TYPES[OrderType.BUY.value] or
                self.ORDER_TYPES[order_type] == self.ORDER_TYPES[OrderType.SELL.value])

    def open_position(self, request: OrderSendRequest) -> OrderSendResponse or None:
        is_to_execute = True
        status = False
        ticket = request.ticket
        code = 0
        comment = ""

        price = mt5.symbol_info(request.symbol).bid
        if request.order_type == mt5.ORDER_TYPE_BUY:
            price = mt5.symbol_info(request.symbol).ask

        if not self._is_buy_or_sell_order(request.order_type.value):
            comment = f"The Order Type ({request.order_type.value}) is neither BUY nor SELL"
            is_to_execute = False

        if not self.have_free_margin(request.order_type.value, request.symbol, request.volume, price):
            comment = f"{request.symbol} - Do not have free margin for volume {request.volume} at price {price}"
            is_to_execute = False

        if is_to_execute:
            request_position_open_atmarket = {
                "action": self.ORDER_EXECUTION[request.action.value],
                "symbol": request.symbol,
                "volume": request.volume,
                "type": self.ORDER_TYPES[request.order_type.value],
                "price": price,
                "sl": request.sl,
                "tp": request.tp,
                "deviation": request.deviation,
                "magic": request.magic,
                "comment": request.comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request_position_open_atmarket)
            status = result.retcode == 10009
            ticket = result.order
            code = result.retcode
            comment = result.comment

        return OrderSendResponse(symbol=request.symbol,
                                 action=request.action,
                                 order_type=request.order_type,
                                 status=status,
                                 ticket=ticket,
                                 code=code,
                                 comment=comment)

    def close_position(self, request: OrderSendRequest) -> OrderSendResponse or None:
        symbol_attr = self.get_symbol_attributes(request.symbol)

        is_to_execute = True
        status = False
        ticket = request.ticket
        code = 0
        comment = ""

        position = self.get_position(request.ticket)
        if position is None:
            comment = f"The Position ({ticket}) is already Closed"
            is_to_execute = False

        price = symbol_attr.ask
        order_type = self.ORDER_TYPES[OrderType.BUY.value]
        if self.ORDER_TYPES[request.order_type.value] == self.ORDER_TYPES[OrderType.BUY.value]:
            order_type = self.ORDER_TYPES[OrderType.SELL.value]
            price = symbol_attr.bid

        if is_to_execute:
            request_position_close = {
                "action": self.ORDER_EXECUTION[request.action.value],
                "symbol": request.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": request.ticket,
                "price": price,
                "deviation": request.deviation,
                "magic": request.magic,
                "comment": request.comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request_position_close)
            status = result.retcode == 10009
            ticket = result.request.position
            code = result.retcode
            comment = result.comment
        return OrderSendResponse(symbol=request.symbol,
                                 action=request.action,
                                 order_type=request.order_type,
                                 status=status,
                                 ticket=ticket,
                                 code=code,
                                 comment=comment)

    def modify_position(self, request: OrderSendRequest) -> OrderSendResponse or None:
        request_position_modify = {
            "action": self.ORDER_EXECUTION[request.action.value],
            "position": request.ticket,
            "symbol": request.symbol,
            "magic": request.magic,
            "sl": request.sl,
            "tp": request.tp
        }
        result = mt5.order_send(request_position_modify)
        status = result.retcode == 10009
        return OrderSendResponse(symbol=request.symbol,
                                 action=request.action,
                                 order_type=request.order_type,
                                 status=status,
                                 ticket=result.order,
                                 code=result.retcode,
                                 comment=result.comment)

    def _is_pending_order(self, type_order: int) -> bool:
        return ((type_order == self.ORDER_TYPES[OrderType.BUY_LIMIT.value]) or
                (type_order == self.ORDER_TYPES[OrderType.BUY_STOP.value]) or
                (type_order == self.ORDER_TYPES[OrderType.BUY_STOP_LIMIT.value]) or
                (type_order == self.ORDER_TYPES[OrderType.SELL_LIMIT.value]) or
                (type_order == self.ORDER_TYPES[OrderType.SELL_STOP.value]) or
                (type_order == self.ORDER_TYPES[OrderType.SELL_STOP_LIMIT.value]))

    def send_pending_order_limit_stop(self, request: OrderSendRequest) -> OrderSendResponse or None:
        is_to_execute = True
        status = False
        ticket = 0
        code = 0
        comment = ""

        if not self._is_pending_order(self.ORDER_TYPES[request.order_type.value]):
            comment = f"The Order Type ({request.order_type.value}) is not a Pending Order"
            is_to_execute = False

        if not self.have_free_margin(request.order_type, request.symbol, request.volume, request.price):
            comment = f"{request.symbol} - Do not have free margin for volume {request.volume} at price {request.price}"
            is_to_execute = False

        if is_to_execute:
            request_send_order_limit = {
                "action": self.ORDER_EXECUTION[request.action.value],
                "symbol": request.symbol,
                "magic": request.magic,
                "volume": request.volume,
                "type": self.ORDER_EXECUTION[request.order_type.value],
                "stoplimit": request.limit_price,
                "price": request.price,
                "sl": request.sl,
                "tp": request.tp,
                "type_time": mt5.ORDER_TIME_GTC,
                "expiration": 0
            }
            result = mt5.order_send(request_send_order_limit)
            status = result.retcode == 10009
            ticket = result.request.position
            code = result.retcode
            comment = result.comment
        return OrderSendResponse(symbol=request.symbol,
                                 action=request.action,
                                 order_type=request.order_type,
                                 status=status,
                                 ticket=ticket,
                                 code=code,
                                 comment=comment)

    def modify_pending_order(self, request: OrderSendRequest) -> OrderSendResponse or None:
        request_order_modify = {
            "action": self.ORDER_TYPES[request.action.value],
            "symbol": request.symbol,
            "magic": request.magic,
            "order": request.ticket,
            "price": request.price,
            "stoplimit": request.stop_limit,
            "sl": request.sl,
            "tp": request.tp,
            "type_time": 0,
            "expiration": 0
        }
        result = mt5.order_send(request_order_modify)
        status = result.retcode == 10009
        return OrderSendResponse(symbol=request.symbol,
                                 action=request.action,
                                 order_type=request.order_type,
                                 status=status,
                                 ticket=result.order,
                                 code=result.retcode,
                                 comment=result.comment)

    def delete_pending_order(self, request: OrderSendRequest) -> OrderSendResponse or None:
        request_order_delete = {
            "action": self.ORDER_EXECUTION[request.action.value],
            "magic": request.magic,
            "order": request.ticket
        }
        result = mt5.order_send(request_order_delete)
        status = result == 10009
        return OrderSendResponse(symbol=request.symbol,
                                 action=request.action,
                                 order_type=request.order_type,
                                 status=status,
                                 ticket=result.order,
                                 code=result.retcode,
                                 comment=result.comment)
