import datetime
from typing import Tuple

from ..core import Trade
from ..datastorage import ListDatastore
from ..historical import MockHistorical
from ..marketplace import MockMarketplace
from .concrete import BuyTrigger
from .factory import make_buy_trigger
from .interface import TriggerSpec


def make_true_trigger() -> Tuple[BuyTrigger, MockMarketplace]:
    datastore = ListDatastore()
    source = MockHistorical()
    market = MockMarketplace()
    trigger_spec = TriggerSpec(
        coin="BTC",
        fiat="EUR",
        volume_fiat=25.0,
        cooldown_minutes=10,
    )
    result = make_buy_trigger(datastore, source, market, trigger_spec)
    return result, market


def test_triggered() -> None:
    true_trigger, market = make_true_trigger()
    # This trigger type must always be triggered.
    assert true_trigger.is_triggered(datetime.datetime.now())


def test_cooled_off() -> None:
    true_trigger, market = make_true_trigger()
    # There are no trades in the DB yet.
    assert true_trigger.has_cooled_off(datetime.datetime.now())


def test_waiting() -> None:
    true_trigger, market = make_true_trigger()
    now = datetime.datetime.now()
    datastore = true_trigger.datastore
    trade = Trade(
        timestamp=now,
        trigger_name=true_trigger.get_name(),
        volume_coin=1.0,
        volume_fiat=1.0,
        coin="BTC",
        fiat="EUR",
    )
    datastore.add_trade(trade)
    assert not true_trigger.has_cooled_off(now)


def test_trade() -> None:
    true_trigger, market = make_true_trigger()
    now = datetime.datetime.now()
    true_trigger.fire(now)
    datastore = true_trigger.datastore
    assert len(datastore.get_all_trades()) == 1
    assert market.orders == 1
