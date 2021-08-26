import datetime
import logging
import sys
import time
import traceback
import typing

import requests.exceptions
import sqlalchemy.exc

from . import configuration
from . import datamodel
from . import historical
from . import logger
from . import marketplace
from . import migrations
from . import telegram
from . import triggers


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


def main(options):
    migrations.run_migrations()

    telegram.add_telegram_logger()
    if not options.one_shot:
        logger.info("Starting up …")

    session = datamodel.open_user_db_session()
    config = configuration.load_config()
    market = marketplace.make_marketplace(options.marketplace, config, options.dry_run)
    marketplace.check_and_perform_widthdrawal(market)

    if not options.one_shot:
        marketplace.report_balances(market, configuration.get_used_currencies(config))

    database_source = historical.DatabaseHistoricalSource(
        session, datetime.timedelta(minutes=5)
    )
    crypto_compare_source = historical.CryptoCompareHistoricalSource(
        config["cryptocompare"]["api_key"]
    )
    market_source = historical.MarketSource(market)
    caching_source = historical.CachingHistoricalSource(
        database_source, [market_source, crypto_compare_source], session
    )
    active_triggers = triggers.make_triggers(
        config, session, caching_source, market, options.dry_run
    )

    trigger_loop = TriggerLoop(
        active_triggers, config["sleep"], options.keepalive, options.one_shot
    )
    trigger_loop.loop()
