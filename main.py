from api.market_data_api import MarketDataAPI
from api.metatrader import MetaTrader5API, TimeFrame
import indicators
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 500)  # número de colunas
pd.set_option('display.width', 1500)      # largura máxima da tabela


def main():
    # CREATE META TRADER 5 API CONNECTION
    api = MetaTrader5API(delta_timezone=-6)
    assert api.connect()
    # EXTRACT DATA AS A PANDAS DATAFRAME
    dataframe = api.create_dataframe_from_bars("BTCUSD", TimeFrame.H1, 0, 100)
    print(dataframe.tail(3))
    # ADDING INDICATORS
    indicators_manager = indicators.Manager()
    indicators_manager.add(indicators.EMA("EMA17", 17))
    indicators_manager.add(indicators.EMA("EMA34", 34))
    indicators_manager.add(indicators.EMA("EMA72", 72))
    dataframe = indicators_manager.calculate_all(dataframe)
    print(dataframe.tail(3))


if __name__ == "__main__":
    main()
