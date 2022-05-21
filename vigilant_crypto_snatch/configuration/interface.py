import dataclasses
from typing import Any
from typing import Dict
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

    def to_primitives(self) -> Dict[str, Any]:
        result = {
            "sleep": self.polling_interval,
            "marketplace": self.marketplace,
            "triggers": [trigger.to_primitives() for trigger in self.triggers],
        }

        if self.crypto_compare is not None:
            result["cryptocompare"] = self.crypto_compare.to_primitives()
        if self.kraken is not None:
            result["kraken"] = self.kraken.to_primitives()
        if self.bitstamp is not None:
            result["bitstamp"] = self.bitstamp.to_primitives()
        if self.telegram is not None:
            result["telegram"] = self.telegram.to_primitives()
        if self.ccxt is not None:
            result["ccxt"] = self.ccxt.to_primitives()
        if self.notify_run is not None:
            result["notify_run"] = self.notify_run.to_primitives()

        return result


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
