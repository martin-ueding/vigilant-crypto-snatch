from . import (
    marketplace,
    bitstamp_adaptor,
    clikraken_adaptor_api,
    clikraken_adaptor_cli,
)


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
