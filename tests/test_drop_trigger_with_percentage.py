import datetime

import pytest

from vigilant_crypto_snatch import datamodel
from vigilant_crypto_snatch import triggers

from . import mock_historical


@pytest.fixture
def drop_trigger_with_percentage() -> triggers.BuyTrigger:
    session = datamodel.open_memory_db_session()
    source = mock_historical.MockHistorical()
    market = mock_historical.MockMarketplace()
    trigger_spec = {
        'coin': 'BTC',
        'fiat': 'EUR',
        'drop_percentage': 120.0,
        'percentage_fiat': 25.0,
        'cooldown_minutes': 10,
        'delay_minutes': 10,
    }
    result = triggers.make_buy_trigger(session, source, market, trigger_spec)
    return result


def test_buy(drop_trigger_with_percentage: triggers.BuyTrigger) -> None:
    drop_trigger_with_percentage.fire(datetime.datetime.now())
    resultset = drop_trigger_with_percentage.session.query(datamodel.Trade).one()
    assert resultset.volume_fiat == 1000.0 * 0.25
