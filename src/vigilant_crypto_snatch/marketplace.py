import datetime

from . import datamodel
from . import logger


class Marketplace(object):
    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        raise NotImplementedError()

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> datamodel.Price:
        raise NotImplementedError()

    def get_name(self) -> str:
        raise NotImplementedError()

    def get_balance(self) -> dict:
        raise NotImplementedError()


class BuyError(Exception):
    pass


class TickerError(Exception):
    pass


def report_balances(market: Marketplace) -> None:
    try:
        balance = market.get_balance()
    except NotImplementedError:
        pass
    else:
        balances_formatted = ', '.join(f'{value} {currency}' for currency, value in sorted(balance.items()))
        logger.info(f'Your balances on {market.get_name()} are: {balances_formatted}')