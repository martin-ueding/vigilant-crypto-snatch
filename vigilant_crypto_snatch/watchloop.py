import datetime
import logging
import time
import traceback
import typing

from . import logger
from .datastorage import DatastoreException
from .marketplace import BuyError
from .marketplace import TickerError
from .marketplace import WithdrawalError
from .myrequests import HttpRequestError
from .telegram import telegram_sender_holder
from .triggers import Trigger


class TriggerLoop(object):
    def __init__(
        self,
        active_triggers: typing.List[Trigger],
        sleep: int,
    ):
        self.active_triggers = active_triggers
        self.sleep = sleep

    def loop(self) -> None:
        try:
            while True:
                self.loop_body()
        except KeyboardInterrupt:
            logger.info("User interrupted, shutting down.")
            if telegram_sender_holder.get_sender() is not None:
                telegram_sender_holder.get_sender().shutdown()

    def loop_body(self) -> None:
        for trigger in self.active_triggers:
            process_trigger(trigger)
        logger.debug(f"All triggers checked, sleeping for {self.sleep} seconds …")
        time.sleep(self.sleep)


def notify_and_continue(exception: Exception, severity: int) -> None:
    logger.log(
        severity, f"An exception of type {type(exception)} has occurred: {exception}"
    )


def process_trigger(trigger: Trigger):
    logger.debug(f"Checking trigger “{trigger.get_name()}” …")
    try:
        now = datetime.datetime.now()
        if trigger.has_cooled_off(now) and trigger.is_triggered(now):
            trigger.fire(now)
    except HttpRequestError as e:
        notify_and_continue(e, logging.ERROR)
    except TickerError as e:
        notify_and_continue(e, logging.ERROR)
    except BuyError as e:
        notify_and_continue(e, logging.CRITICAL)
    except WithdrawalError as e:
        notify_and_continue(e, logging.CRITICAL)
    except DatastoreException as e:
        notify_and_continue(e, logging.ERROR)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        logger.critical(
            f"Unhandled exception type: {repr(e)}. Please report this to Martin!\n"
            f"\n"
            f"{traceback.format_exc()}\n"
        )
