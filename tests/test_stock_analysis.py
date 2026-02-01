import pandas as pd
import pytest

from stock_analysis import add_metrics, fetch_prices, get_close


def test_add_metrics():
    data = {"Close": [10, 20, 30, 40, 50], "Adj Close": [10, 20, 30, 40, 50]}
    df = pd.DataFrame(data)

    df = add_metrics(df, 2)

    assert "return_daily" in df.columns
    assert "SMA_2" in df.columns
    assert df["SMA_2"].iloc[-1] == 45


def test_get_close_raises_when_missing_columns():
    df = pd.DataFrame({"Open": [1, 2, 3]})

    with pytest.raises(KeyError, match="Adj Close|Close"):
        get_close(df)


def test_fetch_prices_raises_when_download_returns_none():
    def fake_download(*_args, **_kwargs):
        return None

    with pytest.raises(RuntimeError, match="No data returned"):
        fetch_prices("AMZN", "5y", "1d", downloader=fake_download)
