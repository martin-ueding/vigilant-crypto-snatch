from .price_data import make_test_dataframe


def test_make_dataframe_from_json() -> None:
    df = make_test_dataframe()
    assert len(df) == 2
