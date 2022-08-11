from .mock_data import btc_dataframe
import indicators
from pandas import DataFrame
import pytest


@pytest.fixture
def dataframe() -> DataFrame:
    return btc_dataframe()


def test_add_indicator():
    indicators_manager = indicators.Manager()
    indicators_manager.add(indicators.EMA("EMA17", 17))
    indicators_manager.add(indicators.EMA("EMA72", 72))
    assert len(indicators_manager.indicators) == 2


def test_calculate_all_indicators(dataframe: DataFrame):
    indicators_manager = indicators.Manager()
    indicators_manager.add(indicators.EMA("EMA17", 17))
    indicators_manager.add(indicators.EMA("EMA72", 72))
    df = indicators_manager.calculate_all(dataframe)
    dataframe_columns = df.columns.to_list()
    assert "EMA17" in dataframe_columns
    assert "EMA72" in dataframe_columns
