from typing import Optional

from .bitstamp_adaptor import BitstampMarketplace
from .ccxt_adapter import CCXTMarketplace
from .interface import BitstampConfig
from .interface import CCXTConfig
from .interface import KrakenConfig
from .interface import Marketplace
from .krakenex_adaptor import KrakenexMarketplace


def make_marketplace(
    marketplace_name: str,
    bitstamp_config: Optional[BitstampConfig] = None,
    kraken_config: Optional[KrakenConfig] = None,
    ccxt_config: Optional[CCXTConfig] = None,
) -> Marketplace:
    real_market: Marketplace
    if marketplace_name == "bitstamp":
        assert bitstamp_config is not None
        real_market = BitstampMarketplace(bitstamp_config)
    elif marketplace_name == "kraken":
        assert kraken_config is not None
        real_market = KrakenexMarketplace(kraken_config)
    elif marketplace_name == "ccxt":
        assert ccxt_config is not None
        real_market = CCXTMarketplace(ccxt_config)
    else:
        raise RuntimeError(f"Unsupported marketplace: {marketplace_name}")
    return real_market
