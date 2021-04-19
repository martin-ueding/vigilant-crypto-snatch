import datetime
import logging
import time
import sys
import typing

import sqlalchemy.exc

from . import configuration
from . import factory
from . import datamodel
from . import marketplace
from . import triggers
from . import historical
from . import telegram
from . import logger


class TriggerLoop(object):
    def __init__(
        self,
        active_triggers: typing.List[triggers.Trigger],
        sleep: int,
        keepalive: bool,
    ):
        self.active_triggers = active_triggers
        self.sleep = sleep
        self.keepalive = keepalive

    def loop(self) -> None:
        try:
            while True:
                self.loop_body()
        except KeyboardInterrupt:
            logger.info("User interrupted, shutting down.")

    def loop_body(self) -> None:
        for trigger in self.active_triggers:
            process_trigger(trigger, self.keepalive)
        self.clean_triggers()
        logger.debug(f"All triggers checked, sleeping for {self.sleep} seconds …")
        time.sleep(self.sleep)

    def clean_triggers(self):
        self.active_triggers = [
            trigger for trigger in self.active_triggers if trigger.trials <= 3
        ]
        if not any(
            isinstance(trigger, triggers.BuyTrigger) for trigger in self.active_triggers
        ):
            logger.critical(
                "All triggers have been disabled, shutting down. You need to manually restart the program after fixing the errors."
            )
            sys.exit(1)


def notify_and_continue(exception: Exception, severity: int) -> None:
    logger.log(
        severity, f"An exception of type {type(exception)} has occurred: {exception}"
    )


def process_trigger(trigger: triggers.Trigger, keepalive: bool):
    logger.debug(f"Checking trigger “{trigger.get_name()}” …")
    try:
        now = datetime.datetime.now()
        if trigger.has_cooled_off(now) and trigger.is_triggered(now):
            trigger.trials += 1
            trigger.fire(now)
            trigger.reset_trials()
    except marketplace.TickerError as e:
        notify_and_continue(e, logging.ERROR)
    except marketplace.BuyError as e:
        notify_and_continue(e, logging.CRITICAL)
    except sqlalchemy.exc.OperationalError as e:
        logger.critical(
            f"Something went wrong with the database. Perhaps it is easiest to just delete the database file at `{datamodel.user_db_path}`. The original exception was this: {repr(e)}"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        logger.critical(
            f"Unhandled exception type: {repr(e)}. Please report this to Martin!"
        )
        if not keepalive:
            raise

    if trigger.trials > 3:
        logger.warning(
            f"Disabling trigger “{trigger.get_name()}” after repeated failures."
        )


def main(options):
    telegram.add_telegram_logger()
    logger.info("Starting up …")

    session = datamodel.open_user_db_session()
    config = configuration.load_config()
    market = factory.make_marketplace(options.marketplace, config)

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
    active_triggers = triggers.make_triggers(config, session, caching_source, market)

    trigger_loop = TriggerLoop(active_triggers, config["sleep"], options.keepalive)
    trigger_loop.loop()
