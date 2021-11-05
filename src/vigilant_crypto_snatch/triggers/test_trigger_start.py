import datetime

import pytest
from vigilant_crypto_snatch import datastorage

from . import BuyTrigger
from . import make_buy_trigger
from ..historical.mock import MockHistorical
from ..marketplace.mock import MockMarketplace


@pytest.fixture
def drop_trigger_with_start() -> BuyTrigger:
    datastore = datastorage.ListDatastore()
    source = MockHistorical()
    market = MockMarketplace()
    trigger_spec = {
        "coin": "BTC",
        "fiat": "EUR",
        "volume_fiat": 10.0,
        "cooldown_minutes": 10,
        "delay_minutes": 10,
        "start": "2021-07-16 00:00:00",
    }
    result = make_buy_trigger(datastore, source, market, trigger_spec)
    return result


def test_trigger_with_start(drop_trigger_with_start: BuyTrigger) -> None:
    before = datetime.datetime(2021, 7, 15, 0, 0, 0)
    after = datetime.datetime(2021, 7, 17, 0, 0, 0)
    assert not drop_trigger_with_start.has_cooled_off(before)
    assert drop_trigger_with_start.has_cooled_off(after)
