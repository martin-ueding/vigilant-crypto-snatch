import datetime

from . import datamodel
from . import historical
from . import marketplace


class Trigger(object):
    def __init__(self, market: marketplace.Marketplace, coin: str, fiat: str, volume_fiat: float, minutes: int):
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
        price = historical.search_current(session, self.market, self.coin, self.fiat)
        then = datetime.datetime.now() - datetime.timedelta(minutes=self.minutes)
        try:
            then_price = historical.search_historical(session, then, config['cryptocompare']['api_key'], self.coin, self.fiat)
        except historical.HistoricalError:
            return False
        critical = then_price * (1 - self.drop / 100)
        return price < critical

    def get_name(self) -> str:
        return f'{self.coin} drop {self.drop} % in {self.minutes} minutes'


class TrueTrigger(Trigger):
    def is_triggered(self, session, config) -> bool:
        return True

    def get_name(self) -> str:
        return f'{self.coin} every {self.minutes} minutes'
