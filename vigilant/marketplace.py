import datetime
import pprint
import sys
import typing

import bitstamp.client
import requests
import urllib3
import clikraken.api.private.place_order
import clikraken.api.public.ticker
import clikraken.api.api_utils
import clikraken.clikraken_utils
import clikraken.global_vars

import vigilant.capture
import vigilant.datamodel
import vigilant.logging


class Marketplace(object):
    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        raise NotImplementedError()

    def get_spot_price(self, coin: str, fiat: str) -> vigilant.datamodel.Price:
        raise NotImplementedError()


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

    def get_spot_price(self, coin: str, fiat: str) -> vigilant.datamodel.Price:
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
            price = vigilant.datamodel.Price(timestamp=now, last=ticker['last'])
            return price


class KrakenArgs(object):
    def __init__(self):
        self.raw = False
        self.csv = True


class KrakenMarketplace(Marketplace):
    def __init__(self):
        clikraken.clikraken_utils.load_config()
        clikraken.api.api_utils.load_api_keyfile()
        clikraken.global_vars.CSV_SEPARATOR = ';'

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        args = KrakenArgs()
        args.pair = self._make_pair(coin, fiat)
        args.type = 'buy'
        args.ordertype = 'market'
        args.volume = volume
        args.starttm = 0
        args.expiretm = 0
        args.leverage = None
        args.price = None
        args.userref = None
        args.viqc = None
        args.validate = False
        clikraken.api.private.place_order.place_order(args)

    def get_spot_price(self, coin: str, fiat: str) -> vigilant.datamodel.Price:
        args = KrakenArgs()
        args.pair = self._make_pair(coin, fiat)
        with vigilant.capture.Capturing() as output:
            clikraken.api.public.ticker.ticker(args)
        header, data = output
        ticker = {h: d for h, d in zip(header.split(';'), data.split(';'))}
        now = datetime.datetime.now()
        price = vigilant.datamodel.Price(timestamp=now, last=float(ticker['last']))
        return price

    def _make_pair(self, coin: str, fiat: str):
        if coin == 'btc':
            coin = 'xbt'
        pair = '{}{}'.format(coin.upper(), fiat.upper())
        return pair



class BuyError(Exception):
    pass


class TickerError(Exception):
    pass
