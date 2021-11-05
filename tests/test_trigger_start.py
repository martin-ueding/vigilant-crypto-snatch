import datetime

import pytest
from vigilant_crypto_snatch import core
from vigilant_crypto_snatch import datastorage
from vigilant_crypto_snatch import triggers

from . import mock_historical


@pytest.fixture
def drop_trigger_with_start() -> triggers.BuyTrigger:
    datastore = datastorage.ListDatastore()
    source = mock_historical.MockHistorical()
    market = mock_historical.MockMarketplace()
    trigger_spec = {
        "coin": "BTC",
        "fiat": "EUR",
        "volume_fiat": 10.0,
        "cooldown_minutes": 10,
        "delay_minutes": 10,
        "start": "2021-07-16 00:00:00",
    }
    result = triggers.make_buy_trigger(datastore, source, market, trigger_spec)
    return result


def test_trigger_with_start(drop_trigger_with_start: triggers.BuyTrigger) -> None:
    before = datetime.datetime(2021, 7, 15, 0, 0, 0)
    after = datetime.datetime(2021, 7, 17, 0, 0, 0)
    assert not drop_trigger_with_start.has_cooled_off(before)
    assert drop_trigger_with_start.has_cooled_off(after)
