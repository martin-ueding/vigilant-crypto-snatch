import datetime

import clikraken.api
import clikraken.clikraken_utils
import clikraken.global_vars

import vigilant.capture
import vigilant.datamodel
from vigilant.marketplace import Marketplace


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
        args.leverage = 'none'
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
        price = vigilant.datamodel.Price(timestamp=now, last=float(ticker['last']), coin=coin, fiat=fiat)
        return price

    def get_name(self):
        return "Kraken"

    @classmethod
    def _make_pair(cls, coin: str, fiat: str) -> str:
        kraken_coin = coin
        if coin == 'BTC':
            kraken_coin = 'xbt'
        pair = '{}{}'.format(kraken_coin, fiat)
        return pair