import datetime

from . import yaml_configuration
from ..triggers import TriggerSpec


def test_minutes_minutes() -> None:
    assert yaml_configuration.get_minutes({"test_minutes": 10}, "test") == 10


def test_minutes_hours() -> None:
    assert yaml_configuration.get_minutes({"test_hours": 10}, "test") == 10 * 60


def test_minutes_days() -> None:
    assert yaml_configuration.get_minutes({"test_days": 10}, "test") == 10 * 60 * 24


def test_minutes_none() -> None:
    assert yaml_configuration.get_minutes({}, "test") is None


def test_minutes_precedence() -> None:
    assert (
        yaml_configuration.get_minutes({"test_days": 10, "test_minutes": 3}, "test")
        == 10 * 60 * 24
    )


def test_get_start_none() -> None:
    assert yaml_configuration.get_start({}) is None


def test_get_start_date() -> None:
    assert yaml_configuration.get_start({"start": "2021-03-04"}) == datetime.datetime(
        2021, 3, 4, 0, 0, 0
    )


def test_get_start_datetime() -> None:
    assert yaml_configuration.get_start(
        {"start": "2021-03-04 14:32"}
    ) == datetime.datetime(2021, 3, 4, 14, 32, 0)


def test_parse_trigger_spec_drop_fixed() -> None:
    target = TriggerSpec(
        name="Large drops",
        coin="BTC",
        fiat="EUR",
        cooldown_minutes=24 * 60,
        delay_minutes=7 * 24 * 60,
        drop_percentage=15,
        volume_fiat=100.0,
        percentage_fiat=None,
        start=None,
    )

    spec_dict = dict(
        coin="btc",
        cooldown_days=1,
        delay_days=7,
        drop_percentage=15,
        fiat="eur",
        name="Large drops",
        volume_fiat=100.0,
    )
    actual = yaml_configuration.parse_trigger_spec(spec_dict)

    assert target == actual


def test_parse_trigger_spec_time_ratio() -> None:
    target = TriggerSpec(
        name=None,
        coin="BTC",
        fiat="EUR",
        cooldown_minutes=24 * 60,
        delay_minutes=None,
        drop_percentage=None,
        volume_fiat=None,
        percentage_fiat=25,
        start=None,
    )

    spec_dict = dict(
        coin="btc", cooldown_days=1, fiat="eur", name=None, percentage_fiat=25
    )
    actual = yaml_configuration.parse_trigger_spec(spec_dict)

    assert target == actual
