import datetime
from typing import Dict
from typing import List
from typing import Optional

from .. import logger
from ..datastorage import Datastore
from ..feargreed import AlternateMeFearAndGreedIndex
from ..historical import HistoricalSource
from ..marketplace import Marketplace
from .concrete import BuyTrigger
from .concrete import CheckinTrigger
from .concrete import DatabaseCleaningTrigger
from .interface import Trigger
from .interface import TriggerSpec
from .triggered_delegates import CooldownTriggeredDelegate
from .triggered_delegates import DropTriggeredDelegate
from .triggered_delegates import FearAndGreedIndexTriggeredDelegate
from .triggered_delegates import StartTriggeredDelegate
from .triggered_delegates import SufficientFundsTriggeredDelegate
from .triggered_delegates import TriggeredDelegate
from .volume_fiat_delegates import FixedVolumeFiatDelegate
from .volume_fiat_delegates import RatioVolumeFiatDelegate
from .volume_fiat_delegates import VolumeFiatDelegate


def make_buy_triggers(
    config: List[TriggerSpec], session, source, market
) -> List[BuyTrigger]:
    active_triggers = []
    for trigger_spec in config:
        trigger = make_buy_trigger(session, source, market, trigger_spec)
        active_triggers.append(trigger)
    return active_triggers


def make_buy_trigger(
    datastore: Datastore,
    source: HistoricalSource,
    market: Marketplace,
    trigger_spec: TriggerSpec,
) -> BuyTrigger:
    logger.debug(f"Processing trigger spec: {trigger_spec}")

    # We first need to construct the `TriggeredDelegate` and find out which type it is.
    triggered_delegates: Dict[str, Optional[TriggeredDelegate]] = {}

    if (
        trigger_spec.delay_minutes is not None
        and trigger_spec.drop_percentage is not None
    ):
        triggered_delegates["Drop"] = DropTriggeredDelegate(
            asset_pair=trigger_spec.asset_pair,
            delay_minutes=trigger_spec.delay_minutes,
            drop_percentage=trigger_spec.drop_percentage,
            source=source,
        )
    else:
        triggered_delegates["Drop"] = None

    if trigger_spec.fear_and_greed_index_below:
        triggered_delegates["Fear & Greed"] = FearAndGreedIndexTriggeredDelegate(
            trigger_spec.fear_and_greed_index_below,
            AlternateMeFearAndGreedIndex(),
        )
    else:
        triggered_delegates["Fear & Greed"] = None

    if trigger_spec.start is not None:
        triggered_delegates["Start"] = StartTriggeredDelegate(trigger_spec.start)
    else:
        triggered_delegates["Start"] = None

    triggered_delegates["Cooldown"] = CooldownTriggeredDelegate(
        trigger_spec.cooldown_minutes,
        datastore,
        trigger_spec.asset_pair,
        trigger_spec.name,
    )

    if trigger_spec.volume_fiat is not None:
        triggered_delegates["Funds"] = SufficientFundsTriggeredDelegate(
            trigger_spec.volume_fiat, trigger_spec.asset_pair.fiat, market
        )
    else:
        triggered_delegates["Funds"] = None

    logger.debug(f"Constructed: {triggered_delegates}")

    # Then we need the `VolumeFiatDelegate`.
    volume_fiat_delegate: VolumeFiatDelegate
    if trigger_spec.volume_fiat is not None:
        volume_fiat_delegate = FixedVolumeFiatDelegate(trigger_spec.volume_fiat)
    elif trigger_spec.percentage_fiat is not None:
        volume_fiat_delegate = RatioVolumeFiatDelegate(
            trigger_spec.asset_pair.fiat, trigger_spec.percentage_fiat, market
        )
    else:
        raise RuntimeError("Could not determine fiat volume strategy from config.")
    logger.debug(f"Constructed: {volume_fiat_delegate}")

    result = BuyTrigger(
        datastore=datastore,
        source=source,
        market=market,
        asset_pair=trigger_spec.asset_pair,
        triggered_delegates=triggered_delegates,
        volume_fiat_delegate=volume_fiat_delegate,
        name=trigger_spec.name,
    )
    logger.debug(f"Constructed trigger: {result.get_name()}")
    return result


def make_triggers(
    config: List[TriggerSpec],
    datastore: Datastore,
    source: HistoricalSource,
    market: Marketplace,
) -> List[Trigger]:
    buy_triggers = make_buy_triggers(config, datastore, source, market)
    longest_cooldown = max(
        (
            trigger_spec.delay_minutes
            for trigger_spec in config
            if trigger_spec.delay_minutes
        ),
        default=0,
    )
    active_triggers: List[Trigger] = list(buy_triggers)
    active_triggers.append(CheckinTrigger())
    active_triggers.append(
        DatabaseCleaningTrigger(
            datastore,
            max(
                2 * datetime.timedelta(minutes=longest_cooldown),
                datetime.timedelta(days=90),
            ),
        )
    )

    return active_triggers
