import datetime

from .. import configuration
from .. import datastorage
from .. import logger
from .. import marketplace
from .. import migrations
from .. import telegram
from .. import triggers
from ..historical import concrete
from ..historical.mock import MockHistorical


def main(marketplace_name) -> None:
    migrations.run_migrations()
    config = configuration.load_config()

    try_database()
    try_balance(config, marketplace_name)
    try_historical(config)
    try_triggers(config)
    try_telegram(config)

    print("Success! Everything seems to be configured correctly.")


def try_database() -> None:
    logger.info("Trying to open persistent database …")
    persistent_datastore = datastorage.make_datastore(persistent=True)


def try_balance(config: dict, marketplace_name: str) -> None:
    logger.info("Trying get balances from marketplace …")
    real_market = marketplace.make_marketplace(marketplace_name, config)
    marketplace.report_balances(real_market, configuration.get_used_currencies(config))


def try_historical(config: dict) -> None:
    logger.info("Trying to get data from Crypto Compare …")
    crypto_compare_source = concrete.CryptoCompareHistoricalSource(
        config["cryptocompare"]["api_key"]
    )
    current_btc_eur = crypto_compare_source.get_price(
        datetime.datetime.now(), "BTC", "EUR"
    )
    logger.info(f"Got current price: {current_btc_eur} EUR/BTC.")


def try_triggers(config: dict) -> None:
    logger.info("Trying to construct triggers …")
    datastore = datastorage.ListDatastore()
    market = marketplace.MockMarketplace()
    caching_source = MockHistorical()
    active_triggers = triggers.make_triggers(config, datastore, caching_source, market)


def try_telegram(config: dict) -> None:
    telegram_sender = telegram.make_telegram_sender(config)
    if telegram_sender is not None:
        telegram_sender.queue_message("Telegram is set up correctly!")
        telegram_sender.shutdown()
    else:
        logger.warning("You have not set up Telegram, so I cannot test it.")
