from signals.ema_crossover import EMACrossover
from .mock_data import btc_dataframe
from pandas import DataFrame
import pytest


@pytest.fixture
def dataframe() -> DataFrame:
    return btc_dataframe()


def test_get_signal(dataframe: DataFrame) -> None:
    # Exponential Moving Average Crossover Signal
    ema_crossover = EMACrossover("EMACrossover", "EMACrossover_17_34")
    signal = ema_crossover.get_signal("BTCUSD", "M5", dataframe)
    assert signal.name == "EMACrossover"
    assert signal.symbol == "BTCUSD"
    assert signal.timeframe == "M5"
    assert signal.signal == 0
