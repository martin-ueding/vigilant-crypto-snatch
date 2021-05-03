import datetime

import pytest

from vigilant_crypto_snatch import datamodel
from vigilant_crypto_snatch import triggers

from . import mock_historical


@pytest.fixture
def drop_trigger_with_percentage() -> triggers.DropTriggerWithPercentage:
    session = datamodel.open_memory_db_session()
    source = mock_historical.MockHistorical()
    market = mock_historical.MockMarketplace()
    drop_trigger = triggers.DropTriggerWithPercentage(
        session, source, market, "BTC", "EUR", 0.25, 10, 120
    )
    return drop_trigger


def test_buy(drop_trigger_with_percentage: triggers.DropTriggerWithPercentage) -> None:
    drop_trigger_with_percentage.fire(datetime.datetime.now())
    resultset = drop_trigger_with_percentage.session.query(datamodel.Trade).one()
    assert resultset.volume_fiat == 1000.0 * 0.25
