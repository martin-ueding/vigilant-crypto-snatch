import dataclasses

from vigilant_crypto_snatch.historical.concrete import CryptoCompareConfig
from vigilant_crypto_snatch.marketplace.factory import BitstampConfig
from vigilant_crypto_snatch.marketplace.factory import KrakenConfig
from vigilant_crypto_snatch.telegram.sender import TelegramConfig


class Configuration:
    def get_polling_interval(self) -> int:
        raise NotImplementedError()

    def get_crypto_compare_config(self) -> CryptoCompareConfig:
        raise NotImplementedError()

    def get_kraken_config(self) -> KrakenConfig:
        raise NotImplementedError()

    def get_bitstamp_config(self) -> BitstampConfig:
        raise NotImplementedError()

    def get_telegram_config(self) -> TelegramConfig:
        raise NotImplementedError()
