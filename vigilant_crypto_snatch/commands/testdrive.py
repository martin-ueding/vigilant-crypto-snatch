import datetime
from typing import List
from typing import Optional

from .. import logger
from ..configuration import Configuration
from ..configuration import get_used_currencies
from ..configuration import run_migrations
from ..configuration import YamlConfigurationFactory
from ..core import AssetPair
from ..datastorage import ListDatastore
from ..datastorage import make_datastore
from ..historical import CryptoCompareConfig
from ..historical import CryptoCompareHistoricalSource
from ..historical import MockHistorical
from ..marketplace import make_marketplace
from ..marketplace import MockMarketplace
from ..marketplace import report_balances
from ..notifications import NotifyRunConfig
from ..notifications import TelegramConfig
from ..notifications import TelegramSender
from ..notifications.notify_run import NotifyRunSender
from ..paths import user_db_path
from ..triggers import make_triggers
from ..triggers import TriggerSpec


def main() -> None:
    run_migrations()
    config = YamlConfigurationFactory().make_config()
    test_drive(config)

    print("Success! Everything seems to be configured correctly.")


def test_drive(config: Configuration) -> None:
    try_database()
    try_balance(config, config.marketplace)
    try_historical(config.crypto_compare)
    try_triggers(config.triggers)
    try_telegram(config.telegram)
    try_notify_run(config.notify_run)


def try_database() -> None:
    logger.info("Trying to open persistent database …")
    make_datastore(user_db_path)


def try_balance(config: Configuration, marketplace_name: str) -> None:
    logger.info("Trying get balances from marketplace …")
    real_market = make_marketplace(
        marketplace_name, config.bitstamp, config.kraken, config.ccxt
    )
    report_balances(real_market, get_used_currencies(config.triggers))


def try_historical(config: CryptoCompareConfig) -> None:
    logger.info("Trying to get data from Crypto Compare …")
    crypto_compare_source = CryptoCompareHistoricalSource(config)
    current_btc_eur = crypto_compare_source.get_price(
        datetime.datetime.now(), AssetPair("BTC", "EUR")
    )
    logger.info(f"Got current price: {current_btc_eur} EUR/BTC.")


def try_triggers(config: List[TriggerSpec]) -> None:
    logger.info("Trying to construct triggers …")
    datastore = ListDatastore()
    market = MockMarketplace()
    caching_source = MockHistorical()
    make_triggers(config, datastore, caching_source, market)


def try_telegram(telegram_config: Optional[TelegramConfig]) -> None:
    logger.info("Trying to send a message to Telegram …")
    if telegram_config:
        telegram_sender = TelegramSender(telegram_config)
        telegram_sender.send_message("Telegram is set up correctly! 🎉")
    else:
        logger.warning("You have not set up Telegram, so I cannot test it.")


def try_notify_run(config: Optional[NotifyRunConfig]) -> None:
    logger.info("Trying to send a message to notify.run …")
    if config:
        sender = NotifyRunSender(config)
        sender.send_message("notify.run is set up correctly! 🎉")
    else:
        logger.warning("You have not set up notify.run, so I cannot test it.")
