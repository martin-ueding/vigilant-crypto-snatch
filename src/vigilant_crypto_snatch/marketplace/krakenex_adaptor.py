import datetime
import typing

import krakenex
import vigilant_crypto_snatch.datamodel

from . import marketplace

from vigilant_crypto_snatch import logger


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
    def __init__(self, api_key: str, api_secret: str, withdrawal_config: dict):
        # self.api_key = api_key
        # self.api_secret = api_secret
        self.handle = krakenex.API(api_key, api_secret)
        self.withdrawal_config = withdrawal_config

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
        return {
            map_kraken_to_normal(currency): float(value)
            for currency, value in answer["result"].items()
        }

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        answer = self.handle.query_private(
            "AddOrder",
            {
                "pair": f"{map_normal_to_kraken(coin)}{fiat}",
                "ordertype": "market",
                "type": f"buy",
                "volume": str(volume),
                # 'validate': 'validate',
            },
        )
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
