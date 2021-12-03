from vigilant_crypto_snatch.configuration.interface import get_used_currencies
from vigilant_crypto_snatch.core import TriggerSpec


def test_used_currencies_empty() -> None:
    assert get_used_currencies([]) == set()


def test_used_currencies_multiple() -> None:
    trigger_specs = [TriggerSpec("BTC", "EUR", 10), TriggerSpec("ETH", "EUR", 10)]
    assert get_used_currencies(trigger_specs) == {"BTC", "EUR", "ETH"}
