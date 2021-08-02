import datetime
import pprint

import bitstamp.client
import requests
import urllib3
from vigilant_crypto_snatch import datamodel

from . import marketplace


class BitstampMarketplace(marketplace.Marketplace):
    def __init__(self, username: str, key: str, secret: str, dry_run: bool):
        self.public_client = bitstamp.client.Public()
        self.trading_client = bitstamp.client.Trading(
            username=username, key=key, secret=secret
        )
        self.dry_run = dry_run

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        if self.dry_run:
            return
        try:
            response = self.trading_client.buy_market_order(
                volume, base=coin, quote=fiat
            )
            pprint.pprint(response, compact=True, width=100)
        except bitstamp.client.BitstampError as e:
            raise marketplace.BuyError(str(e))

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> datamodel.Price:
        try:
            ticker = self.public_client.ticker(base=coin, quote=fiat)
        except requests.exceptions.ChunkedEncodingError as e:
            raise marketplace.TickerError(str(e))
        except requests.exceptions.HTTPError as e:
            raise marketplace.TickerError(str(e))
        except urllib3.exceptions.ProtocolError as e:
            raise marketplace.TickerError(str(e))
        else:
            now = datetime.datetime.fromtimestamp(int(ticker["timestamp"]))
            price = datamodel.Price(
                timestamp=now, last=ticker["last"], coin=coin, fiat=fiat
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
