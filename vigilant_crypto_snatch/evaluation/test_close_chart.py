import tempfile

from vigilant_crypto_snatch.evaluation.close_chart import make_close_chart
from vigilant_crypto_snatch.evaluation.price_data import make_test_dataframe


def test_make_close_chart() -> None:
    df = make_test_dataframe()
    chart = make_close_chart(df, "BTC", "EUR")
    with tempfile.TemporaryFile(mode="w") as f:
        chart.save(f, format="json")
