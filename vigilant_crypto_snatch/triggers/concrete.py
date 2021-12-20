import abc
import datetime
from typing import List
from typing import Optional

from .. import logger
from ..core import Trade
from ..datastorage import Datastore
from ..historical import HistoricalSource
from ..marketplace import check_and_perform_widthdrawal
from ..marketplace import Marketplace
from ..marketplace import report_balances
from .interface import Trigger
from .triggered_delegates import TriggeredDelegate
from .volume_fiat_delegates import VolumeFiatDelegate


class FailureTimeout(object):
    TRIGGER_FAILURE_COUNT = 3
    TRIGGER_FAILURE_TIMEOUT_HOURS = 12

    def __init__(self):
        self.trials = 0
        self.last_trial = None

    def start(self, now: datetime.datetime) -> None:
        self.trials += 1
        self.last_trial = now

    def finish(self) -> None:
        self.trials = 0
        self.last_trial = None

    def has_timeout(self, now: datetime.datetime) -> bool:
        if self.trials < self.TRIGGER_FAILURE_COUNT:
            return False
        else:
            end_timeout = self.last_trial + datetime.timedelta(
                hours=self.TRIGGER_FAILURE_TIMEOUT_HOURS
            )
            return end_timeout >= now


class BuyTrigger(Trigger, abc.ABC):
    def __init__(
        self,
        datastore: Datastore,
        source: HistoricalSource,
        market: Marketplace,
        coin: str,
        fiat: str,
        cooldown_minutes: int,
        triggered_delegates: List[TriggeredDelegate],
        volume_fiat_delegate: VolumeFiatDelegate,
        name: Optional[str] = None,
        start: Optional[datetime.datetime] = None,
    ):
        super().__init__()
        self.datastore = datastore
        self.source = source
        self.market = market
        self.coin = coin
        self.fiat = fiat
        self.cooldown_minutes = cooldown_minutes
        self.triggered_delegates = triggered_delegates
        self.volume_fiat_delegate = volume_fiat_delegate
        self.name = name
        self.start = start
        self.failure_timeout = FailureTimeout()

    def is_triggered(self, now: datetime.datetime) -> bool:
        return all(
            triggered_delegate.is_triggered(now)
            for triggered_delegate in self.triggered_delegates
        )

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        if self.failure_timeout.has_timeout(now):
            return False
        if self.start is not None and now < self.start:
            return False

        then = now - datetime.timedelta(minutes=self.cooldown_minutes)
        return not self.datastore.was_triggered_since(
            self.get_name(), self.coin, self.fiat, then
        )

    def fire(self, now: datetime.datetime) -> None:
        logger.info(f"Trigger “{self.get_name()}” fired, try buying …")
        self.failure_timeout.start(now)
        price = self.source.get_price(now, self.coin, self.fiat)
        volume_fiat = self.volume_fiat_delegate.get_volume_fiat()
        volume_coin = round(volume_fiat / float(price.last), 8)
        self.perform_buy(volume_coin, volume_fiat, now)
        self.failure_timeout.finish()

    def perform_buy(
        self, volume_coin: float, volume_fiat: float, now: datetime.datetime
    ) -> None:
        self.market.place_order(self.coin, self.fiat, volume_coin)
        try:
            check_and_perform_widthdrawal(self.market)
        except NotImplementedError as e:
            logger.warning(
                f"Marketplace {self.market.get_name()} doesn't support withdrawal."
            )
        trade = Trade(
            timestamp=now,
            trigger_name=self.get_name(),
            volume_coin=volume_coin,
            volume_fiat=volume_fiat,
            coin=self.coin,
            fiat=self.fiat,
        )
        self.datastore.add_trade(trade)

        rate = volume_fiat / volume_coin
        buy_message = f"{volume_coin} {self.coin} for {volume_fiat} {self.fiat} ({rate} {self.fiat}/{self.coin}) on {self.market.get_name()} due to “{self.get_name()}”"
        logger.info(f"Bought {buy_message}.")
        report_balances(self.market, {self.coin, self.fiat})

    def get_name(self) -> str:
        if self.name is None:
            return f"Buy(cooldown_minutes={self.cooldown_minutes}, trigger={str(self.triggered_delegates)}, volume_fiat={str(self.volume_fiat_delegate)})"
        else:
            return self.name


class CheckinTrigger(Trigger):
    def __init__(self, now=datetime.datetime.now()):
        super().__init__()
        self.last_checkin = now

    def is_triggered(self, now: datetime.datetime) -> bool:
        return now.hour == 6

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        return self.last_checkin < now - datetime.timedelta(hours=2)

    def get_name(self) -> str:
        return "Checkin"

    def fire(self, now: datetime.datetime) -> None:
        logger.info("I am still here!")
        self.last_checkin = now


class DatabaseCleaningTrigger(Trigger):
    def __init__(self, datastore: Datastore, interval: datetime.timedelta):
        super().__init__()
        self.datastore = datastore
        self.interval = interval
        self.last_cleaning = None

    def is_triggered(self, now: datetime.datetime) -> bool:
        return True

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        if self.last_cleaning is None:
            return True
        return self.last_cleaning < now - self.interval

    def fire(self, now: datetime.datetime) -> None:
        self.datastore.clean_old(now - self.interval)

    def get_name(self) -> str:
        return "Database cleaning"
