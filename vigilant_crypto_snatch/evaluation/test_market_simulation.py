from ..triggers import TriggerSpec
from .market_simulation import accumulate_value
from .market_simulation import make_gain_chart
from .market_simulation import simulate_triggers
from .market_simulation import summarize_simulation
from .price_data import make_test_dataframe


def test_simulate_triggers() -> None:
    coin = "BTC"
    fiat = "EUR"
    trigger_specs = [
        TriggerSpec(coin=coin, fiat=fiat, cooldown_minutes=1, volume_fiat=1),
        TriggerSpec(coin=coin, fiat=fiat, cooldown_minutes=10000, volume_fiat=1),
    ]
    data = make_test_dataframe()

    trades, trigger_names = simulate_triggers(data, coin, fiat, trigger_specs)
    value = accumulate_value(data, trades, trigger_names)
    summary = summarize_simulation(data, trades, value, trigger_names, coin, fiat)
    gain_chart = make_gain_chart(value, fiat)
