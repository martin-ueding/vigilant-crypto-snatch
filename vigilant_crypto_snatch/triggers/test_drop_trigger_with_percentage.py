import datetime

import pytest

from . import BuyTrigger
from . import make_buy_trigger
from .. import datastorage
from ..historical.mock import MockHistorical
from ..marketplace.mock import MockMarketplace


@pytest.fixture
def drop_trigger_with_percentage() -> BuyTrigger:
    datastore = datastorage.ListDatastore()
    source = MockHistorical()
    market = MockMarketplace()
    trigger_spec = {
        "coin": "BTC",
        "fiat": "EUR",
        "drop_percentage": 120.0,
        "percentage_fiat": 25.0,
        "cooldown_minutes": 10,
        "delay_minutes": 10,
    }
    result = make_buy_trigger(datastore, source, market, trigger_spec)
    return result


def test_buy(drop_trigger_with_percentage: BuyTrigger) -> None:
    drop_trigger_with_percentage.fire(datetime.datetime.now())
    resultset = drop_trigger_with_percentage.datastore.get_all_trades()
    assert len(resultset) == 1
    assert resultset[0].volume_fiat == 1000.0 * 0.25
