import copy
import datetime
import logging
import time
import sys

import sqlalchemy.exc

from . import datamodel
from . import marketplace
from . import triggers
from . import historical


logger = logging.getLogger('vigilant_crypto_snatch')


def check_for_drops(config: dict, session, market: marketplace.Marketplace, options) -> None:
    active_triggers = []
    if 'triggers' in config and config['triggers'] is not None:
        for trigger_spec in config['triggers']:
            trigger = triggers.DropTrigger(
                market=market,
                coin=trigger_spec['coin'].upper(),
                fiat=trigger_spec['fiat'].upper(),
                volume_fiat=trigger_spec['volume_fiat'],
                drop=trigger_spec['drop'],
                minutes=trigger_spec['minutes'])
            logger.debug(f'Constructed trigger: {trigger.get_name()}')
            active_triggers.append(trigger)
    if 'timers' in config and config['timers'] is not None:
        for timer_spec in config['timers']:
            trigger = triggers.TrueTrigger(
                market=market,
                coin=timer_spec['coin'].upper(),
                fiat=timer_spec['fiat'].upper(),
                volume_fiat=timer_spec['volume_fiat'],
                minutes=timer_spec['minutes'])
            logger.debug(f'Constructed trigger: {trigger.get_name()}')
            active_triggers.append(trigger)

    longest_cooldown = max(trigger.minutes for trigger in active_triggers)
    logger.debug(f'Longest cooldown for any trigger is {longest_cooldown} minutes.')
    last_cleaning = None
    last_checkin = datetime.datetime.now()

    try:
        while True:
            if len(active_triggers) == 0:
                logger.critical('All triggers have been disabled, shutting down. You need to manually restart the program after fixing the errors.')
                return

            now = datetime.datetime.now()
            if now.hour == 6 and last_checkin < now - datetime.timedelta(hours=2):
                logger.info("Hey there, I'm still there! 🤖")
                last_checkin = now

            for trigger in copy.copy(active_triggers):
                logger.debug(f'Checking trigger “{trigger.get_name()}” …')
                try:
                    if trigger.has_cooled_off(session) and trigger.is_triggered(session, config):
                        trigger.trials += 1
                        logger.info(f'Trigger “{trigger.get_name()}” fired, try buying …')
                        buy(config, trigger, session)
                        trigger.reset_trials()
                except marketplace.TickerError as e:
                    notify_and_continue(e, logging.ERROR)
                except marketplace.BuyError as e:
                    notify_and_continue(e, logging.CRITICAL)
                except sqlalchemy.exc.OperationalError as e:
                    logger.critical(f'Something went wrong with the database. Perhaps it is easiest to just delete the database file at `{datamodel.db_path}`. The original exception was this: {repr(e)}')
                    sys.exit(1)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.critical(f'Unhandled exception type: {repr(e)}. Please report this to Martin!')
                    if not options.keepalive:
                        raise

                if trigger.trials > 3:
                    logger.warning(f'Disabling trigger “{trigger.get_name()}” after repeated failures.')
                    active_triggers.remove(trigger)

            if last_cleaning is None or last_cleaning < datetime.datetime.now() - datetime.timedelta(minutes=60):
                datamodel.garbage_collect_db(session, datetime.datetime.now() - 2 * datetime.timedelta(minutes=longest_cooldown))
                last_cleaning = datetime.datetime.now()

            logger.debug(f'All triggers checked, sleeping for {config["sleep"]} seconds …')
            time.sleep(config['sleep'])
    except KeyboardInterrupt:
        logger.info('User interrupted, shutting down.')


def notify_and_continue(exception: Exception, severity: int) -> None:
    logger.log(severity, f'An exception of type {type(exception)} has occurred: {exception}')


def buy(config: dict, trigger: triggers.Trigger, session):
    price = historical.search_current(session, trigger.market, trigger.coin, trigger.fiat)
    volume_coin = round(trigger.volume_fiat / price, 8)

    trigger.market.place_order(trigger.coin, trigger.fiat, volume_coin)
    trade = datamodel.Trade(
        timestamp=datetime.datetime.now(),
        trigger_name=trigger.get_name(),
        volume_coin=volume_coin,
        volume_fiat=trigger.volume_fiat,
        coin=trigger.coin,
        fiat=trigger.fiat)
    session.add(trade)
    session.commit()

    buy_message = f'{volume_coin} {trigger.coin} for {trigger.volume_fiat} {trigger.fiat} on {trigger.market.get_name()} due to “{trigger.get_name()}”'
    logger.info(f'Bought {buy_message}.')
