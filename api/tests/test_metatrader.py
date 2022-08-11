from api.market_data_api import MarketDataAPI
from api.metatrader import MetaTrader5API
from datetime import datetime, timedelta
import pytest


@pytest.fixture
def api() -> MarketDataAPI:
    return MetaTrader5API(delta_timezone=-6)


@pytest.fixture
def today() -> datetime:
    return datetime.today()


@pytest.fixture
def symbol() -> str:
    return "EURUSD"


@pytest.fixture
def bars() -> int:
    return 30


def test_connect(api: MarketDataAPI) -> None:
    assert api.connect() is True


def test_shutdown(api: MarketDataAPI) -> None:
    assert api.connect() is True
    assert api.shutdown() is True


def test_create_dataframe_from_bars(api: MarketDataAPI, symbol: str, bars: int) -> None:
    assert api.connect() is True
    dataframe = api.create_dataframe_from_bars(symbol, "M5", 0, bars)
    assert dataframe is not None
    assert len(dataframe) == bars
    assert api.shutdown() is True


def test_do_not_create_dataframe_from_bars(api: MarketDataAPI, symbol: str, bars: int) -> None:
    assert api.connect() is True
    dataframe = api.create_dataframe_from_bars("invalid-symbol", "M5", 0, bars)
    assert dataframe is None
    assert api.shutdown() is True


def test_create_dataframe_from_date(api: MarketDataAPI, symbol: str, bars: int, today: datetime) -> None:
    assert api.connect() is True
    dataframe = api.create_dataframe_from_date(symbol, "D1", today - timedelta(days=bars), today)
    assert dataframe is not None
    # Weekends or holidays may not have data
    # The dataframe length should be smaller than the timedelta
    assert 15 <= len(dataframe) <= bars
    assert api.shutdown() is True


def test_do_not_create_dataframe_from_date(api: MarketDataAPI, symbol: str, bars: int, today: datetime) -> None:
    assert api.connect() is True
    dataframe = api.create_dataframe_from_date("invalid-symbol", "H1", today - timedelta(days=bars), today)
    assert dataframe is None
    assert api.shutdown() is True


def test_standardize_dataframe(api: MarketDataAPI, symbol: str, bars: int) -> None:
    assert api.connect() is True
    dataframe = api.create_dataframe_from_bars(symbol, "M15", 0, bars)
    assert dataframe is not None
    assert dataframe.columns.to_list().sort() == MarketDataAPI.DATAFRAME_COLUMNS.sort()
    assert api.shutdown() is True
