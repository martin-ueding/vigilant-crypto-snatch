import abc
import dataclasses
import datetime
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

from .. import logger
from ..core import AssetPair
from ..core import Price


@dataclasses.dataclass()
class BitstampConfig:
    username: str
    key: str
    secret: str

    def to_primitives(self) -> Dict[str, Any]:
        return {"username": self.username, "key": self.key, "secret": self.secret}


@dataclasses.dataclass()
class KrakenWithdrawalConfig:
    coin: str
    target: str
    fee_limit_percent: float


@dataclasses.dataclass()
class KrakenConfig:
    key: str
    secret: str
    prefer_fee_in_base_currency: bool
    withdrawal: Dict[str, KrakenWithdrawalConfig]

    def to_primitives(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "secret": self.secret,
            "prefer_fee_in_base_currency": self.prefer_fee_in_base_currency,
            "withdrawal": {
                w.coin: {"target": w.target, "fee_limit_percent": w.fee_limit_percent}
                for w in self.withdrawal.values()
            },
        }


@dataclasses.dataclass()
class CCXTConfig:
    exchange: str
    parameters: dict

    def to_primitives(self) -> Dict[str, Any]:
        return {"exchange": self.exchange, "parameters": self.parameters}


class Marketplace(abc.ABC):
    def place_order(self, asset_pair: AssetPair, volume_coin: float) -> None:
        raise NotImplementedError()  # pragma: no cover

    def get_spot_price(self, asset_pair: AssetPair, now: datetime.datetime) -> Price:
        raise NotImplementedError()  # pragma: no cover

    def get_name(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    def get_balance(self) -> dict:
        raise NotImplementedError()  # pragma: no cover

    def get_withdrawal_fee(self, coin: str, volume: float) -> float:
        raise NotImplementedError(
            "Selected marketplace does not support withdrawal fee."
        )  # pragma: no cover

    def withdrawal(self, coin: str, volume: float) -> None:
        raise NotImplementedError(
            "Selected marketplace does not support withdrawal."
        )  # pragma: no cover


def check_and_perform_widthdrawal(market: Marketplace) -> None:
    balance = market.get_balance()
    for coin, balance_coin in balance.items():
        market.withdrawal(coin, balance_coin)


class BuyError(Exception):
    pass


class InsufficientFundsError(BuyError):
    pass


class TickerError(Exception):
    pass


class WithdrawalError(Exception):
    pass


def report_balances(market: Marketplace, subset: Optional[set[str]] = None) -> None:
    try:
        balance = market.get_balance()
    except NotImplementedError:
        return

    if subset is None:
        filtered_balances = balance
    else:
        filtered_balances = {
            currency: value
            for currency, value in balance.items()
            if currency in subset or value in subset
        }
    balances_formatted = ", ".join(
        f"{value} {currency}" for currency, value in sorted(filtered_balances.items())
    )
    logger.info(f"Your balances on {market.get_name()} are: {balances_formatted}")
