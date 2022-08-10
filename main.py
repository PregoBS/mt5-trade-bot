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
    # EXTRACT DATA AS A PANDAS DATAFRAME
    dataframe = mt5api.create_dataframe_from_bars("BTCUSD", mt5api.TIMEFRAME.H1, 0, 100)
    print(dataframe.tail(3))
    # ADDING INDICATORS
    indicators_manager = indicators.Manager()
    indicators_manager.add(indicators.EMA("EMA17", 17))
    indicators_manager.add(indicators.EMA("EMA34", 34))
    indicators_manager.add(indicators.EMA("EMA72", 72))
    # COMPUTING ALL INDICATORS
    dataframe = indicators_manager.calculate_all(dataframe)
    # ADDING STRATEGIES
    # -- THE STRATEGY MUST BE THE SUBJECT OF THE STRATEGY MANAGER
    # COMPUTING STRATEGIES
    # -- THE STRATEGY MANAGER MUST BE THE OBSERVER OF EACH STRATEGY
    # -- THE STRATEGY MANAGER MUST BE THE SUBJECT OF THE TRADE BOT
    # CREATE THE TRADE BOT
    # -- THE TRADE BOT MUST BE THE OBSERVER OF THE STRATEGY MANAGER
    # ----- IT WILL EXECUTE THE TRADES AS THE STRATEGY MANAGER UPDATES ITS STATE
    print(dataframe.tail(3))
    return api_disconnect(mt5api)


if __name__ == "__main__":
    main()
