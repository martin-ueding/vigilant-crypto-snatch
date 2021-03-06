import datetime
import abc
import typing

import sqlalchemy.orm

from . import datamodel
from . import historical
from .marketplace import marketplace
from . import logger


class TriggeredDelegate(object):
    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()


class DropTriggeredDelegate(TriggeredDelegate):
    def __init__(
        self,
        coin: str,
        fiat: str,
        delay_minutes: int,
        drop_percentage: float,
        source: historical.HistoricalSource,
    ):
        self.coin = coin
        self.fiat = fiat
        self.delay_minutes = delay_minutes
        self.drop_percentage = drop_percentage
        self.source = source

    def is_triggered(self, now: datetime.datetime) -> bool:
        price = self.source.get_price(now, self.coin, self.fiat)
        then = now - datetime.timedelta(minutes=self.delay_minutes)
        try:
            then_price = self.source.get_price(then, self.coin, self.fiat)
        except historical.HistoricalError:
            return False
        critical = then_price.last * (1 - self.drop_percentage / 100)
        return price.last < critical

    def __str__(self) -> str:
        return f"Drop(delay_minutes={self.delay_minutes}, drop={self.drop_percentage})"


class TrueTriggeredDelegate(TriggeredDelegate):
    def is_triggered(self, now: datetime.datetime) -> bool:
        return True

    def __str__(self) -> str:
        return f"True()"


class VolumeFiatDelegate(object):
    def get_volume_fiat(self) -> float:
        raise NotImplementedError()


class FixedVolumeFiatDelegate(VolumeFiatDelegate):
    def __init__(self, volume_fiat: float):
        self.volume_fiat = volume_fiat

    def get_volume_fiat(self) -> float:
        return self.volume_fiat

    def __str__(self) -> str:
        return f"Fixed(volume_fiat={self.volume_fiat})"


class RatioVolumeFiatDelegate(VolumeFiatDelegate):
    def __init__(
        self, fiat: str, percentage_fiat: float, market: marketplace.Marketplace
    ):
        self.fiat = fiat
        self.market = market
        self.percentage_fiat = percentage_fiat

    def get_volume_fiat(self) -> float:
        balances = self.market.get_balance()
        balance_fiat = balances[self.fiat]
        return balance_fiat * self.percentage_fiat / 100

    def __str__(self) -> str:
        return f"Ratio(percentage_fiat={self.percentage_fiat})"


class Trigger(object):
    def __init__(self):
        self.trials = 0

    def get_name(self) -> str:
        raise NotImplementedError()

    def fire(self, now: datetime.datetime) -> None:
        raise NotImplementedError()

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()

    def reset_trials(self):
        self.trials = 0

    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()


class BuyTrigger(Trigger, abc.ABC):
    def __init__(
        self,
        session: sqlalchemy.orm.session,
        source: historical.HistoricalSource,
        market: marketplace.Marketplace,
        coin: str,
        fiat: str,
        cooldown_minutes: int,
        triggered_delegate: TriggeredDelegate,
        volume_fiat_delegate: VolumeFiatDelegate,
        name: typing.Optional[str],
    ):
        super().__init__()
        self.session = session
        self.source = source
        self.market = market
        self.coin = coin
        self.fiat = fiat
        self.cooldown_minutes = cooldown_minutes
        self.triggered_delegate = triggered_delegate
        self.volume_fiat_delegate = volume_fiat_delegate
        self.name = name
        self.reset_trials()

    def is_triggered(self, now: datetime.datetime) -> bool:
        return self.triggered_delegate.is_triggered(now)

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        then = now - datetime.timedelta(minutes=self.cooldown_minutes)
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
        volume_fiat = self.volume_fiat_delegate.get_volume_fiat()
        volume_coin = round(volume_fiat / price.last, 8)
        self.perform_buy(volume_coin, volume_fiat, now)

    def perform_buy(
        self, volume_coin: float, volume_fiat: float, now: datetime.datetime
    ) -> None:
        self.market.place_order(self.coin, self.fiat, volume_coin)
        trade = datamodel.Trade(
            timestamp=now,
            trigger_name=self.get_name(),
            volume_coin=volume_coin,
            volume_fiat=volume_fiat,
            coin=self.coin,
            fiat=self.fiat,
        )
        self.session.add(trade)
        self.session.commit()

        rate = volume_fiat / volume_coin
        buy_message = f"{volume_coin} {self.coin} for {volume_fiat} {self.fiat} ({rate} {self.fiat}/{self.coin}) on {self.market.get_name()} due to “{self.get_name()}”"
        logger.info(f"Bought {buy_message}.")
        marketplace.report_balances(self.market)

    def get_name(self) -> str:
        if self.name is None:
            return f"Buy(cooldown_minutes={self.cooldown_minutes}, trigger={str(self.triggered_delegate)}, volume_fiat={str(self.volume_fiat_delegate)})"
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


def make_buy_triggers(config, session, source, market) -> typing.List[BuyTrigger]:
    active_triggers = []
    for trigger_spec in config["triggers"]:
        trigger = make_buy_trigger(session, source, market, trigger_spec)
        active_triggers.append(trigger)
    return active_triggers


def make_buy_trigger(session, source, market, trigger_spec) -> BuyTrigger:
    logger.debug(f"Processing trigger spec: {trigger_spec}")

    # We first need to construct the `TriggeredDelegate` and find out which type it is.
    if "delay_minutes" in trigger_spec and "drop_percentage" in trigger_spec:
        triggered_delegate = DropTriggeredDelegate(
            coin=trigger_spec["coin"].upper(),
            fiat=trigger_spec["fiat"].upper(),
            delay_minutes=trigger_spec["delay_minutes"],
            drop_percentage=trigger_spec["drop_percentage"],
            source=source,
        )
    else:
        triggered_delegate = TrueTriggeredDelegate()
    logger.debug(f"Constructed: {triggered_delegate}")

    # Then we need the `VolumeFiatDelegate`.
    if "volume_fiat" in trigger_spec:
        volume_fiat_delegate = FixedVolumeFiatDelegate(trigger_spec["volume_fiat"])
    elif "percentage_fiat" in trigger_spec:
        volume_fiat_delegate = RatioVolumeFiatDelegate(
            trigger_spec["fiat"], trigger_spec["percentage_fiat"], market
        )
    else:
        raise RuntimeError("Could not determine fiat volume strategy from config.")
    logger.debug(f"Constructed: {volume_fiat_delegate}")

    result = BuyTrigger(
        session=session,
        source=source,
        market=market,
        coin=trigger_spec["coin"].upper(),
        fiat=trigger_spec["fiat"].upper(),
        cooldown_minutes=trigger_spec["cooldown_minutes"],
        triggered_delegate=triggered_delegate,
        volume_fiat_delegate=volume_fiat_delegate,
        name=trigger_spec.get("name", None),
    )
    logger.debug(f"Constructed trigger: {result.get_name()}")
    return result


def make_triggers(
    config, session, source: historical.HistoricalSource, market
) -> typing.List[Trigger]:
    active_triggers = make_buy_triggers(config, session, source, market)
    longest_cooldown = max(
        trigger.triggered_delegate.delay_minutes
        for trigger in active_triggers
        if isinstance(trigger.triggered_delegate, DropTriggeredDelegate)
    )
    active_triggers.append(CheckinTrigger())
    active_triggers.append(
        DatabaseCleaningTrigger(
            session, 2 * datetime.timedelta(minutes=longest_cooldown)
        )
    )

    return active_triggers
