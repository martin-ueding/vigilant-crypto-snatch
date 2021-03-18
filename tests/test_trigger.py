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


def test_true_trigger_triggered(true_trigger: triggers.TrueTrigger) -> None:
    # This trigger type must always be triggered.
    assert true_trigger.is_triggered()


def test_true_trigger_cooled_off(true_trigger: triggers.TrueTrigger) -> None:
    # There are no trades in the DB yet.
    assert true_trigger.has_cooled_off()


def test_true_trigger_after_trade(true_trigger: triggers.TrueTrigger) -> None:
    true_trigger.fire()
    session = true_trigger.session
    assert session.query(datamodel.Trade).count() == 1
