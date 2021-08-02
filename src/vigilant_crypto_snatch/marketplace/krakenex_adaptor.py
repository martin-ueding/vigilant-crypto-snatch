import datetime
import typing

import krakenex
import vigilant_crypto_snatch.datamodel
from vigilant_crypto_snatch import logger

from . import marketplace


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


class KrakenexMarketplace(marketplace.Marketplace):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        withdrawal_config: dict,
        prefer_fee_in_base_currency: bool,
        dry_run: bool,
    ):
        self.handle = krakenex.API(api_key, api_secret)
        self.withdrawal_config = withdrawal_config
        self.prefer_fee_in_base_currency = prefer_fee_in_base_currency
        self.dry_run = dry_run

    def get_name(self) -> str:
        return "Kraken"

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> vigilant_crypto_snatch.datamodel.Price:
        answer = self.handle.query_public(
            "Ticker", {"pair": f"{map_normal_to_kraken(coin)}{fiat}"}
        )
        raise_error(answer, marketplace.TickerError)
        close = float(list(answer["result"].values())[0]["c"][0])
        logger.debug(f"Retrieved {close} for {fiat}/{coin} from Krakenex.")
        price = vigilant_crypto_snatch.datamodel.Price(
            timestamp=now, last=close, coin=coin, fiat=fiat
        )
        return price

    def get_balance(self) -> dict:
        answer = self.handle.query_private("Balance")
        raise_error(answer, marketplace.TickerError)
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
        if self.dry_run:
            arguments["validate"] = "true"
        answer = self.handle.query_private("AddOrder", arguments)
        raise_error(answer, marketplace.BuyError)
        marketplace.check_and_perform_widthdrawal(self)

    def get_withdrawal_fee(self, coin: str, volume: float) -> float:
        target = self.withdrawal_config[coin]["target"]
        answer = self.handle.query_private(
            "WithdrawInfo",
            {
                "asset": map_normal_to_kraken(coin),
                "amount": volume,
                "key": target,
            },
        )
        raise_error(answer, marketplace.WithdrawalError)
        fee = float(answer["result"]["fee"])
        logger.debug(f"Withdrawal fee for {coin} is {fee} {coin}.")
        return fee

    def withdrawal(self, coin: str, volume: float) -> None:
        if coin not in self.withdrawal_config:
            logger.debug(f"No withdrawal config for {coin}.")
            return
        target = self.withdrawal_config[coin]["target"]
        fee = self.get_withdrawal_fee(coin, volume)
        if fee / volume <= self.withdrawal_config[coin]["fee_limit_percent"] / 100:
            logger.info(
                f"Trying to withdraw {volume} {coin} as fee is just {fee} {coin} and below limit."
            )
            if self.dry_run:
                return
            answer = self.handle.query_private(
                "Withdraw",
                {
                    "asset": map_normal_to_kraken(coin),
                    "amount": volume,
                    "key": target,
                },
            )
            raise_error(answer, marketplace.WithdrawalError)
        else:
            logger.debug(
                f"Not withdrawing {volume} {coin} as fee is {fee} {coin} and above limit."
            )


def raise_error(answer: dict, exception: typing.Type[Exception]):
    if len(answer["error"]) > 0:
        raise exception(answer["error"])
