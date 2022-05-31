import pytest

from ..core import AssetPair
from .interface import InvalidTriggerSpec
from .interface import TriggerSpec


def test_missing_delay() -> None:
    with pytest.raises(InvalidTriggerSpec):
        TriggerSpec(
            name="Test",
            asset_pair=AssetPair("BTC", "EUR"),
            cooldown_minutes=1,
            drop_percentage=1,
        )


def test_missing_drop_percentage() -> None:
    with pytest.raises(InvalidTriggerSpec):
        TriggerSpec(
            name="Test",
            asset_pair=AssetPair("BTC", "EUR"),
            cooldown_minutes=1,
            delay_minutes=1,
        )
