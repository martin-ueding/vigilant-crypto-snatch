import datetime

from vigilant_crypto_snatch import datamodel
from vigilant_crypto_snatch import logger


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

    def get_withdrawal_fee(self, coin: str, volume: float) -> float:
        raise NotImplementedError(
            "Selected marketplace does not support withdrawal fee."
        )

    def withdrawal(self, coin: str, volume: float) -> None:
        raise NotImplementedError("Selected marketplace does not support withdrawal.")


def check_and_perform_widthdrawal(market: Marketplace) -> None:
    balance = market.get_balance()
    for coin, balance_coin in balance.items():
        market.withdrawal(coin, balance_coin)


class BuyError(Exception):
    pass


class TickerError(Exception):
    pass


class WithdrawalError(Exception):
    pass


def report_balances(market: Marketplace) -> None:
    try:
        balance = market.get_balance()
    except NotImplementedError:
        pass
    else:
        balances_formatted = ", ".join(
            f"{value} {currency}" for currency, value in sorted(balance.items())
        )
        logger.info(f"Your balances on {market.get_name()} are: {balances_formatted}")
