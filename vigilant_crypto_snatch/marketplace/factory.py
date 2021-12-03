from .bitstamp_adaptor import BitstampMarketplace
from .krakenex_adaptor import KrakenexMarketplace


def make_marketplace(config, marketplace_name):
    if marketplace_name == "bitstamp":
        real_market = BitstampMarketplace(config.get_bitstamp_config())
    elif marketplace_name == "kraken":
        real_market = KrakenexMarketplace(config.get_kraken_config())
    else:
        raise RuntimeError(f"Unsupported marketplace: {marketplace_name}")
    return real_market
