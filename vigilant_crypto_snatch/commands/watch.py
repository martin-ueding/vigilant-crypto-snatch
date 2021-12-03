import datetime

from ..configuration import get_used_currencies
from ..configuration import run_migrations
from ..configuration import YamlConfiguration
from ..datastorage import make_datastore
from ..historical import CachingHistoricalSource
from ..historical import CryptoCompareHistoricalSource
from ..historical import DatabaseHistoricalSource
from ..historical import MarketSource
from ..marketplace import check_and_perform_widthdrawal
from ..marketplace import make_marketplace
from ..marketplace import report_balances
from ..paths import user_db_path
from ..telegram import add_telegram_logger
from ..triggers import make_triggers
from ..watchloop import TriggerLoop


def main(marketplace_name, keepalive, one_shot, dry_run):
    run_migrations()
    config = YamlConfiguration()

    add_telegram_logger(config.get_telegram_config())
    if not one_shot:
        logger.info("Starting up …")

    datastore = make_datastore(user_db_path)
    market = make_marketplace(marketplace_name, config, dry_run)
    check_and_perform_widthdrawal(market)

    if not one_shot:
        report_balances(market, get_used_currencies(config.get_trigger_config()))

    database_source = DatabaseHistoricalSource(datastore, datetime.timedelta(minutes=5))
    crypto_compare_source = CryptoCompareHistoricalSource(
        config.get_crypto_compare_config()
    )
    market_source = MarketSource(market)
    caching_source = CachingHistoricalSource(
        database_source, [market_source, crypto_compare_source], datastore
    )
    active_triggers = make_triggers(
        config.get_trigger_config(), datastore, caching_source, market, dry_run
    )

    trigger_loop = TriggerLoop(
        active_triggers, config.get_polling_interval(), keepalive, one_shot
    )
    trigger_loop.loop()
