import datetime

import pytest

from .concrete import FailureTimeout


@pytest.fixture
def ft_blank() -> FailureTimeout:
    return FailureTimeout()


@pytest.fixture
def ft_failed_three_times() -> FailureTimeout:
    ft = FailureTimeout()
    now = datetime.datetime(2021, 1, 1, 0, 0, 0)
    ft.start(now)
    ft.start(now)
    ft.start(now)
    return ft


def test_blank(ft_blank: FailureTimeout) -> None:
    now = datetime.datetime(2021, 1, 1, 0, 0, 0)
    assert not ft_blank.has_timeout(now)


def test_reset(ft_failed_three_times: FailureTimeout) -> None:
    now = datetime.datetime(2021, 1, 1, 0, 0, 0)
    assert ft_failed_three_times.has_timeout(now)
    ft_failed_three_times.finish()
    assert not ft_failed_three_times.has_timeout(now)


def test_timeout(ft_failed_three_times: FailureTimeout) -> None:
    now = datetime.datetime(2021, 1, 1, 0, 0, 0)
    assert ft_failed_three_times.has_timeout(now)
    later = datetime.datetime(2021, 1, 2, 0, 0, 0)
    assert not ft_failed_three_times.has_timeout(later)
