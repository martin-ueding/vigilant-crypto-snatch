import csv
import datetime
import subprocess

from . import datamodel
from . import marketplace
from . import clikraken_adaptor_api


_delimiter = ';'


class KrakenMarketplace(marketplace.Marketplace):
    def __init__(self):
        pass

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        pass

    def get_spot_price(self, coin: str, fiat: str) -> datamodel.Price:
        command = ['clikraken', '--csv', '--csvseparator', _delimiter, 'ticker', '-p',
                   clikraken_adaptor_api.make_asset_pair(coin, fiat)]
        try:
            run = subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise marketplace.TickerError(e)

        reader = csv.reader(run.stdout.decode().split('\n'), delimiter=_delimiter)
        header = next(reader)
        values = next(reader)
        ticker = dict(zip(header, values))
        now = datetime.datetime.now()
        price = datamodel.Price(timestamp=now, last=float(ticker['last']), coin=coin, fiat=fiat)
        return price

    def get_name(self):
        return "Kraken"
