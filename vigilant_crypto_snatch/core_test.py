import datetime

from .core import Price
from .core import Trade


def test_price() -> None:
    price = Price(timestamp=datetime.datetime.now(), last=10.0, coin="BTC", fiat="EUR")
    str(price)
    repr(price)


def test_trade() -> None:
    trade = Trade(datetime.datetime.now(), "Test", 10.0, 10.0, "BTC", "EUR")
    str(trade)
    repr(trade)
    d = trade.to_dict()
    assert isinstance(d, dict)
