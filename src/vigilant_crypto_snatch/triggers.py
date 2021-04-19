import datetime
import logging
import abc
import typing

import sqlalchemy.orm

from . import datamodel
from . import historical
from . import marketplace
from . import logger


class Trigger(object):
    def __init__(self):
        self.trials = 0

    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()

    def get_name(self) -> str:
        raise NotImplementedError()

    def fire(self, now: datetime.datetime) -> None:
        raise NotImplementedError()

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()

    def reset_trials(self):
        self.trials = 0


class BuyTrigger(Trigger, abc.ABC):
    def __init__(
        self,
        session: sqlalchemy.orm.session,
        source: historical.HistoricalSource,
        market: marketplace.Marketplace,
        coin: str,
        fiat: str,
        volume_fiat: float,
        minutes: int,
    ):
        super().__init__()
        self.session = session
        self.source = source
        self.market = market
        self.coin = coin
        self.fiat = fiat
        self.volume_fiat = volume_fiat
        self.minutes = minutes
        self.reset_trials()

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        then = now - datetime.timedelta(minutes=self.minutes)
        trade_count = (
            self.session.query(datamodel.Trade)
            .filter(
                datamodel.Trade.trigger_name == self.get_name(),
                datamodel.Trade.timestamp > then,
                datamodel.Trade.coin == self.coin,
                datamodel.Trade.fiat == self.fiat,
            )
            .count()
        )
        return trade_count == 0

    def fire(self, now: datetime.datetime) -> None:
        logger.info(f"Trigger “{self.get_name()}” fired, try buying …")
        price = self.source.get_price(now, self.coin, self.fiat)
        volume_coin = round(self.volume_fiat / price.last, 8)

        self.market.place_order(self.coin, self.fiat, volume_coin)
        trade = datamodel.Trade(
            timestamp=now,
            trigger_name=self.get_name(),
            volume_coin=volume_coin,
            volume_fiat=self.volume_fiat,
            coin=self.coin,
            fiat=self.fiat,
        )
        self.session.add(trade)
        self.session.commit()

        buy_message = f"{volume_coin} {self.coin} for {self.volume_fiat} {self.fiat} on {self.market.get_name()} due to “{self.get_name()}”"
        logger.info(f"Bought {buy_message}.")


class DropTrigger(BuyTrigger):
    def __init__(
        self,
        session: sqlalchemy.orm.session,
        source: historical.HistoricalSource,
        market: marketplace.Marketplace,
        coin: str,
        fiat: str,
        volume_fiat: float,
        minutes: int,
        drop: float,
    ):
        super().__init__(session, source, market, coin, fiat, volume_fiat, minutes)
        self.drop = drop
        assert self.drop > 0, "Drop triggers must have positive percentages!"

    def is_triggered(self, now: datetime.datetime) -> bool:
        price = self.source.get_price(now, self.coin, self.fiat)
        then = now - datetime.timedelta(minutes=self.minutes)
        try:
            then_price = self.source.get_price(then, self.coin, self.fiat)
        except historical.HistoricalError:
            return False
        critical = then_price.last * (1 - self.drop / 100)
        return price.last < critical

    def get_name(self) -> str:
        return f"{self.coin} drop {self.drop} % in {self.minutes} minutes"


class TrueTrigger(BuyTrigger):
    def is_triggered(self, now: datetime.datetime) -> bool:
        return True

    def get_name(self) -> str:
        return f"{self.coin} every {self.minutes} minutes"


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
    def __init__(self, session: sqlalchemy.orm.session, interval: datetime.timedelta):
        super().__init__()
        self.session = session
        self.interval = interval
        self.last_cleaning = None

    def is_triggered(self, now: datetime.datetime) -> bool:
        return True

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        if self.last_cleaning is None:
            return True
        return self.last_cleaning < now - self.interval

    def fire(self, now: datetime.datetime) -> None:
        datamodel.garbage_collect_db(
            self.session,
            now - self.interval,
        )

    def get_name(self) -> str:
        return "Database cleaning"


def make_buy_triggers(config, session, source, market) -> typing.List[Trigger]:
    active_triggers = []
    if "triggers" in config and config["triggers"] is not None:
        for trigger_spec in config["triggers"]:
            trigger = DropTrigger(
                session=session,
                source=source,
                market=market,
                coin=trigger_spec["coin"].upper(),
                fiat=trigger_spec["fiat"].upper(),
                volume_fiat=trigger_spec["volume_fiat"],
                drop=trigger_spec["drop"],
                minutes=trigger_spec["minutes"],
            )
            logger.debug(f"Constructed trigger: {trigger.get_name()}")
            active_triggers.append(trigger)

    if "timers" in config and config["timers"] is not None:
        for timer_spec in config["timers"]:
            trigger = TrueTrigger(
                session=session,
                source=source,
                market=market,
                coin=timer_spec["coin"].upper(),
                fiat=timer_spec["fiat"].upper(),
                volume_fiat=timer_spec["volume_fiat"],
                minutes=timer_spec["minutes"],
            )
            logger.debug(f"Constructed trigger: {trigger.get_name()}")
            active_triggers.append(trigger)
    return active_triggers


def make_triggers(
    config, session, source: historical.HistoricalSource, market
) -> typing.List[Trigger]:
    active_triggers = make_buy_triggers(config, session, source, market)
    longest_cooldown = max(trigger.minutes for trigger in active_triggers)
    active_triggers.append(CheckinTrigger())
    active_triggers.append(
        DatabaseCleaningTrigger(
            session, 2 * datetime.timedelta(minutes=longest_cooldown)
        )
    )

    return active_triggers
