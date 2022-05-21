import datetime

from .. import __version__
from .. import logger
from ..configuration import get_used_currencies
from ..configuration import run_migrations
from ..configuration import YamlConfigurationFactory
from ..datastorage import make_datastore
from ..historical import CachingHistoricalSource
from ..historical import CryptoCompareHistoricalSource
from ..historical import DatabaseHistoricalSource
from ..historical import MarketSource
from ..marketplace import check_and_perform_widthdrawal
from ..marketplace import make_marketplace
from ..marketplace import report_balances
from ..notifications import add_notify_run_logger
from ..notifications import add_telegram_logger
from ..paths import user_db_path
from ..triggers import make_triggers
from ..watchloop import TriggerLoop


def main():
    run_migrations()
    config = YamlConfigurationFactory().make_config()

    add_telegram_logger(config.telegram)
    add_notify_run_logger(config.notify_run)
    logger.info(f"Starting up with version {__version__} …")

    datastore = make_datastore(user_db_path)
    market = make_marketplace(
        config.marketplace, config.bitstamp, config.kraken, config.ccxt
    )
    check_and_perform_widthdrawal(market)

    report_balances(market, get_used_currencies(config.triggers))

    database_source = DatabaseHistoricalSource(datastore, datetime.timedelta(minutes=5))
    crypto_compare_source = CryptoCompareHistoricalSource(config.crypto_compare)
    market_source = MarketSource(market)
    caching_source = CachingHistoricalSource(
        database_source, [market_source, crypto_compare_source], datastore
    )
    active_triggers = make_triggers(config.triggers, datastore, caching_source, market)

    trigger_loop = TriggerLoop(active_triggers, config.polling_interval)
    trigger_loop.loop()
