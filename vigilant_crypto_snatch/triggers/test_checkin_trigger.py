import datetime

from .concrete import CheckinTrigger


def test_checkin():
    start = datetime.datetime(2021, 1, 1, 0, 0, 0)
    trigger = CheckinTrigger(start)
    assert not trigger.is_triggered(start)

    morning = datetime.datetime(2021, 1, 1, 6, 1, 0)
    assert trigger.is_triggered(morning)
    trigger.fire(morning)

    later = datetime.datetime(2021, 1, 1, 6, 2, 0)
    assert not trigger.is_triggered(later)
