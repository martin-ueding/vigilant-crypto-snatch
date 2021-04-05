import datetime

import pytest

from vigilant_crypto_snatch import datamodel
from vigilant_crypto_snatch import triggers

from . import mock_historical


@pytest.fixture
def true_trigger() -> triggers.TrueTrigger:
    session = datamodel.open_memory_db_session()
    source = mock_historical.MockHistorical()
    market = mock_historical.MockMarketplace()
    true_trigger = triggers.TrueTrigger(session, source, market, "BTC", "EUR", 25.0, 10)
    return true_trigger


def test_triggered(true_trigger: triggers.TrueTrigger) -> None:
    # This trigger type must always be triggered.
    assert true_trigger.is_triggered(datetime.datetime.now())


def test_cooled_off(true_trigger: triggers.TrueTrigger) -> None:
    # There are no trades in the DB yet.
    assert true_trigger.has_cooled_off(datetime.datetime.now())


def test_waiting(true_trigger: triggers.TrueTrigger) -> None:
    now = datetime.datetime.now()
    session = true_trigger.session
    trade = datamodel.Trade(
        timestamp=now,
        trigger_name=true_trigger.get_name(),
        volume_coin=1.0,
        volume_fiat=1.0,
        coin="BTC",
        fiat="EUR",
    )
    session.add(trade)
    session.commit()
    assert not true_trigger.has_cooled_off(now)


def test_trade(true_trigger: triggers.TrueTrigger) -> None:
    now = datetime.datetime.now()
    true_trigger.fire(now)
    session = true_trigger.session
    assert session.query(datamodel.Trade).count() == 1
    assert true_trigger.market.orders == 1
