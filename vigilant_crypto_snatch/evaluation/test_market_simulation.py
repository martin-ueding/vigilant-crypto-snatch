from ..triggers import TriggerSpec
from .market_simulation import simulate_triggers
from .price_data import make_test_dataframe


def test_simulate_triggers() -> None:
    trigger_spec = TriggerSpec(
        coin="BTC", fiat="EUR", cooldown_minutes=1, volume_fiat=1
    )
    data = make_test_dataframe()
    trades, trigger_names = simulate_triggers(data, "BTC", "EUR", [trigger_spec])
