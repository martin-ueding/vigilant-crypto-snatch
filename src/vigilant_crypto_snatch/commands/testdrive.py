import datetime

from vigilant_crypto_snatch import configuration
from vigilant_crypto_snatch import datastorage
from vigilant_crypto_snatch import logger
from vigilant_crypto_snatch import marketplace
from vigilant_crypto_snatch import migrations
from vigilant_crypto_snatch import triggers
from vigilant_crypto_snatch.historical import concrete
from vigilant_crypto_snatch.historical.mock import MockHistorical


def main(marketplace_name) -> None:
    migrations.run_migrations()
    config = configuration.load_config()

    try_database()
    try_balance(config, marketplace_name)
    try_historical(config)
    try_triggers(config)

    print("Success! Everything seems to be configured correctly.")


def try_database() -> None:
    logger.info("Trying to open persistent database …")
    persistent_datastore = datastorage.make_datastore(persistent=True)


def try_balance(config: dict, marketplace_name: str) -> None:
    logger.info("Trying get balances from marketplace …")
    real_market = marketplace.make_marketplace(marketplace_name, config)
    marketplace.report_balances(real_market, configuration.get_used_currencies(config))


def try_historical(config):
    logger.info("Trying to get data from Crypto Compare …")
    crypto_compare_source = concrete.CryptoCompareHistoricalSource(
        config["cryptocompare"]["api_key"]
    )
    current_btc_eur = crypto_compare_source.get_price(
        datetime.datetime.now(), "BTC", "EUR"
    )
    logger.info(f"Got current price: {current_btc_eur} EUR/BTC.")


def try_triggers(config):
    logger.info("Trying to construct triggers …")
    datastore = datastorage.ListDatastore()
    market = marketplace.MockMarketplace()
    caching_source = MockHistorical()
    active_triggers = triggers.make_triggers(config, datastore, caching_source, market)
