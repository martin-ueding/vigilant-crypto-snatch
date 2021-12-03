import datetime
from typing import List
from typing import Optional

from .. import logger
from ..configuration import Configuration
from ..configuration import get_used_currencies
from ..configuration import run_migrations
from ..configuration import YamlConfiguration
from ..datastorage import ListDatastore
from ..datastorage import make_datastore
from ..historical import CryptoCompareConfig
from ..historical import CryptoCompareHistoricalSource
from ..historical import MockHistorical
from ..marketplace import make_marketplace
from ..marketplace import MockMarketplace
from ..marketplace import report_balances
from ..paths import user_db_path
from ..telegram import TelegramConfig
from ..telegram import TelegramSender
from ..triggers import make_triggers
from ..triggers import TriggerSpec


def main(marketplace_name) -> None:
    run_migrations()
    config = YamlConfiguration()

    try_database()
    try_balance(config, marketplace_name)
    try_historical(config.get_crypto_compare_config())
    try_triggers(config.get_trigger_config())
    try_telegram(config.get_telegram_config())

    print("Success! Everything seems to be configured correctly.")


def try_database() -> None:
    logger.info("Trying to open persistent database …")
    make_datastore(user_db_path)


def try_balance(config: Configuration, marketplace_name: str) -> None:
    logger.info("Trying get balances from marketplace …")
    real_market = make_marketplace(config, marketplace_name)
    report_balances(real_market, get_used_currencies(config.get_trigger_config()))


def try_historical(config: CryptoCompareConfig) -> None:
    logger.info("Trying to get data from Crypto Compare …")
    crypto_compare_source = CryptoCompareHistoricalSource(config)
    current_btc_eur = crypto_compare_source.get_price(
        datetime.datetime.now(), "BTC", "EUR"
    )
    logger.info(f"Got current price: {current_btc_eur} EUR/BTC.")


def try_triggers(config: List[TriggerSpec]) -> None:
    logger.info("Trying to construct triggers …")
    datastore = ListDatastore()
    market = MockMarketplace()
    caching_source = MockHistorical()
    make_triggers(config, datastore, caching_source, market)


def try_telegram(config: Optional[TelegramConfig]) -> None:
    logger.info("Trying to send a message to Telegram …")
    if config:
        telegram_sender = TelegramSender(config)
        telegram_sender.queue_message("Telegram is set up correctly!")
        telegram_sender.shutdown()
    else:
        logger.warning("You have not set up Telegram, so I cannot test it.")
