import datetime

import pytest

from ..configuration import parse_trigger_spec
from ..core import AssetPair
from ..datastorage import ListDatastore
from ..historical import MockHistorical
from ..marketplace import MockMarketplace
from .concrete import BuyTrigger
from .factory import make_buy_trigger
from .interface import TriggerSpec


@pytest.fixture
def drop_trigger_with_start() -> BuyTrigger:
    datastore = ListDatastore()
    source = MockHistorical()
    market = MockMarketplace()
    trigger_spec = TriggerSpec(
        asset_pair=AssetPair("BTC", "EUR"),
        volume_fiat=10.0,
        cooldown_minutes=10,
        start=datetime.datetime(2021, 7, 16, 9, 10, 34),
    )
    result = make_buy_trigger(datastore, source, market, trigger_spec)
    return result


def test_trigger_with_start(drop_trigger_with_start: BuyTrigger) -> None:
    before = datetime.datetime(2021, 7, 16, 9, 9, 10)
    after = datetime.datetime(2021, 7, 16, 9, 14, 0)
    assert not drop_trigger_with_start.has_cooled_off(before)
    assert drop_trigger_with_start.has_cooled_off(after)


def test_error() -> None:
    trigger_spec_dict = {
        "name": "DCA weekly BTC",
        "coin": "btc",
        "fiat": "busd",
        "cooldown_days": 7,
        "volume_fiat": 15,
        "start": datetime.datetime(2022, 5, 28, 9, 0),
    }
    trigger_spec = parse_trigger_spec(trigger_spec_dict)
    print(trigger_spec)
    datastore = ListDatastore()
    source = MockHistorical()
    market = MockMarketplace()
    trigger = make_buy_trigger(datastore, source, market, trigger_spec)
    before = datetime.datetime(2022, 5, 28, 0, 0, 49)
    after = datetime.datetime(2022, 7, 16, 9, 14, 0)
    assert not trigger.has_cooled_off(before)
    assert trigger.has_cooled_off(after)
