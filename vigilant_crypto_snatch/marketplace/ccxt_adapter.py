import datetime
from typing import Dict
from typing import List
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
        self.markets = self.exchange.load_markets()

    def place_order(self, asset_pair: AssetPair, volume: float) -> None:
        volume_coin = (
            volume / self.get_spot_price(asset_pair, datetime.datetime.now()).last
        )
        self.exchange.create_market_order(
            symbol=get_symbol(self.markets, asset_pair), side="buy", amount=volume_coin
        )

    def get_spot_price(self, asset_pair: AssetPair, now: datetime.datetime) -> Price:
        response = self.exchange.fetch_ticker(get_symbol(self.markets, asset_pair))
        return response["last"]

    def get_name(self) -> str:
        return f"{self.exchange.name} via CCXT"

    def get_balance(self) -> dict:
        response = self.exchange.fetch_balance()
        return response["total"]

    def get_withdrawal_fee(self, coin: str, volume: float) -> float:
        pass

    def withdrawal(self, coin: str, volume: float) -> None:
        pass


def get_symbol(markets: Dict[str, Dict], asset_pair: AssetPair) -> str:
    for market in markets.values():
        if market["base"] == asset_pair.coin and market["quote"] == asset_pair.fiat:
            return market["symbol"]
    else:
        raise RuntimeError(
            f"Could not find asset pair {asset_pair} among the available markets via CCXT."
        )
