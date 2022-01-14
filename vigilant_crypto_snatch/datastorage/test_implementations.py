import datetime

import pytest

from ..core import AssetPair
from ..core import Price
from ..core import Trade
from .interface import Datastore
from .list_store import ListDatastore
from .sqlalchemy_store import SqlAlchemyDatastore


@pytest.fixture(params=[ListDatastore, SqlAlchemyDatastore])
def datastore(request) -> Datastore:
    return request.param()


def test_store_price(datastore: Datastore) -> None:
    price = Price(datetime.datetime.now(), 12.3, AssetPair("BTC", "EUR"))
    assert datastore.get_all_prices() == []
    datastore.add_price(price)
    assert datastore.get_all_prices() == [price]


def test_store_trade(datastore: Datastore) -> None:
    trade = Trade(datetime.datetime.now(), "Test", 12.3, 43.2, AssetPair("BTC", "EUR"))
    assert datastore.get_all_trades() == []
    datastore.add_trade(trade)
    assert datastore.get_all_trades() == [trade]


def test_was_triggered_since(datastore: Datastore) -> None:
    now = datetime.datetime.now()
    trade = Trade(now, "Test", 12.3, 43.2, AssetPair("BTC", "EUR"))
    datastore.add_trade(trade)
    assert not datastore.was_triggered_since(trade.trigger_name, trade.asset_pair, now)
    assert not datastore.was_triggered_since(
        trade.trigger_name, trade.asset_pair, now + datetime.timedelta(seconds=1)
    )
    assert datastore.was_triggered_since(
        trade.trigger_name, trade.asset_pair, now - datetime.timedelta(seconds=1)
    )


def test_get_price_around(datastore: Datastore) -> None:
    now = datetime.datetime.now()
    price = Price(now, 12.3, AssetPair("BTC", "EUR"))
    datastore.add_price(price)
    assert (
        datastore.get_price_around(
            now + datetime.timedelta(seconds=1),
            price.asset_pair,
            datetime.timedelta(seconds=2),
        )
        == price
    )
    assert (
        datastore.get_price_around(
            now + datetime.timedelta(seconds=0),
            price.asset_pair,
            datetime.timedelta(seconds=2),
        )
        == price
    )
    assert (
        datastore.get_price_around(
            now + datetime.timedelta(seconds=10),
            price.asset_pair,
            datetime.timedelta(seconds=2),
        )
        is None
    )


def test_clean_old(datastore: Datastore) -> None:
    then = datetime.datetime(2021, 1, 1)
    now = datetime.datetime(2021, 1, 2)
    assert len(datastore.get_all_prices()) == 0
    datastore.clean_old(now)
    assert len(datastore.get_all_prices()) == 0
    price = Price(then, 12.3, AssetPair("BTC", "EUR"))
    datastore.add_price(price)
    assert len(datastore.get_all_prices()) == 1
    datastore.clean_old(now)
    assert len(datastore.get_all_prices()) == 0
