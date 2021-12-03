import datetime

import pytest

from .interface import KrakenConfig
from .interface import TickerError
from .krakenex_adaptor import KrakenexMarketplace


def test_get_spot_price_success() -> None:
    config = KrakenConfig("mock", "mock", False, {})
    market = KrakenexMarketplace(config)
    now = datetime.datetime.now()
    price = market.get_spot_price("BTC", "EUR", now)
    assert price.timestamp == now
    assert price.coin == "BTC"
    assert price.fiat == "EUR"
    assert price.last == 50162.2


def test_get_spot_price_error() -> None:
    config = KrakenConfig("mock", "mock", False, {})
    market = KrakenexMarketplace(config)
    now = datetime.datetime.now()
    with pytest.raises(TickerError):
        price = market.get_spot_price("AAA", "AAA", now)
