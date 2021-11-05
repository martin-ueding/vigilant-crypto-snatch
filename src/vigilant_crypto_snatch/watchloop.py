import datetime
import logging
import time
import traceback
import typing

import requests.exceptions
import sqlalchemy.exc

from . import configuration
from . import datastorage
from . import historical
from . import logger
from . import marketplace
from . import migrations
from . import telegram
from . import triggers
from .historical import concrete


class TriggerLoop(object):
    def __init__(
        self,
        active_triggers: typing.List[triggers.Trigger],
        sleep: int,
        keepalive: bool,
        one_shot: bool,
    ):
        self.active_triggers = active_triggers
        self.sleep = sleep
        self.keepalive = keepalive
        self.one_shot = one_shot

    def loop(self) -> None:
        try:
            while True:
                self.loop_body()
                if self.one_shot:
                    if telegram.telegram_sender is not None:
                        telegram.telegram_sender.shutdown()
                    break
        except KeyboardInterrupt:
            logger.info("User interrupted, shutting down.")
            if telegram.telegram_sender is not None:
                telegram.telegram_sender.shutdown()

    def loop_body(self) -> None:
        for trigger in self.active_triggers:
            process_trigger(trigger, self.keepalive)
        if not self.one_shot:
            logger.debug(f"All triggers checked, sleeping for {self.sleep} seconds …")
            time.sleep(self.sleep)


def notify_and_continue(exception: Exception, severity: int) -> None:
    logger.log(
        severity, f"An exception of type {type(exception)} has occurred: {exception}"
    )


def process_trigger(trigger: triggers.Trigger, keepalive: bool):
    logger.debug(f"Checking trigger “{trigger.get_name()}” …")
    try:
        now = datetime.datetime.now()
        if trigger.has_cooled_off(now) and trigger.is_triggered(now):
            trigger.fire(now)
    except marketplace.TickerError as e:
        notify_and_continue(e, logging.ERROR)
    except marketplace.BuyError as e:
        notify_and_continue(e, logging.CRITICAL)
    except requests.exceptions.ReadTimeout as e:
        logger.error(
            f"We have had a read timeout, likely just a temporary internet or API availability glitch."
            f"Details: {e}"
        )
    except requests.exceptions.ConnectionError as e:
        notify_and_continue(e, logging.ERROR)
    except requests.exceptions.HTTPError as e:
        notify_and_continue(e, logging.ERROR)
    except sqlalchemy.exc.OperationalError as e:
        logger.critical(
            f"Something went wrong with the database. Perhaps it is easiest to just delete the database file at `{configuration.user_db_path}`. The original exception was this: `{repr(e)}`"
        )
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        logger.critical(
            f"Unhandled exception type: {repr(e)}. Please report this to Martin!\n"
            f"\n"
            f"{traceback.format_exc()}\n"
        )
        if not keepalive:
            raise


def main(marketplace_name, keepalive, one_shot, dry_run):
    migrations.run_migrations()

    telegram.add_telegram_logger()
    if not one_shot:
        logger.info("Starting up …")

    datastore = datastorage.make_datastore(persistent=True)
    config = configuration.load_config()
    market = marketplace.make_marketplace(marketplace_name, config, dry_run)
    marketplace.check_and_perform_widthdrawal(market)

    if not one_shot:
        marketplace.report_balances(market, configuration.get_used_currencies(config))

    database_source = concrete.DatabaseHistoricalSource(
        datastore, datetime.timedelta(minutes=5)
    )
    crypto_compare_source = concrete.CryptoCompareHistoricalSource(
        config["cryptocompare"]["api_key"]
    )
    market_source = concrete.MarketSource(market)
    caching_source = concrete.CachingHistoricalSource(
        database_source, [market_source, crypto_compare_source], datastore
    )
    active_triggers = triggers.make_triggers(
        config, datastore, caching_source, market, dry_run
    )

    trigger_loop = TriggerLoop(active_triggers, config["sleep"], keepalive, one_shot)
    trigger_loop.loop()
