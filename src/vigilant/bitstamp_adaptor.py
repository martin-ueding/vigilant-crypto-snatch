import datetime
import pprint

import bitstamp.client
import requests
import urllib3

import src.vigilant.datamodel
from src.vigilant.marketplace import Marketplace, BuyError, TickerError


class BitstampMarketplace(Marketplace):
    def __init__(self, username: str, key: str, secret: str):
        self.public_client = bitstamp.client.Public()
        self.trading_client = bitstamp.client.Trading(username=username, key=key, secret=secret)

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        try:
            response = self.trading_client.buy_market_order(volume, base=coin, quote=fiat)
            pprint.pprint(response, compact=True, width=100)
        except bitstamp.client.BitstampError as e:
            raise BuyError(str(e))

    def get_spot_price(self, coin: str, fiat: str) -> src.vigilant.datamodel.Price:
        try:
            ticker = self.public_client.ticker(base=coin, quote=fiat)
        except requests.exceptions.ChunkedEncodingError as e:
            raise TickerError(str(e))
        except requests.exceptions.HTTPError as e:
            raise TickerError(str(e))
        except urllib3.exceptions.ProtocolError as e:
            raise TickerError(str(e))
        else:
            now = datetime.datetime.fromtimestamp(int(ticker['timestamp']))
            price = src.vigilant.datamodel.Price(timestamp=now, last=ticker['last'], coin=coin, fiat=fiat)
            return price

    def get_name(self):
        return "Bitstamp"