from .mock_data import btc_dataframe
import signals
from pandas import DataFrame
import pytest


@pytest.fixture
def dataframe() -> DataFrame:
    return btc_dataframe()


def test_add_signal():
    signals_manager = signals.Manager()
    signals_manager.add(signals.EMACrossover("EMACrossover", "EMACrossover_17_34"))
    assert len(signals_manager.signals) == 1


def test_get_signals_results(dataframe: DataFrame):
    signals_manager = signals.Manager()
    signals_manager.add(signals.EMACrossover("EMACrossover", "EMACrossover_17_34"))
    results = signals_manager.get_results("BTCUSD", "M5", dataframe)
    assert len(results) == 1
    assert results[0].name == "EMACrossover"
    assert results[0].symbol == "BTCUSD"
    assert results[0].timeframe == "M5"
    assert results[0].value == 0
