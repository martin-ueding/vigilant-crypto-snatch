import datetime

import pytest
from vigilant_crypto_snatch import core
from vigilant_crypto_snatch import datastorage
from vigilant_crypto_snatch import triggers

from . import mock_historical


@pytest.fixture
def drop_trigger_with_percentage() -> triggers.BuyTrigger:
    datastore = datastorage.ListDatastore()
    source = mock_historical.MockHistorical()
    market = mock_historical.MockMarketplace()
    trigger_spec = {
        "coin": "BTC",
        "fiat": "EUR",
        "drop_percentage": 120.0,
        "percentage_fiat": 25.0,
        "cooldown_minutes": 10,
        "delay_minutes": 10,
    }
    result = triggers.make_buy_trigger(datastore, source, market, trigger_spec)
    return result


def test_buy(drop_trigger_with_percentage: triggers.BuyTrigger) -> None:
    drop_trigger_with_percentage.fire(datetime.datetime.now())
    resultset = drop_trigger_with_percentage.datastore.get_all_trades()
    assert len(resultset) == 1
    assert resultset[0].volume_fiat == 1000.0 * 0.25
