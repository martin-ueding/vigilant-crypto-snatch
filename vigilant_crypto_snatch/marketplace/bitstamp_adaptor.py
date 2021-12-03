import datetime
import pprint

import bitstamp.client
import requests
import urllib3

from ..core import Price
from .interface import BitstampConfig
from .interface import BuyError
from .interface import Marketplace
from .interface import TickerError


class BitstampMarketplace(Marketplace):
    def __init__(self, config: BitstampConfig):
        self.public_client = bitstamp.client.Public()
        self.trading_client = bitstamp.client.Trading(
            username=config.username, key=config.key, secret=config.secret
        )

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        try:
            response = self.trading_client.buy_market_order(
                volume, base=coin, quote=fiat
            )
            pprint.pprint(response, compact=True, width=100)
        except bitstamp.client.BitstampError as e:
            raise BuyError() from e

    def get_spot_price(self, coin: str, fiat: str, now: datetime.datetime) -> Price:
        try:
            ticker = self.public_client.ticker(base=coin, quote=fiat)
        except requests.exceptions.ChunkedEncodingError as e:
            raise TickerError() from e
        except requests.exceptions.HTTPError as e:
            raise TickerError() from e
        except urllib3.exceptions.ProtocolError as e:
            raise TickerError() from e
        else:
            now = datetime.datetime.fromtimestamp(int(ticker["timestamp"]))
            price = Price(timestamp=now, last=ticker["last"], coin=coin, fiat=fiat)
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
