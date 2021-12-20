import datetime

from vigilant_crypto_snatch.feargreed.alternateme import AlternateMeFearAndGreedIndex


def test_alternate_me() -> None:
    index = AlternateMeFearAndGreedIndex(test=True)
    assert index.get_value(datetime.datetime.now()) == 25
