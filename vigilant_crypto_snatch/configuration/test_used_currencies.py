from ..triggers import TriggerSpec
from .interface import get_used_currencies


def test_used_currencies_empty() -> None:
    assert get_used_currencies([]) == set()


def test_used_currencies_multiple() -> None:
    trigger_specs = [TriggerSpec("BTC", "EUR", 10), TriggerSpec("ETH", "EUR", 10)]
    assert get_used_currencies(trigger_specs) == {"BTC", "EUR", "ETH"}
