import api
import bot
from database import Database
import indicators
import numpy as np
import os
import pandas as pd
import signals
from signals.signal import SignalObj
import strategies
import sys
from typing import List


pd.set_option('display.max_columns', 500)   # número de colunas
pd.set_option('display.width', 1500)        # largura máxima da tabela


def api_connection(_api: api.MarketDataAPI) -> api.MarketDataAPI:
    try:
        assert _api.connect() is True
    except AssertionError:
        print("API didn't connect")
        sys.exit(1)
    return _api


def api_disconnect(_api: api.MarketDataAPI) -> None:
    try:
        assert _api.shutdown() is True
    except AssertionError:
        print("API didn't disconnect")
        sys.exit(1)
    return


def create_indicators_manager_with_indicators() -> indicators.Manager:
    manager = indicators.Manager()
    manager.add(indicators.EMA("EMA17", 17))
    manager.add(indicators.EMA("EMA34", 34))
    manager.add(indicators.EMA("EMA72", 72))
    manager.add(indicators.EMACrossover("EMACrossover17_34", 17, 34))
    return manager


def create_dataframe_with_indicators(_api: api.MarketDataAPI, symbol: str, timeframe: str, bars: int) -> pd.DataFrame:
    df = _api.create_dataframe_from_bars(symbol, timeframe, 12, bars)
    indicators_manager = create_indicators_manager_with_indicators()
    return indicators_manager.calculate_all(df)


def create_signals_manager_with_signals() -> signals.Manager:
    manager = signals.Manager()
    manager.add(signals.EMACrossover("EMACrossover", "EMACrossover17_34"))
    return manager


def create_signals_results(symbol: str, timeframe: str, dataframe: pd.DataFrame) -> List[SignalObj]:
    signals_manager = create_signals_manager_with_signals()
    return signals_manager.get_results(symbol, timeframe, dataframe)


def create_strategy_manager_with_strategies() -> strategies.Manager:
    manager = strategies.Manager()
    manager.add(strategies.EMACrossover("EMACrossover"))
    return manager


def main(symbol: str, timeframe: str) -> None:
    # CREATE API CONNECTION
    mt5api = api_connection(api.MetaTrader5API(delta_timezone=-6))
    # ---------------------------------------------------------------------------

    # CREATE DATABASE
    db = Database(f"{os.path.dirname(__file__)}/database.db")
    # ---------------------------------------------------------------------------

    # CREATE TRADE BOT
    trade_bot = bot.TradeBot()
    trade_bot.subscribe(db)
    # ---------------------------------------------------------------------------

    # CREATE ACCOUNT MANAGER - TODO 5
    # -- MUST BE A SUBJECT FOR THE TRADE BOT
    # -- IT WILL BE LISTENING FOR ANY CHANGES ON ACCOUNT
    # ----- LIKE PLACED ORDERS, OPENED POSITIONS, CLOSED POSITIONS
    # ---------------------------------------------------------------------------

    dataframe = create_dataframe_with_indicators(mt5api, symbol, timeframe, 100)
    print(dataframe.tail(3), end="\n\n")
    # ---------------------------------------------------------------------------

    signals_results = create_signals_results(symbol, timeframe, dataframe)
    print([s.name for s in signals_results], end="\n\n")
    # ---------------------------------------------------------------------------

    # CREATE STRATEGY MANAGER
    strategies_manager = create_strategy_manager_with_strategies()
    strategies_manager.subscribe_observer(trade_bot)
    # COMPUTING STRATEGIES
    strategies_manager.verify_all(symbol, timeframe, dataframe, signals_results)
    # ---------------------------------------------------------------------------

    return api_disconnect(mt5api)


if __name__ == "__main__":
    main("US500", "D1")
