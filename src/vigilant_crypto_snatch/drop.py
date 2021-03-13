import datetime
import logging
import time

from . import datamodel
from . import marketplace
from . import triggers
from . import historical


logger = logging.getLogger('vigilant_crypto_snatch')


def check_for_drops(config: dict, session, market: marketplace.Marketplace, options) -> None:
    active_triggers = []
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
    for timer_spec in config['timers']:
        trigger = triggers.TrueTrigger(
            market=market,
            coin=timer_spec['coin'].upper(),
            fiat=timer_spec['fiat'].upper(),
            volume_fiat=timer_spec['volume_fiat'],
            minutes=timer_spec['minutes'])
        logger.debug(f'Constructed trigger: {trigger.get_name()}')
        active_triggers.append(trigger)

    try:
        while True:
            for trigger in active_triggers:
                logger.debug(f'Checking trigger “{trigger.get_name()}” …')
                try:
                    if trigger.has_cooled_off(session) and trigger.is_triggered(session, config):
                        logger.info(f'Trigger “{trigger.get_name()}” fired, try buying …')
                        buy(config, trigger, session)
                except marketplace.TickerError as e:
                    notify_and_continue(e, logging.ERROR)
                except marketplace.BuyError as e:
                    notify_and_continue(e, logging.CRITICAL)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.critical(f'Unhandled exception type: {repr(e)}. Please report this to Martin!')
                    if not options.keepalive:
                        raise

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
