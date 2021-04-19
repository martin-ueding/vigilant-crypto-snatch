import csv
import datetime
import subprocess
import typing
import logging
import shlex

from . import clikraken_adaptor_api
from . import datamodel
from . import marketplace
from . import logger


_delimiter = ";"


class KrakenMarketplace(marketplace.Marketplace):
    def __init__(self):
        pass

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        command = [
            "clikraken",
            "--csv",
            "--csvseparator",
            _delimiter,
            "place",
            "-p",
            clikraken_adaptor_api.make_asset_pair(coin, fiat),
            "-t",
            "market",
            "buy",
            f"{volume:.8f}",
        ]
        output = run_command(command, marketplace.BuyError)
        logger.info(f"Output from clikraken: {output}")

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> datamodel.Price:
        command = [
            "clikraken",
            "--csv",
            "--csvseparator",
            _delimiter,
            "ticker",
            "-p",
            clikraken_adaptor_api.make_asset_pair(coin, fiat),
        ]
        output = run_command(command, marketplace.TickerError)

        ticker = csv_to_dict(output)
        price = datamodel.Price(
            timestamp=now, last=float(ticker["last"]), coin=coin, fiat=fiat
        )
        return price

    def get_name(self) -> str:
        return "Kraken"


def run_command(command: typing.List[str], exception: typing.Type[Exception]) -> str:
    escaped = " ".join(map(shlex.quote, command))
    logger.debug(f"Running `{escaped}` …")
    try:
        run = subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise exception(e)

    stdout = run.stdout.decode().strip()
    stderr = run.stderr.decode().strip()
    if "ERROR" in stdout:
        raise exception(stdout)
    if "ERROR" in stderr:
        raise exception(stderr)
    if len(stdout.strip()) == 0:
        raise exception("No output from clikraken!")
    return stdout


def csv_to_dict(line: str) -> typing.Dict[str, str]:
    reader = csv.reader(line.split("\n"), delimiter=_delimiter)
    header = next(reader)
    values = next(reader)
    data = dict(zip(header, values))
    return data
