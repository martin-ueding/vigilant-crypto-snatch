import csv
import datetime
import subprocess
import typing

from . import clikraken_adaptor_api
from . import datamodel
from . import logging
from . import marketplace


_delimiter = ';'


class KrakenMarketplace(marketplace.Marketplace):
    def __init__(self):
        pass

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        command = ['clikraken',
                   '--csv', '--csvseparator', _delimiter,
                   'place',
                   '-p', clikraken_adaptor_api.make_asset_pair(coin, fiat),
                   '-t', 'market',
                   str(volume)]
        output = run_command(command, marketplace.TickerError)
        logging.write_log(output.split('\n'))

    def get_spot_price(self, coin: str, fiat: str) -> datamodel.Price:
        command = ['clikraken',
                   '--csv', '--csvseparator', _delimiter,
                   'ticker',
                   '-p', clikraken_adaptor_api.make_asset_pair(coin, fiat)]
        output = run_command(command, marketplace.TickerError)

        ticker = csv_to_dict(output)
        now = datetime.datetime.now()
        price = datamodel.Price(timestamp=now, last=float(ticker['last']), coin=coin, fiat=fiat)
        return price

    def get_name(self) -> str:
        return "Kraken"


def run_command(command: typing.List[str], exception: typing.Type[Exception]) -> str:
    try:
        run = subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise exception(e)

    output = run.stdout.decode()

    if 'ERROR' in output:
        raise marketplace.TickerError(output)
    if len(output.strip()) == 0:
        raise exception('No output from clikraken!')

    return output


def csv_to_dict(line: str) -> typing.Dict[str, str]:
    reader = csv.reader(line.split('\n'), delimiter=_delimiter)
    header = next(reader)
    values = next(reader)
    data = dict(zip(header, values))
    return data
