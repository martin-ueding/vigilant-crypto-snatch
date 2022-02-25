import datetime
from typing import Type

import ccxt

from ..core import AssetPair
from ..core import Price
from .interface import CCXTConfig
from .interface import Marketplace


class CCXTMarketplace(Marketplace):
    def __init__(self, config: CCXTConfig):
        exchange_type: Type[ccxt.Exchange] = getattr(ccxt, config.exchange)
        self.exchange = exchange_type(config.parameters)

    def place_order(self, asset_pair: AssetPair, volume: float) -> None:
        pass

    def get_spot_price(self, asset_pair: AssetPair, now: datetime.datetime) -> Price:
        pass

    def get_name(self) -> str:
        return f"{self.exchange.name} via CCXT"

    def get_balance(self) -> dict:
        response = self.exchange.fetch_balance()
        return response["total"]

    def get_withdrawal_fee(self, coin: str, volume: float) -> float:
        pass

    def withdrawal(self, coin: str, volume: float) -> None:
        pass
