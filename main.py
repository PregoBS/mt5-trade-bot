from api.market_data_api import MarketDataAPI
from api.metatrader import MetaTrader5API, TimeFrame
import indicators
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 500)  # número de colunas
pd.set_option('display.width', 1500)      # largura máxima da tabela


def main():
    api = MetaTrader5API(delta_timezone=-6)
    assert api.connect()
    dataframe = api.create_dataframe_from_bars("BTCUSD", TimeFrame.H1, 0, 100)
    print(dataframe.tail(3))
    print()
    ema17 = indicators.EMA("EMA17", 17)
    ema34 = indicators.EMA("EMA34", 34)
    ema72 = indicators.EMA("EMA72", 72)
    dataframe = ema17.calculate(dataframe)
    dataframe = ema34.calculate(dataframe)
    dataframe = ema72.calculate(dataframe)
    print(dataframe.tail(3))


if __name__ == "__main__":
    main()
