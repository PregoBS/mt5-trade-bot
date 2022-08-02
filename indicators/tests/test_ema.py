from .fixtures import btc_dataframe
from indicators.ema import EMA
from pandas import DataFrame
import pytest


@pytest.fixture
def dataframe() -> DataFrame:
    return btc_dataframe()


def test_calculate(dataframe: DataFrame) -> None:
    # Exponential Moving Average
    ema = EMA("EMA17", 17)
    df = ema.calculate(dataframe)
    assert "EMA17" in df.columns.to_list()

