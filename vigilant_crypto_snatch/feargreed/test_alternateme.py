import datetime

from .alternateme import AlternateMeFearAndGreedIndex


def test_alternate_me() -> None:
    index = AlternateMeFearAndGreedIndex(test=True)
    # assert index.get_value(datetime.date(2021, 12, 22)) == 45
    # assert index.get_value(datetime.date(2021, 12, 21)) == 27
