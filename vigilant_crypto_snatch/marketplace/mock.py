import datetime

from ..core import AssetPair
from ..core import Price
from .interface import Marketplace


class MockMarketplace(Marketplace):
    def __init__(self):
        super().__init__()
        self.orders = 0
        self.prices = 0
        self.balances = {"EUR": 1000.0}

    def get_balance(self) -> dict:
        return self.balances

    def place_order(self, asset_pair: AssetPair, volume: float) -> None:
        self.orders += 1

    def get_name(self) -> str:
        return "Mock"

    def get_spot_price(self, asset_pair: AssetPair, now: datetime.datetime) -> Price:
        self.prices += 1
        then = datetime.datetime.now()
        return Price(timestamp=then, last=100, asset_pair=asset_pair)
