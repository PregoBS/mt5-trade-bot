from api.market_data_api import MarketDataAPI
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def dataframe() -> pd.DataFrame:
    index = np.array([
        '2022-08-01T20:00:00.000000000',
        '2022-08-01T21:00:00.000000000',
        '2022-08-01T22:00:00.000000000',
        '2022-08-01T23:00:00.000000000',
        '2022-08-02T00:00:00.000000000',
        '2022-08-02T01:00:00.000000000',
        '2022-08-02T02:00:00.000000000',
        '2022-08-02T03:00:00.000000000',
        '2022-08-02T04:00:00.000000000',
        '2022-08-02T05:00:00.000000000',
        '2022-08-02T06:00:00.000000000',
        '2022-08-02T07:00:00.000000000',
        '2022-08-02T08:00:00.000000000',
        '2022-08-02T09:00:00.000000000',
        '2022-08-02T10:00:00.000000000',
        '2022-08-02T11:00:00.000000000',
        '2022-08-02T12:00:00.000000000',
        '2022-08-02T13:00:00.000000000',
        '2022-08-02T14:00:00.000000000',
        '2022-08-02T15:00:00.000000000'
    ])
    data = np.array([
        [23174.26, 23419.77, 23174.26, 23274.51, 0, 4194, 550],
        [23274.31, 23447.25, 23167.0, 23190.25, 0, 3591, 550],
        [23189.76, 23248.75, 22952.24, 23004.24, 0, 3441, 550],
        [23000.25, 23080.76, 22824.24, 22917.77, 0, 3702, 550],
        [22909.75, 22921.28, 22787.26, 22857.77, 0, 3413, 550],
        [22855.20, 22902.76, 22756.24, 22865.77, 0, 2362, 550],
        [22865.06, 22907.25, 22843.77, 22856.85, 0, 2012, 550],
        [22857.25, 22938.71, 22856.76, 22878.56, 0, 2094, 550],
        [22877.51, 22920.25, 22718.25, 22893.51, 0, 3814, 550],
        [22893.01, 22913.36, 22777.75, 22814.26, 0, 3004, 550],
        [22812.26, 22844.26, 22660.45, 22878.56, 0, 3432, 550],
        [22715.70, 22877.01, 22700.25, 22719.75, 0, 3611, 550],
        [22864.75, 22978.24, 22850.13, 22866.27, 0, 3535, 550],
        [22888.01, 22913.77, 22667.75, 22887.27, 0, 3787, 550],
        [22741.24, 22888.75, 22705.51, 22741.01, 0, 6014, 550],
        [22797.24, 23155.51, 22668.38, 22798.83, 0, 8424, 550],
        [23029.25, 23106.23, 22814.24, 22981.51, 0, 8468, 550],
        [22985.75, 23457.00, 22953.26, 23383.25, 0, 7145, 550],
        [23382.76, 23438.25, 23144.74, 23186.75, 0, 5706, 550],
        [23186.74, 23278.30, 23075.71, 23125.23, 0, 3770, 550],
    ])
    return pd.DataFrame(data=data, columns=MarketDataAPI.DATAFRAME_COLUMNS, index=index)