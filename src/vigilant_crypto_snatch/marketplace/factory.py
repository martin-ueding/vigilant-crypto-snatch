from . import krakenex_adaptor
from vigilant_crypto_snatch import (
    marketplace,
)
from vigilant_crypto_snatch.marketplace import (
    clikraken_adaptor_api,
    clikraken_adaptor_cli,
    bitstamp_adaptor,
)


def make_marketplace(marketplace_str: str, config: dict) -> marketplace.Marketplace:
    if marketplace_str == "bitstamp":
        return bitstamp_adaptor.BitstampMarketplace(
            config["bitstamp"]["username"],
            config["bitstamp"]["key"],
            config["bitstamp"]["secret"],
        )
    elif marketplace_str == "clikraken-api":
        return clikraken_adaptor_api.KrakenMarketplace()
    elif marketplace_str == "clikraken":
        return clikraken_adaptor_cli.KrakenMarketplace()
    elif marketplace_str == "kraken":
        return krakenex_adaptor.KrakenexMarketplace(
            config["kraken"]["key"],
            config["kraken"]["secret"],
            withdrawal_config=config["kraken"].get("withdrawal", {}),
        )
    else:
        raise RuntimeError(f"Unknown market place {marketplace_str}!")
