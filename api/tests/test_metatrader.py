from api.metatrader import MetaTrader5API, TimeFrame
from datetime import datetime, timedelta


api = MetaTrader5API(delta_timezone=-5)
today = datetime.today()
symbol = "EURUSD"
bars = 30


def test_connect() -> None:
    assert api.connect() is True


def test_shutdown() -> None:
    assert api.connect() is True
    assert api.shutdown() is True


def test_create_dataframe_from_bars() -> None:
    assert api.connect() is True
    dataframe = api.create_dataframe_from_bars(symbol, TimeFrame.M5, 0, bars)
    assert len(dataframe) == bars
    assert api.shutdown() is True


def test_create_dataframe_from_date() -> None:
    assert api.connect() is True
    dataframe = api.create_dataframe_from_date(symbol, TimeFrame.D1, today + timedelta(days=-bars), today)
    # Weekends or holidays may not have data
    # The dataframe length should be smaller than the timedelta
    assert 15 <= len(dataframe) <= bars
    assert api.shutdown() is True


def test_standardize_dataframe() -> None:
    assert api.connect() is True
    dataframe = api.create_dataframe_from_bars(symbol, TimeFrame.M5, 0, bars)
    assert dataframe.columns.to_list().sort() == api.dataframe_columns.sort()
    assert api.shutdown() is True
