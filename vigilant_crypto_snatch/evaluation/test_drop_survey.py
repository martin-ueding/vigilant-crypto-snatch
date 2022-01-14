import tempfile

from ..core import AssetPair
from .drop_survey import make_survey_chart
from .price_data import make_test_dataframe


def test_make_survey_chart() -> None:
    data = make_test_dataframe()
    chart = make_survey_chart(data, (1, 3), (0.1, 0.3), AssetPair("BTC", "EUR"))
    with tempfile.TemporaryFile("w") as f:
        chart.save(f, format="json")
