import datetime
from typing import List
from typing import Optional

from ..core import Price
from ..core import Trade
from .interface import Datastore


class ListDatastore(Datastore):
    def __init__(self):
        self.trades = []
        self.prices = []

    def add_price(self, price: Price) -> None:
        self.prices.append(price)

    def add_trade(self, trade: Trade) -> None:
        self.trades.append(trade)

    def get_price_around(
        self,
        then: datetime.datetime,
        coin: str,
        fiat: str,
        tolerance: datetime.timedelta,
    ) -> Optional[Price]:
        self.prices.sort(key=lambda price: price.timestamp)
        for price in reversed(self.prices):
            if (
                price.coin == coin
                and price.fiat == fiat
                and then - tolerance <= price.timestamp <= then
            ):
                return price
        return None

    def was_triggered_since(
        self, trigger_name: str, coin: str, fiat: str, then: datetime.datetime
    ) -> bool:
        for trade in self.trades:
            if (
                trade.trigger_name == trigger_name
                and trade.coin == coin
                and trade.fiat == fiat
                and trade.timestamp > then
            ):
                return True
        return False

    def get_all_prices(self) -> List[Price]:
        return self.prices

    def get_all_trades(self) -> List[Trade]:
        return self.trades

    def clean_old(self, before: datetime.datetime) -> None:
        self.prices = [price for price in self.prices if price.timestamp >= before]
