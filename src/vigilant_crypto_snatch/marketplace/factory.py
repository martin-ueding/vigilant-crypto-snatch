from . import krakenex_adaptor
from . import marketplace
from . import bitstamp_adaptor


def make_marketplace(marketplace_str: str, config: dict) -> marketplace.Marketplace:
    if marketplace_str == "bitstamp":
        return bitstamp_adaptor.BitstampMarketplace(
            config["bitstamp"]["username"],
            config["bitstamp"]["key"],
            config["bitstamp"]["secret"],
        )
    elif marketplace_str == "kraken":
        return krakenex_adaptor.KrakenexMarketplace(
            config["kraken"]["key"],
            config["kraken"]["secret"],
            withdrawal_config=config["kraken"].get("withdrawal", {}),
            prefer_fee_in_base_currency=config["kraken"].get(
                "prefer_fee_in_base_currency", False
            ),
        )
    else:
        raise RuntimeError(f"Unknown market place {marketplace_str}!")
