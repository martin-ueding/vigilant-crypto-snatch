from vigilant_crypto_snatch.evaluation import make_dataframe_from_json
from vigilant_crypto_snatch.evaluation.price_data import download_hourly_data_stub


def test_make_dataframe_from_json() -> None:
    response = download_hourly_data_stub()
    df = make_dataframe_from_json(response["Data"])
    assert len(df) == 2
