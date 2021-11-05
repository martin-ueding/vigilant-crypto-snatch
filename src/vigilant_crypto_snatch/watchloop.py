import datetime
import logging
import time
import traceback
import typing

import requests.exceptions

from . import datastorage
from . import logger
from . import marketplace
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
    except datastorage.DatastoreException as e:
        notify_and_continue(e, logging.ERROR)
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
