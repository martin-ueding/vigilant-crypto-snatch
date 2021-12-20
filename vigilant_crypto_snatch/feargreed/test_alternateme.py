import datetime

from vigilant_crypto_snatch.feargreed.alternateme import AlternateMeFearAndGreedIndex


def test_alternateme() -> None:
    index = AlternateMeFearAndGreedIndex()
    assert index.get_value(datetime.datetime.now()) == 25
