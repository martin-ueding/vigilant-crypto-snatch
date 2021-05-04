import datetime

import pytest

from vigilant_crypto_snatch import datamodel
from vigilant_crypto_snatch import triggers

from . import mock_historical


@pytest.fixture
def drop_trigger() -> triggers.BuyTrigger:
    session = datamodel.open_memory_db_session()
    source = mock_historical.MockHistorical()
    market = mock_historical.MockMarketplace()
    trigger_spec = {
        'coin': 'BTC',
        'fiat': 'EUR',
        'drop_percentage': 120.0,
        'volume_fiat': 25.0,
        'cooldown_minutes': 10,
        'delay_minutes': 10,
    }
    result = triggers.make_buy_trigger(session, source, market, trigger_spec)
    return result


def test_triggered(drop_trigger: triggers.BuyTrigger) -> None:
    # The drop is so extreme that it can never be triggered.
    assert not drop_trigger.is_triggered(datetime.datetime.now())
    session = drop_trigger.session
    assert session.query(datamodel.Price).count() == 0
    assert drop_trigger.source.calls == 2


def test_cooled_off(drop_trigger: triggers.BuyTrigger) -> None:
    # There are no trades in the DB yet.
    assert drop_trigger.has_cooled_off(datetime.datetime.now())


def test_waiting(drop_trigger: triggers.BuyTrigger) -> None:
    now = datetime.datetime.now()
    session = drop_trigger.session
    trade = datamodel.Trade(
        timestamp=now,
        trigger_name=drop_trigger.get_name(),
        volume_coin=1.0,
        volume_fiat=1.0,
        coin="BTC",
        fiat="EUR",
    )
    session.add(trade)
    session.commit()
    assert not drop_trigger.has_cooled_off(now)
