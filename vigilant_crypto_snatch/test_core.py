import datetime

from .core import AssetPair
from .core import Price
from .core import Trade


def test_price() -> None:
    price = Price(
        timestamp=datetime.datetime.now(),
        last=10.0,
        asset_pair=AssetPair(coin="BTC", fiat="EUR"),
    )
    str(price)
    repr(price)


def test_trade() -> None:
    trade = Trade(datetime.datetime.now(), "Test", 10.0, 10.0, AssetPair("BTC", "EUR"))
    str(trade)
    repr(trade)
    d = trade.to_dict()
    assert isinstance(d, dict)
