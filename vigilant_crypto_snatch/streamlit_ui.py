import dataclasses
import datetime
import os
import sys
from typing import Any
from typing import Dict

import pandas as pd
import streamlit as st
import streamlit.cli as st_cli

from vigilant_crypto_snatch.configuration import migrations
from vigilant_crypto_snatch.configuration import parse_trigger_spec
from vigilant_crypto_snatch.configuration import YamlConfiguration
from vigilant_crypto_snatch.core import AssetPair
from vigilant_crypto_snatch.evaluation import accumulate_value
from vigilant_crypto_snatch.evaluation import get_available_coins
from vigilant_crypto_snatch.evaluation import get_available_fiats
from vigilant_crypto_snatch.evaluation import get_currency_pairs
from vigilant_crypto_snatch.evaluation import get_hourly_data
from vigilant_crypto_snatch.evaluation import make_close_chart
from vigilant_crypto_snatch.evaluation import make_dataframe_from_json
from vigilant_crypto_snatch.evaluation import make_fear_greed_chart
from vigilant_crypto_snatch.evaluation import make_gain_chart
from vigilant_crypto_snatch.evaluation import make_survey_chart
from vigilant_crypto_snatch.evaluation import simulate_triggers
from vigilant_crypto_snatch.evaluation import summarize_simulation
from vigilant_crypto_snatch.reporting import get_user_trades_df
from vigilant_crypto_snatch.reporting import plot_fiat_spent_per_month
from vigilant_crypto_snatch.reporting import plot_gains_from_individual_trades
from vigilant_crypto_snatch.reporting import plot_gains_per_month
from vigilant_crypto_snatch.reporting import plot_value_and_investment
from vigilant_crypto_snatch.triggers import TriggerSpec


@dataclasses.dataclass()
class SidebarSettings:
    asset_pair: AssetPair
    data: pd.DataFrame


def sub_home(sidebar_settings: SidebarSettings):
    st.title("Home")

    st.markdown(
        """
    Welcome to the evaluation toolbox. Select a currency pair in the sidebar and then use the various tools.
    """
    )


def sub_price(sidebar_settings: SidebarSettings):
    st.title("Close price")

    show_close_chart(sidebar_settings)


def show_close_chart(sidebar_settings: SidebarSettings):
    close_chart = make_close_chart(sidebar_settings.data, sidebar_settings.asset_pair)
    st.altair_chart(close_chart, use_container_width=True)


def sub_drop_survey(sidebar_settings: SidebarSettings):
    st.markdown("# Drop survey")

    show_close_chart(sidebar_settings)

    time_begin, time_end = make_time_slider(sidebar_settings)
    data_datetime = sidebar_settings.data["datetime"]
    selection = (time_begin <= data_datetime) & (data_datetime <= time_end)

    range_delay = st.slider(
        "Delay / hours", min_value=1, max_value=14 * 24, value=(1, 48)
    )
    range_percentage = st.slider("Drop / %", min_value=0, max_value=100, value=(1, 30))
    chart = make_survey_chart(
        sidebar_settings.data.loc[selection].reset_index(),
        range_delay,
        range_percentage,
        sidebar_settings.asset_pair,
    )
    st.altair_chart(chart, use_container_width=True)


def make_trigger_ui(sidebar_settings: SidebarSettings, i) -> TriggerSpec:
    trigger_spec: Dict[str, Any] = {
        "fiat": sidebar_settings.asset_pair.fiat,
        "coin": sidebar_settings.asset_pair.coin,
    }

    trigger_spec["name"] = st.text_input(
        "Name",
        f"Trigger {i+1}",
        key=f"name{i}",
    )

    trigger_spec["cooldown_minutes"] = 60 * st.slider(
        "Cooldown / hours",
        min_value=1,
        max_value=14 * 24,
        value=24,
        key=f"cooldown_minutes{i}",
    )

    trigger_spec["volume_fiat"] = st.number_input(
        f"Volume / {sidebar_settings.asset_pair.fiat}",
        min_value=25,
        max_value=None,
        value=25,
        key=f"trigger_volume_{i}",
    )

    if st.checkbox("Use drop strategy", key=f"trigger_volume_{i}"):
        trigger_spec["delay_minutes"] = 60 * st.slider(
            "Delay / hours",
            min_value=1,
            max_value=14 * 24,
            value=24,
            key=f"delay_minutes{i}",
        )
        trigger_spec["drop_percentage"] = st.slider(
            "Drop / %",
            min_value=0,
            max_value=100,
            value=30,
            key=f"drop_percentage{i}",
        )

    if st.checkbox("Use Fear & Greed strategy", key=f"fear_greed_{i}"):
        trigger_spec["fear_and_greed_index_below"] = st.slider(
            "Fear & Greed index below",
            min_value=0,
            max_value=101,
            value=50,
            key=f"fear_greed_{i}",
        )

    return parse_trigger_spec(trigger_spec)


