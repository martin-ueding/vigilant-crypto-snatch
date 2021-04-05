import datetime

from vigilant_crypto_snatch import triggers


def test_checkin():
    start = datetime.datetime(2021, 1, 1, 0, 0, 0)
    trigger = triggers.CheckinTrigger(start)
    assert not trigger.is_triggered(start)
    assert not trigger.has_cooled_off(start)

    morning = datetime.datetime(2021, 1, 1, 6, 1, 0)
    assert trigger.is_triggered(morning)
    assert trigger.has_cooled_off(morning)
    trigger.fire(morning)

    later = datetime.datetime(2021, 1, 1, 6, 2, 0)
    assert trigger.is_triggered(later)
    assert not trigger.has_cooled_off(later)