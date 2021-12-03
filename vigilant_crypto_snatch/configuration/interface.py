from typing import List
from typing import Optional
from typing import Set

from vigilant_crypto_snatch import logger
from vigilant_crypto_snatch.core import TriggerSpec
from vigilant_crypto_snatch.historical import CryptoCompareConfig
from vigilant_crypto_snatch.marketplace.interface import BitstampConfig
from vigilant_crypto_snatch.marketplace.interface import KrakenConfig
from vigilant_crypto_snatch.telegram.sender import TelegramConfig


class Configuration:
    def get_polling_interval(self) -> int:
        raise NotImplementedError()  # pragma: no cover

    def get_crypto_compare_config(self) -> CryptoCompareConfig:
        raise NotImplementedError()  # pragma: no cover

    def get_kraken_config(self) -> Optional[KrakenConfig]:
        raise NotImplementedError()  # pragma: no cover

    def get_bitstamp_config(self) -> Optional[BitstampConfig]:
        raise NotImplementedError()  # pragma: no cover

    def get_telegram_config(self) -> Optional[TelegramConfig]:
        raise NotImplementedError()  # pragma: no cover

    def get_trigger_config(self) -> List[TriggerSpec]:
        raise NotImplementedError()  # pragma: no cover


def get_used_currencies(config: List[TriggerSpec]) -> Set[str]:
    result = set()
    for trigger_spec in config:
        result.add(trigger_spec.fiat)
        result.add(trigger_spec.coin)
    logger.debug(f"Currencies used in triggers: {result}")
    return result