def sub_trigger_simulation(sidebar_settings: SidebarSettings):
    st.title("Trigger simulation")

    time_begin, time_end = make_time_slider(sidebar_settings)
    data_datetime = sidebar_settings.data["datetime"]
    selection = (time_begin <= data_datetime) & (data_datetime <= time_end)

    close_chart = make_close_chart(
        sidebar_settings.data[selection], sidebar_settings.asset_pair
    )
    st.altair_chart(close_chart, use_container_width=True)

    feargreed_chart = make_fear_greed_chart(time_begin, time_end)
    st.altair_chart(feargreed_chart, use_container_width=True)

    st.markdown("# Parameters")

    number_of_triggers = int(
        st.number_input("Number of triggers", min_value=1, max_value=None, value=2)
    )

    trigger_specs = []
    for i in range(number_of_triggers):
        if i % 3 == 0:
            col = st.columns(min(number_of_triggers - i, 3))
        with col[i % 3]:
            trigger_specs.append(make_trigger_ui(sidebar_settings, i))
    if not st.button("Go!"):
        return

    st.markdown("# Run")

    st.markdown("Simulating triggers …")
    simulation_progress_bar = st.progress(0.0)

    trades, trigger_names = simulate_triggers(
        sidebar_settings.data.loc[selection].reset_index(),
        sidebar_settings.asset_pair,
        trigger_specs,
        simulation_progress_bar.progress,
    )

    if len(trades) == 0:
        st.markdown("This trigger did not execute once.")
        st.stop()

    st.markdown("Accumulating value …")
    cumsum_progress_bar = st.progress(0.0)
    value = accumulate_value(
        sidebar_settings.data, trades, trigger_names, cumsum_progress_bar.progress
    )

    st.markdown("# Summary")

    summary = summarize_simulation(
        sidebar_settings.data.loc[selection],
        trades,
        value,
        trigger_names,
        sidebar_settings.asset_pair,
    )
    st.dataframe(summary)

    gain_chart = make_gain_chart(value, sidebar_settings.asset_pair.fiat)
    st.markdown("# Diagram with gains")
    st.altair_chart(gain_chart, use_container_width=True)

    st.markdown("# Table with trades")
    st.dataframe(trades)


def make_time_slider(sidebar_settings: SidebarSettings):
    time_begin = min(sidebar_settings.data["datetime"]).toordinal()
    time_end = max(sidebar_settings.data["datetime"]).toordinal()
    time_range = st.slider(
        "Data range",
        min_value=time_begin,
        max_value=time_end,
        value=(time_begin, time_end),
    )
    time_begin = datetime.datetime.fromordinal(time_range[0])
    time_end = datetime.datetime.fromordinal(time_range[1])
    st.markdown(f"From {time_begin} to {time_end}")
    return time_begin, time_end


def sub_trade_report(sidebar_settings: SidebarSettings) -> None:
    st.title("Trades Report")

    trades = get_user_trades_df()
    if trades is None:
        st.markdown("No user database could be found, therefore nothing can be shown.")
        return

    st.markdown(
        "Here you can find all the trades that have been made with the program."
    )

    st.markdown("# Table")
    st.dataframe(
        trades[
            [
                "timestamp",
                "trigger_name",
                "coin",
                "fiat",
                "volume_coin",
                "volume_fiat",
                "buy_price",
                "current_value",
                "gains",
            ]
        ]
    )

    st.markdown("# Static plots")
    st.markdown(
        "The following plot will not change over time, new data will just be added to the left. It contrast the amount of fiat you have spend to the coin value *at that time*."
    )
    st.altair_chart(plot_value_and_investment(trades), use_container_width=True)

    st.markdown("# Dynamic plots")
    st.markdown(
        "The following plots change over time because they compare the buy price with the coin price _right now_. Should be coin price go up, your ganes from old purchases will also go up."
    )
    st.altair_chart(plot_gains_from_individual_trades(trades), use_container_width=True)
    st.altair_chart(plot_gains_per_month(trades), use_container_width=True)
    st.altair_chart(plot_fiat_spent_per_month(trades), use_container_width=True)


class Namespace(object):
    pass


def get_api_key() -> str:
    var_name = "CRYPTOCOMPARE_API_KEY"
    key = os.environ.get(var_name, None)
    if key is not None:
        return key
    else:
        config = YamlConfiguration()
        return config.get_crypto_compare_config().api_key


def ui():
    api_key = get_api_key()
    st.sidebar.title("Vigilant Crypto Snatch Evaluation")

    available_pairs = get_currency_pairs(api_key)
    available_fiats = get_available_fiats(available_pairs)
    fiat = st.sidebar.selectbox(
        "Fiat", available_fiats, index=available_fiats.index("EUR")
    )
    available_coins = get_available_coins(available_pairs, fiat)
    coin = st.sidebar.selectbox(
        "Coin", available_coins, index=available_coins.index("BTC")
    )

    asset_pair = AssetPair(coin, fiat)

    data = get_hourly_data(asset_pair, api_key)
    data = make_dataframe_from_json(data)

    sidebar_settings = SidebarSettings(asset_pair=asset_pair, data=data)

    tools = {
        "Home": sub_home,
        "Price": sub_price,
        "Drop survey": sub_drop_survey,
        "Trigger simulation": sub_trigger_simulation,
        "Trades report": sub_trade_report,
    }

    nav = st.sidebar.radio("Tool", list(tools.keys()))
    tools[nav](sidebar_settings)


if __name__ == "__main__" and st._is_running_with_streamlit:
    ui()


def main():
    migrations.run_migrations()
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(st_cli.main())
