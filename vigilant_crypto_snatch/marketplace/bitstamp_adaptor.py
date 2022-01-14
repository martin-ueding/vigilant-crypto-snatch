import datetime
import pprint

import bitstamp.client
import requests
import urllib3

from ..core import AssetPair
from ..core import Price
from ..myrequests import HttpRequestError
from .interface import BitstampConfig
from .interface import BuyError
from .interface import Marketplace


class BitstampMarketplace(Marketplace):
    def __init__(self, config: BitstampConfig):
        self.public_client = bitstamp.client.Public()
        self.trading_client = bitstamp.client.Trading(
            username=config.username, key=config.key, secret=config.secret
        )

    def place_order(self, asset_pair: AssetPair, volume: float) -> None:
        try:
            response = self.trading_client.buy_market_order(
                volume, base=asset_pair.coin, quote=asset_pair.fiat
            )
            pprint.pprint(response, compact=True, width=100)
        except bitstamp.client.BitstampError as e:
            raise BuyError() from e

    def get_spot_price(self, asset_pair: AssetPair, now: datetime.datetime) -> Price:
        try:
            ticker = self.public_client.ticker(
                base=asset_pair.coin, quote=asset_pair.fiat
            )
        except requests.exceptions.ChunkedEncodingError as e:
            raise HttpRequestError() from e
        except requests.exceptions.HTTPError as e:
            raise HttpRequestError() from e
        except urllib3.exceptions.ProtocolError as e:
            raise HttpRequestError() from e
        else:
            now = datetime.datetime.fromtimestamp(int(ticker["timestamp"]))
            price = Price(
                timestamp=now,
                last=ticker["last"],
                asset_pair=asset_pair,
            )
            return price

    def get_balance(self) -> dict:
        balance = self.trading_client.account_balance()
        out = {
            key[:3].upper(): value
            for key, value in sorted(balance.items())
            if key.endswith("available")
        }
        return out

    def get_name(self) -> str:
        return "Bitstamp"
