import datetime

from .triggers import *


def test_minutes_minutes() -> None:
    assert get_minutes({"test_minutes": 10}, "test") == 10


def test_minutes_hours() -> None:
    assert get_minutes({"test_hours": 10}, "test") == 10 * 60


def test_minutes_days() -> None:
    assert get_minutes({"test_days": 10}, "test") == 10 * 60 * 24


def test_minutes_none() -> None:
    assert get_minutes({}, "test") is None


def test_minutes_precedence() -> None:
    assert get_minutes({"test_days": 10, "test_minutes": 3}, "test") == 10 * 60 * 24


def test_get_start_none() -> None:
    assert get_start({}) is None


def test_get_start_date() -> None:
    assert get_start({"start": "2021-03-04"}) == datetime.datetime(2021, 3, 4, 0, 0, 0)


def test_get_start_datetime() -> None:
    assert get_start({"start": "2021-03-04 14:32"}) == datetime.datetime(
        2021, 3, 4, 14, 32, 0
    )
