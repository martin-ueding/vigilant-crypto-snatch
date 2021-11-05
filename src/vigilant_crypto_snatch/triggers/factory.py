import sys
from typing import List

import dateutil.parser

from .. import datastorage
from .concrete import *
from .triggered_delegates import *
from .volume_fiat_delegates import *


def make_buy_triggers(
    config, session, source, market, dry_run: bool = False
) -> List[BuyTrigger]:
    active_triggers = []
    for trigger_spec in config["triggers"]:
        trigger = make_buy_trigger(session, source, market, trigger_spec, dry_run)
        active_triggers.append(trigger)
    return active_triggers


def make_buy_trigger(
    datastore: datastorage.Datastore,
    source: historical.HistoricalSource,
    market: marketplace.Marketplace,
    trigger_spec: Dict,
    dry_run: bool = False,
) -> BuyTrigger:
    logger.debug(f"Processing trigger spec: {trigger_spec}")

    delay_minutes = get_minutes(trigger_spec, "delay")
    cooldown_minutes = get_minutes(trigger_spec, "cooldown")
    if cooldown_minutes is None:
        logger.critical(f"Trigger needs to have a cooldown: {trigger_spec}")
        sys.exit(1)

    # We first need to construct the `TriggeredDelegate` and find out which type it is.
    triggered_delegate: TriggeredDelegate
    if delay_minutes is not None and "drop_percentage" in trigger_spec:
        triggered_delegate = DropTriggeredDelegate(
            coin=trigger_spec["coin"].upper(),
            fiat=trigger_spec["fiat"].upper(),
            delay_minutes=delay_minutes,
            drop_percentage=trigger_spec["drop_percentage"],
            source=source,
        )
    else:
        triggered_delegate = TrueTriggeredDelegate()
    logger.debug(f"Constructed: {triggered_delegate}")

    # Then we need the `VolumeFiatDelegate`.
    volume_fiat_delegate: VolumeFiatDelegate
    if "volume_fiat" in trigger_spec:
        volume_fiat_delegate = FixedVolumeFiatDelegate(trigger_spec["volume_fiat"])
    elif "percentage_fiat" in trigger_spec:
        volume_fiat_delegate = RatioVolumeFiatDelegate(
            trigger_spec["fiat"].upper(), trigger_spec["percentage_fiat"], market
        )
    else:
        raise RuntimeError("Could not determine fiat volume strategy from config.")
    logger.debug(f"Constructed: {volume_fiat_delegate}")

    result = BuyTrigger(
        datastore=datastore,
        source=source,
        market=market,
        coin=trigger_spec["coin"].upper(),
        fiat=trigger_spec["fiat"].upper(),
        cooldown_minutes=cooldown_minutes,
        triggered_delegate=triggered_delegate,
        volume_fiat_delegate=volume_fiat_delegate,
        name=trigger_spec.get("name", None),
        start=get_start(trigger_spec),
        dry_run=dry_run,
    )
    logger.debug(f"Constructed trigger: {result.get_name()}")
    return result


def make_triggers(
    config: Dict,
    datastore: datastorage.Datastore,
    source: historical.HistoricalSource,
    market: marketplace.Marketplace,
    dry_run: bool = False,
) -> Sequence[Trigger]:
    buy_triggers = make_buy_triggers(config, datastore, source, market, dry_run)
    longest_cooldown = max(
        (
            trigger.triggered_delegate.delay_minutes
            for trigger in buy_triggers
            if isinstance(trigger.triggered_delegate, DropTriggeredDelegate)
        ),
        default=120,
    )
    active_triggers: List[Trigger] = list(buy_triggers)
    active_triggers.append(CheckinTrigger())
    active_triggers.append(
        DatabaseCleaningTrigger(
            datastore, 2 * datetime.timedelta(minutes=longest_cooldown)
        )
    )

    return active_triggers


def get_start(trigger_spec: dict) -> Optional[datetime.datetime]:
    if "start" in trigger_spec:
        return dateutil.parser.parse(trigger_spec["start"])
    else:
        return None


def get_minutes(trigger_spec: dict, key: str) -> Optional[int]:
    if f"{key}_days" in trigger_spec:
        return trigger_spec[f"{key}_days"] * 60 * 24
    if f"{key}_hours" in trigger_spec:
        return trigger_spec[f"{key}_hours"] * 60
    elif f"{key}_minutes" in trigger_spec:
        return trigger_spec[f"{key}_minutes"]
    else:
        return None
