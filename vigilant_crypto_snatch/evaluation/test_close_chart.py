import tempfile

from ..core import AssetPair
from .close_chart import make_close_chart
from .price_data import make_test_dataframe


def test_make_close_chart() -> None:
    df = make_test_dataframe()
    chart = make_close_chart(df, AssetPair("BTC", "EUR"))
    with tempfile.TemporaryFile(mode="w") as f:
        chart.save(f, format="json")
