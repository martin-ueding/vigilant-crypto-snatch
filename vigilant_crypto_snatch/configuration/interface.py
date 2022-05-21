import dataclasses
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


@dataclasses.dataclass()
class Configuration:
    polling_interval: int
    crypto_compare: CryptoCompareConfig
    triggers: List[TriggerSpec]
    marketplace: str
    kraken: Optional[KrakenConfig] = None
    bitstamp: Optional[BitstampConfig] = None
    telegram: Optional[TelegramConfig] = None
    ccxt: Optional[CCXTConfig] = None
    notify_run: Optional[NotifyRunConfig] = None


class ConfigurationFactory:
    def make_config(self) -> Configuration:
        raise NotImplementedError()  # pragma: no cover


def get_used_currencies(config: List[TriggerSpec]) -> Set[str]:
    result = set()
    for trigger_spec in config:
        result.add(trigger_spec.asset_pair.fiat)
        result.add(trigger_spec.asset_pair.coin)
    logger.debug(f"Currencies used in triggers: {result}")
    return result
