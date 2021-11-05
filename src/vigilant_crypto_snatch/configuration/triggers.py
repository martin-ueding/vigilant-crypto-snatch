import datetime
import sys
from typing import Optional

import dateutil.parser

from .. import logger
from ..core import TriggerSpec


def parse_trigger_spec(trigger_spec_dict: dict) -> TriggerSpec:
    cooldown_minutes = get_minutes(trigger_spec_dict, "cooldown")
    if cooldown_minutes is None:
        logger.critical(f"Trigger needs to have a cooldown: {trigger_spec_dict}")
        sys.exit(1)

    trigger_spec = TriggerSpec(
        fiat=trigger_spec_dict["fiat"].upper(),
        coin=trigger_spec_dict["coin"].upper(),
        delay_minutes=get_minutes(trigger_spec_dict, "delay"),
        cooldown_minutes=cooldown_minutes,
        drop_percentage=trigger_spec_dict.get("drop_percentage", None),
        volume_fiat=trigger_spec_dict.get("volume_fiat", None),
        percentage_fiat=trigger_spec_dict.get("percentage_fiat", None),
        name=trigger_spec_dict.get("name", None),
        start=get_start(trigger_spec_dict),
    )

    return trigger_spec


def get_start(trigger_spec_dict: dict) -> Optional[datetime.datetime]:
    if "start" in trigger_spec_dict:
        return dateutil.parser.parse(trigger_spec_dict["start"])
    else:
        return None


def get_minutes(config: dict, key: str) -> Optional[int]:
    if f"{key}_days" in config:
        return config[f"{key}_days"] * 60 * 24
    if f"{key}_hours" in config:
        return config[f"{key}_hours"] * 60
    elif f"{key}_minutes" in config:
        return config[f"{key}_minutes"]
    else:
        return None
