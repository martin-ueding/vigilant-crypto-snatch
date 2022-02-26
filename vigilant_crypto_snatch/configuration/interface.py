from typing import List
from typing import Optional
from typing import Set

from .. import logger
from ..historical import CryptoCompareConfig
from ..marketplace import BitstampConfig
from ..marketplace import CCXTConfig
from ..marketplace import KrakenConfig
from ..notifications import NotifyRunConfig
from ..notifications import TelegramConfig
from ..triggers import TriggerSpec


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

    def get_ccxt_config(self) -> CCXTConfig:
        raise NotImplementedError()  # pragma: no cover

    def get_marketplace(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    def get_notify_run_config(self) -> Optional[NotifyRunConfig]:
        raise NotImplementedError()  # pragma: no cover


def get_used_currencies(config: List[TriggerSpec]) -> Set[str]:
    result = set()
    for trigger_spec in config:
        result.add(trigger_spec.asset_pair.fiat)
        result.add(trigger_spec.asset_pair.coin)
    logger.debug(f"Currencies used in triggers: {result}")
    return result
