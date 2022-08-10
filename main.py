import api
import indicators
import pandas as pd
import numpy as np
import sys

pd.set_option('display.max_columns', 500)  # número de colunas
pd.set_option('display.width', 1500)      # largura máxima da tabela


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


def main() -> None:
    # CREATE API CONNECTION
    mt5api = api_connection(api.MetaTrader5API(delta_timezone=-6))
    # ---------------------------------------------------------------------------

    # CREATE ACCOUNT MANAGER - TODO 5
    # -- MUST BE A SUBJECT FOR THE TRADE BOT
    # -- IT WILL BE LISTENING FOR ANY CHANGES ON ACCOUNT
    # ----- LIKE PLACED ORDERS, OPENED POSITIONS, CLOSED POSITIONS
    # ---------------------------------------------------------------------------

    # EXTRACT DATA AS A PANDAS DATAFRAME
    dataframe = mt5api.create_dataframe_from_bars("BTCUSD", mt5api.TIMEFRAME.H1, 0, 100)
    print(dataframe.tail(3))
    # ---------------------------------------------------------------------------

    # ADDING INDICATORS
    indicators_manager = indicators.Manager()
    indicators_manager.add(indicators.EMA("EMA17", 17))
    indicators_manager.add(indicators.EMA("EMA34", 34))
    indicators_manager.add(indicators.EMA("EMA72", 72))
    # ---------------------------------------------------------------------------

    # COMPUTING ALL INDICATORS
    dataframe = indicators_manager.calculate_all(dataframe)
    print(dataframe.tail(3))
    # ---------------------------------------------------------------------------

    # ADDING SIGNALS - TODO 1
    # -- SIGNAL IS A SINGLE INDICATOR OR A COMBINATION OF INDICATORS INTERPRETED AS:
    # ----- BUY MOVEMENT SIGNAL: 1 | SELL MOVEMENT SIGNAL: -1 | NOTHING HAPPENING: 0
    # ---------------------------------------------------------------------------

    # COMPUTING SIGNALS - TODO 2
    # ---------------------------------------------------------------------------

    # ADDING STRATEGIES - TODO 3
    # -- THE STRATEGY MUST BE A SUBJECT OF THE STRATEGY MANAGER
    # -- THE STRATEGY IS A SINGLE SIGNAL OR A COMBINATION OF SIGNALS INTERPRETED AS:
    # ----- BUY EVENT | SELL EVENT | NOTHING TO DO | UPDATE STOPLOSS (TRAILING STOP) | CLOSE TRADE AT MARKET
    # ---------------------------------------------------------------------------

    # COMPUTING STRATEGIES - TODO 4
    # -- THE STRATEGY MANAGER MUST BE A OBSERVER OF EACH STRATEGY
    # -- THE STRATEGY MANAGER MUST BE A SUBJECT OF THE TRADE BOT
    # ---------------------------------------------------------------------------

    # CREATE THE TRADE BOT - TODO 6
    # -- THE TRADE BOT MUST BE A OBSERVER OF THE STRATEGY MANAGER
    # -- THE TRADE BOT MUST BE A OBSERVER OF THE ACCOUNT MANAGER
    # ----- IT WILL EXECUTE THE TRADES AS THE STRATEGY MANAGER UPDATES ITS STATE
    # ---------------------------------------------------------------------------

    # CREATE TRADE RESULTS - TODO 7
    # -- THE TRADE RESULTS MUST BE THE OBSERVER OF THE TRADE BOT
    # ----- IT WILL STORE ALL TRADE DATA IN DATABASE FOR ANALYSIS
    # ---------------------------------------------------------------------------
    return api_disconnect(mt5api)


if __name__ == "__main__":
    main()
