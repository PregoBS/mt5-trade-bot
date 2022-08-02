from api.metatrader import MetaTrader5API, TimeFrame


def main():
    api = MetaTrader5API(delta_timezone=-6)
    assert api.connect()
    dataframe = api.create_dataframe_from_bars("BTCUSD", TimeFrame.H1, 0, 50)
    print(dataframe.tail())


if __name__ == "__main__":
    main()
