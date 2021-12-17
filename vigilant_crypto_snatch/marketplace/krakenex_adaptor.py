import datetime
from typing import Dict
from typing import Protocol
from typing import Type

import krakenex
import requests

from .. import logger
from ..core import Price
from ..myrequests import HttpRequestError
from .interface import BuyError
from .interface import KrakenConfig
from .interface import Marketplace
from .interface import TickerError
from .interface import WithdrawalError


class KrakenexInterface(Protocol):
    def query_public(self, command: str, parameters: Dict = None) -> Dict:
        raise NotImplementedError()  # pragma: no cover

    def query_private(self, command: str, parameters: Dict = None) -> Dict:
        raise NotImplementedError()  # pragma: no cover


mapping_normal_to_kraken = {"BTC": "XBT"}
mapping_kraken_to_normal = {
    kraken: normal for normal, kraken in mapping_normal_to_kraken.items()
}


def map_normal_to_kraken(coin: str) -> str:
    return mapping_normal_to_kraken.get(coin, coin)


def map_kraken_to_normal(coin: str) -> str:
    if len(coin) == 4 and coin[0] in "ZX":
        coin = coin[1:]
    return mapping_kraken_to_normal.get(coin, coin)


class KrakenexMarketplace(Marketplace):
    def __init__(self, config: KrakenConfig, handle: KrakenexInterface = None):
        if handle:
            self.handle = handle
        else:
            self.handle = krakenex.API(config.key, config.secret)
        self.withdrawal_config = config.withdrawal
        self.prefer_fee_in_base_currency = config.prefer_fee_in_base_currency

    def get_name(self) -> str:
        return "Kraken"

    def get_spot_price(self, coin: str, fiat: str, now: datetime.datetime) -> Price:
        try:
            answer = self.handle.query_public(
                "Ticker", {"pair": f"{map_normal_to_kraken(coin)}{fiat}"}
            )
        except requests.exceptions.ConnectionError as e:
            raise HttpRequestError("Connection error in Kraken Ticker") from e
        raise_error(answer, TickerError)
        close = float(list(answer["result"].values())[0]["c"][0])
        logger.debug(f"Retrieved {close} for {fiat}/{coin} from Krakenex.")
        price = Price(timestamp=now, last=close, coin=coin, fiat=fiat)
        return price

    def get_balance(self) -> dict:
        try:
            answer = self.handle.query_private("Balance")
        except requests.exceptions.ConnectionError as e:
            raise HttpRequestError("Connection error in Kraken Balance") from e
        raise_error(answer, TickerError)
        # The key `result` will only be present if the user has any balances.
        if "result" in answer:
            return {
                map_kraken_to_normal(currency): float(value)
                for currency, value in answer["result"].items()
            }
        else:
            return {}

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        arguments = {
            "pair": f"{map_normal_to_kraken(coin)}{fiat}",
            "ordertype": "market",
            "type": f"buy",
            "volume": str(volume),
            "oflags": "fcib" if self.prefer_fee_in_base_currency else "fciq",
        }
        try:
            answer = self.handle.query_private("AddOrder", arguments)
        except requests.exceptions.ConnectionError as e:
            raise HttpRequestError("Connection error in Kraken AddOrder") from e
        raise_error(answer, BuyError)

    def get_withdrawal_fee(self, coin: str, volume: float) -> float:
        target = self.withdrawal_config[coin].target
        try:
            answer = self.handle.query_private(
                "WithdrawInfo",
                {
                    "asset": map_normal_to_kraken(coin),
                    "amount": volume,
                    "key": target,
                },
            )
        except requests.exceptions.ConnectionError as e:
            raise HttpRequestError("Connection error in Kraken WithdrawInfo") from e
        raise_error(answer, WithdrawalError)
        fee = float(answer["result"]["fee"])
        logger.debug(f"Withdrawal fee for {coin} is {fee} {coin}.")
        return fee

    def withdrawal(self, coin: str, volume: float) -> None:
        if coin not in self.withdrawal_config:
            logger.debug(f"No withdrawal config for {coin}.")
            return
        if volume == 0:
            return
        target = self.withdrawal_config[coin].target
        fee = self.get_withdrawal_fee(coin, volume)
        if fee / volume <= self.withdrawal_config[coin].fee_limit_percent / 100:
            logger.info(
                f"Trying to withdraw {volume} {coin} as fee is just {fee} {coin} and below limit."
            )
            try:
                answer = self.handle.query_private(
                    "Withdraw",
                    {
                        "asset": map_normal_to_kraken(coin),
                        "amount": volume,
                        "key": target,
                    },
                )
            except requests.exceptions.ConnectionError as e:
                raise HttpRequestError("Connection error in Kraken Withdraw") from e
            raise_error(answer, WithdrawalError)
        else:
            logger.debug(
                f"Not withdrawing {volume} {coin} as fee is {fee} {coin} and above limit."
            )


def raise_error(answer: dict, exception: Type[Exception]):
    if len(answer["error"]) > 0:
        raise exception(answer["error"])
