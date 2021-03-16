import datetime
import logging

from . import datamodel
from . import historical
from . import marketplace


logger = logging.getLogger('vigilant_crypto_snatch')


class Trigger(object):
    def __init__(self, session, source: historical.HistoricalSource, market: marketplace.Marketplace, coin: str, fiat: str, volume_fiat: float, minutes: int):
        self.session = session
        self.source = source
        self.market = market
        self.coin = coin
        self.fiat = fiat
        self.volume_fiat = volume_fiat
        self.minutes = minutes
        self.reset_trials()

    def is_triggered(self, session, config) -> bool:
        raise NotImplementedError()

    def get_name(self) -> str:
        raise NotImplementedError()

    def has_cooled_off(self, session) -> bool:
        then = datetime.datetime.now() - datetime.timedelta(minutes=self.minutes)
        trade_count = session.query(datamodel.Trade).filter(
            datamodel.Trade.trigger_name == self.get_name(),
            datamodel.Trade.timestamp > then,
            datamodel.Trade.coin == self.coin,
            datamodel.Trade.fiat == self.fiat).count()
        return trade_count == 0

    def reset_trials(self):
        self.trials = 0


class DropTrigger(Trigger):
    def __init__(self, market: marketplace.Marketplace, coin: str, fiat: str, volume_fiat: float, minutes: int, drop: float):
        super().__init__(market, coin, fiat, volume_fiat, minutes)
        self.drop = drop
        assert self.drop > 0, "Drop triggers must have positive percentages!"

    def is_triggered(self, session, config) -> bool:
        price = self.source.get_price(datetime.datetime.now(), self.coin, self.fiat)
        then = datetime.datetime.now() - datetime.timedelta(minutes=self.minutes)
        try:
            then_price = self.source.get_price(then, self.coin, self.fiat)
        except historical.HistoricalError:
            return False
        critical = then_price.last * (1 - self.drop / 100)
        return price.last < critical

    def get_name(self) -> str:
        return f'{self.coin} drop {self.drop} % in {self.minutes} minutes'


class TrueTrigger(Trigger):
    def is_triggered(self, session, config) -> bool:
        return True

    def get_name(self) -> str:
        return f'{self.coin} every {self.minutes} minutes'


def make_triggers(config, session, source: historical.HistoricalSource, market):
    active_triggers = []
    if 'triggers' in config and config['triggers'] is not None:
        for trigger_spec in config['triggers']:
            trigger = DropTrigger(
                session=session,
                source=source,
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
            trigger = TrueTrigger(
                session=session,
                source=source,
                market=market,
                coin=timer_spec['coin'].upper(),
                fiat=timer_spec['fiat'].upper(),
                volume_fiat=timer_spec['volume_fiat'],
                minutes=timer_spec['minutes'])
            logger.debug(f'Constructed trigger: {trigger.get_name()}')
            active_triggers.append(trigger)
    return active_triggers