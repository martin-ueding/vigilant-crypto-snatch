import datetime

from .. import core
from .interface import Marketplace


class MockMarketplace(Marketplace):
    def __init__(self):
        super().__init__()
        self.orders = 0
        self.prices = 0
        self.balances = {"EUR": 1000.0}

    def get_balance(self) -> dict:
        return self.balances

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        self.orders += 1

    def get_name(self) -> str:
        return "Mock"

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> core.Price:
        self.prices += 1
        then = datetime.datetime.now()
        return core.Price(
            timestamp=then,
            last=100,
            coin=coin,
            fiat=fiat,
        )
