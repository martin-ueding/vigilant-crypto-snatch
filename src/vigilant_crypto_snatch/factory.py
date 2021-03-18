import logging
import os
import sys

import yaml

from . import (
    marketplace,
    bitstamp_adaptor,
    clikraken_adaptor_api,
    clikraken_adaptor_cli,
)


logger = logging.getLogger("vigilant_crypto_snatch")
config_path = os.path.expanduser("~/.config/vigilant-crypto-snatch.yml")


def make_marketplace(marketplace_str: str, config: dict) -> marketplace.Marketplace:
    if marketplace_str == "bitstamp":
        return bitstamp_adaptor.BitstampMarketplace(
            config["bitstamp"]["username"],
            config["bitstamp"]["key"],
            config["bitstamp"]["secret"],
        )
    elif marketplace_str == "kraken-api":
        return clikraken_adaptor_api.KrakenMarketplace()
    elif marketplace_str == "kraken":
        return clikraken_adaptor_cli.KrakenMarketplace()
    else:
        raise RuntimeError(f"Unknown market place {marketplace_str}!")


def load_config() -> dict:
    if not os.path.isfile(config_path):
        logger.error(f"Please create the configuration file at {config_path}.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config
