import dataclasses
from typing import List

from . import bitstamp_adaptor
from . import interface
from . import krakenex_adaptor


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
    withdrawal: List[KrakenWithdrawalConfig]


@dataclasses.dataclass()
class BitstampConfig:
    username: str
    key: str
    secret: str


def make_marketplace(
    marketplace_str: str, config: dict, dry_run: bool = False
) -> interface.Marketplace:
    if marketplace_str == "bitstamp":
        return bitstamp_adaptor.BitstampMarketplace(
            config["bitstamp"]["username"],
            config["bitstamp"]["key"],
            config["bitstamp"]["secret"],
            dry_run=dry_run,
        )
    elif marketplace_str == "kraken":
        return krakenex_adaptor.KrakenexMarketplace(
            config["kraken"]["key"],
            config["kraken"]["secret"],
            withdrawal_config=config["kraken"].get("withdrawal", {}),
            prefer_fee_in_base_currency=config["kraken"].get(
                "prefer_fee_in_base_currency", False
            ),
            dry_run=dry_run,
        )
    else:
        raise RuntimeError(f"Unknown market place {marketplace_str}!")
