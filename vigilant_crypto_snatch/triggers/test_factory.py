import datetime

from ..core import AssetPair
from ..datastorage import ListDatastore
from ..historical import MockHistorical
from ..marketplace import MockMarketplace
from ..triggers import make_buy_trigger
from .interface import TriggerSpec


def test_dca_trigger() -> None:
    datastore = ListDatastore()
    source = MockHistorical()
    market = MockMarketplace()
    trigger_spec = TriggerSpec(
        asset_pair=AssetPair(coin="BTC", fiat="EUR"),
        cooldown_minutes=10,
        volume_fiat=10,
    )
    trigger = make_buy_trigger(datastore, source, market, trigger_spec)
    assert trigger.is_triggered(datetime.datetime.now())


def disabled_test_fear_greed_trigger() -> None:
    datastore = ListDatastore()
    source = MockHistorical()
    market = MockMarketplace()
    trigger_spec = TriggerSpec(
        asset_pair=AssetPair(coin="BTC", fiat="EUR"),
        cooldown_minutes=10,
        volume_fiat=10,
        fear_and_greed_index_below=101,
    )
    trigger = make_buy_trigger(datastore, source, market, trigger_spec)
    assert trigger.is_triggered(datetime.datetime.now())
