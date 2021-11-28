import datetime
from typing import List

from vigilant_crypto_snatch import logger
from vigilant_crypto_snatch.core import TriggerSpec
from vigilant_crypto_snatch.datastorage.interface import Datastore
from vigilant_crypto_snatch.historical.interface import HistoricalSource
from vigilant_crypto_snatch.marketplace.interface import Marketplace
from vigilant_crypto_snatch.triggers.concrete import BuyTrigger
from vigilant_crypto_snatch.triggers.concrete import CheckinTrigger
from vigilant_crypto_snatch.triggers.concrete import DatabaseCleaningTrigger
from vigilant_crypto_snatch.triggers.interface import Trigger
from vigilant_crypto_snatch.triggers.triggered_delegates import DropTriggeredDelegate
from vigilant_crypto_snatch.triggers.triggered_delegates import TriggeredDelegate
from vigilant_crypto_snatch.triggers.triggered_delegates import TrueTriggeredDelegate
from vigilant_crypto_snatch.triggers.volume_fiat_delegates import (
    FixedVolumeFiatDelegate,
)
from vigilant_crypto_snatch.triggers.volume_fiat_delegates import (
    RatioVolumeFiatDelegate,
)
from vigilant_crypto_snatch.triggers.volume_fiat_delegates import VolumeFiatDelegate


def make_buy_triggers(
    config: List[TriggerSpec], session, source, market, dry_run: bool = False
) -> List[BuyTrigger]:
    active_triggers = []
    for trigger_spec in config:
        trigger = make_buy_trigger(session, source, market, trigger_spec, dry_run)
        active_triggers.append(trigger)
    return active_triggers


def make_buy_trigger(
    datastore: Datastore,
    source: HistoricalSource,
    market: Marketplace,
    trigger_spec: TriggerSpec,
    dry_run: bool = False,
) -> BuyTrigger:
    logger.debug(f"Processing trigger spec: {trigger_spec}")

    # We first need to construct the `TriggeredDelegate` and find out which type it is.
    triggered_delegate: TriggeredDelegate
    if (
        trigger_spec.delay_minutes is not None
        and trigger_spec.drop_percentage is not None
    ):
        triggered_delegate = DropTriggeredDelegate(
            coin=trigger_spec.coin,
            fiat=trigger_spec.fiat,
            delay_minutes=trigger_spec.delay_minutes,
            drop_percentage=trigger_spec.drop_percentage,
            source=source,
        )
    else:
        triggered_delegate = TrueTriggeredDelegate()
    logger.debug(f"Constructed: {triggered_delegate}")

    # Then we need the `VolumeFiatDelegate`.
    volume_fiat_delegate: VolumeFiatDelegate
    if trigger_spec.volume_fiat is not None:
        volume_fiat_delegate = FixedVolumeFiatDelegate(trigger_spec.volume_fiat)
    elif trigger_spec.percentage_fiat is not None:
        volume_fiat_delegate = RatioVolumeFiatDelegate(
            trigger_spec.fiat, trigger_spec.percentage_fiat, market
        )
    else:
        raise RuntimeError("Could not determine fiat volume strategy from config.")
    logger.debug(f"Constructed: {volume_fiat_delegate}")

    result = BuyTrigger(
        datastore=datastore,
        source=source,
        market=market,
        coin=trigger_spec.coin,
        fiat=trigger_spec.fiat,
        cooldown_minutes=trigger_spec.cooldown_minutes,
        triggered_delegate=triggered_delegate,
        volume_fiat_delegate=volume_fiat_delegate,
        name=trigger_spec.name,
        start=trigger_spec.start,
        dry_run=dry_run,
    )
    logger.debug(f"Constructed trigger: {result.get_name()}")
    return result


def make_triggers(
    config: List[TriggerSpec],
    datastore: Datastore,
    source: HistoricalSource,
    market: Marketplace,
    dry_run: bool = False,
) -> List[Trigger]:
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
