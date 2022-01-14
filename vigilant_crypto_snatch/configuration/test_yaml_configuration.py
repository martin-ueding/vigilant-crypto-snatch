import copy
import datetime
import tempfile

import pytest
import yaml

from . import yaml_configuration
from ..core import AssetPair
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


def test_get_start_with_datetime() -> None:
    assert yaml_configuration.get_start(
        {"start": yaml.safe_load("2021-03-04")}
    ) == datetime.datetime(2021, 3, 4)


def test_get_start_with_unknown_type() -> None:
    with pytest.raises(RuntimeError):
        yaml_configuration.get_start({"start": 0})


def test_parse_trigger_spec_drop_fixed() -> None:
    target = TriggerSpec(
        name="Large drops",
        asset_pair=AssetPair("BTC", "EUR"),
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
        asset_pair=AssetPair("BTC", "EUR"),
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


def test_parse_trigger_spec_without_cooldown() -> None:
    spec_dict = dict(coin="btc", fiat="eur", name=None, percentage_fiat=25)
    with pytest.raises(RuntimeError):
        yaml_configuration.parse_trigger_spec(spec_dict)


def test_get_polling_interval() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write("sleep: 10")
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_polling_interval() == 10


trigger_config = """
triggers:
# This is a trigger with drops and a name.
- coin: btc
  cooldown_days: 1
  delay_days: 7
  drop_percentage: 15
  fiat: eur
  name: Large drops
  volume_fiat: 100.0
  
# This one is with drops, but doesn't contain a name.
- coin: btc
  cooldown_days: 1
  delay_days: 4
  drop_percentage: 10
  fiat: eur
  volume_fiat: 100.0
  start: 2021-12-12T04:12:00

# This uses the Fear & Greed index, as well as a start date.
- coin: btc
  cooldown_days: 1
  delay_days: 2
  drop_percentage: 5
  fiat: eur
  name: Small drops
  volume_fiat: 26.0
  fear_and_greed_index_below: 30
  start: 2021-12-12
  
# This one doesn't use drops and has a name.
- coin: btc
  cooldown_days: 20
  fiat: eur
  name: Regular
  volume_fiat: 26.0
  start: 2021-12-12T04:12Z
  
# This one doesn't use drops and has a name.
- coin: btc
  cooldown_days: 20
  fiat: eur
  name: Regular
  volume_fiat: 26.0
  start: 2021-12-12 04:12:12
"""


def test_get_trigger_config() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(trigger_config)
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        config.get_trigger_config()


def test_get_bitstamp_config_empty() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write("sleep: 1")
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_bitstamp_config() is None


bitstamp_config = """
bitstamp:
  key: test-key
  secret: test-secret
  username: test-username
"""


def test_get_bitstamp_config() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(bitstamp_config)
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_bitstamp_config() is not None


def test_get_kraken_config_empty() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write("sleep: 1")
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_kraken_config() is None


kraken_config_full = """
kraken:
  key: test-key
  secret: test-secret
  prefer_fee_in_base_currency: true
  withdrawal:
    BTC:
      target: test-target
      fee_limit_percent: 0.7
"""


def test_get_kraken_config_full() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(kraken_config_full)
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_kraken_config() is not None


kraken_config_minimal = """
kraken:
  key: test-key
  secret: test-secret
"""


def test_get_kraken_config_minimal() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(kraken_config_minimal)
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_kraken_config() is not None


def test_get_telegram_config_empty() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write("sleep: 1")
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_telegram_config() is None


telegram_config_minimal = """
telegram:
  token: test-token
  level: info
"""


def test_get_telegram_config_minimal() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(telegram_config_minimal)
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_telegram_config() is not None


telegram_config_full = """
telegram:
  chat_id: 0
  level: info
  token: test-token
"""


def test_get_telegram_config_full() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(telegram_config_full)
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_telegram_config() is not None


def test_loading_nonexistent_path() -> None:
    with pytest.raises(RuntimeError):
        yaml_configuration.YamlConfiguration("")


crypto_compare_config = """
cryptocompare:
  api_key: test-key
"""


def test_get_crypto_compare_config() -> None:
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(crypto_compare_config)
        f.close()
        config = yaml_configuration.YamlConfiguration(f.name)
        assert config.get_crypto_compare_config() is not None
