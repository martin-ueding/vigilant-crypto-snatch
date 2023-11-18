import datetime
from typing import Dict
from typing import List
from typing import Type

import ccxt

from .. import logger
from ..core import AssetPair
from ..core import Price
from .interface import BuyError
from .interface import CCXTConfig
from .interface import Marketplace


class CCXTMarketplace(Marketplace):
    def __init__(self, config: CCXTConfig):
        exchange_type: Type[ccxt.Exchange] = getattr(ccxt, config.exchange)
        self.exchange = exchange_type(config.parameters)
        logger.info("Loading available markets from CCXT exchange …")
        self.markets = self.exchange.load_markets()
        self.withdrawal_address = None

    def place_order(self, asset_pair: AssetPair, volume_coin: float) -> None:
        try:
            self.exchange.create_market_order(
                symbol=get_symbol(self.markets, asset_pair),
                side="buy",
                amount=volume_coin,
            )
        except ccxt.base.errors.InvalidOrder as e:
            raise BuyError("Order was invalid") from e

    def get_spot_price(self, asset_pair: AssetPair, now: datetime.datetime) -> Price:
        response: dict = self.exchange.fetch_ticker(
            get_symbol(self.markets, asset_pair)
        )
        result = Price(timestamp=now, last=response["last"], asset_pair=asset_pair)
        return result

    def get_name(self) -> str:
        return f"{self.exchange.name} via CCXT"

    def get_balance(self) -> dict:
        response = self.exchange.fetch_balance()
        return response["total"]

    def withdrawal(self, coin: str, volume: float) -> None:
        if self.withdrawal_address:
            self.exchange.withdraw(coin, volume, self.withdrawal_address)


def get_symbol(markets: Dict[str, Dict], asset_pair: AssetPair) -> str:
    for market in markets.values():
        if market["base"] == asset_pair.coin and market["quote"] == asset_pair.fiat:
            return market["symbol"]
    else:
        raise RuntimeError(
            f"Could not find asset pair {asset_pair} among the available markets via CCXT."
        )
