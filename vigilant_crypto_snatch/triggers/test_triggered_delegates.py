import datetime

from ..feargreed import AlternateMeFearAndGreedIndex
from .triggered_delegates import FearAndGreedIndexTriggeredDelegate


def test_fear_and_greed_triggered_delegate_true() -> None:
    index = AlternateMeFearAndGreedIndex(test=True)
    delegate = FearAndGreedIndexTriggeredDelegate(50, index)
    assert delegate.is_triggered(datetime.datetime(2021, 12, 22))


def test_fear_and_greed_triggered_delegate_false() -> None:
    index = AlternateMeFearAndGreedIndex(test=True)
    delegate = FearAndGreedIndexTriggeredDelegate(25, index)
    assert not delegate.is_triggered(datetime.datetime(2021, 12, 22))
