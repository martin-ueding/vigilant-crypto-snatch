import datetime
import os
import sys

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.cli as st_cli

from vigilant_crypto_snatch.configuration import migrations
from vigilant_crypto_snatch.configuration import parse_trigger_spec
from vigilant_crypto_snatch.configuration import YamlConfiguration
from vigilant_crypto_snatch.datastorage import Datastore
from vigilant_crypto_snatch.datastorage import make_datastore
from vigilant_crypto_snatch.evaluation import drop_survey
from vigilant_crypto_snatch.evaluation import InterpolatingSource
from vigilant_crypto_snatch.evaluation import make_dataframe_from_json
from vigilant_crypto_snatch.evaluation import SimulationMarketplace
from vigilant_crypto_snatch.historical import get_hourly_data
from vigilant_crypto_snatch.historical import HistoricalError
from vigilant_crypto_snatch.myrequests import perform_http_request
from vigilant_crypto_snatch.triggers import BuyTrigger
from vigilant_crypto_snatch.triggers import make_buy_trigger


def get_currency_pairs(api_key: str) -> list:
    r = perform_http_request(
        f"https://min-api.cryptocompare.com/data/v2/pair/mapping/exchange"
        f"?e=Kraken"
        f"&api_key={api_key}"
    )
    data = r["Data"]["current"]
    pairs = [(e["fsym"], e["tsym"]) for e in data]
    return pairs


def sub_home(sidebar_settings):
    st.title("Home")

    st.markdown(
        """
    Welcome to the evaluation toolbox. Select a currency pair in the sidebar and then use the various tools.
    """
    )


def sub_price(sidebar_settings):
    st.title("Close price")

    show_close_chart(sidebar_settings)


def show_close_chart(sidebar_settings):
    close_chart = (
        alt.Chart(sidebar_settings.data)
        .mark_line()
        .encode(
            x=alt.X("datetime", title="Date"),
            y=alt.X(
                "close", title=f"Close {sidebar_settings.fiat}/{sidebar_settings.coin}"
            ),
        )
        .interactive()
    )
    st.altair_chart(close_chart, use_container_width=True)


def sub_drop_survey(sidebar_settings):
    st.markdown("# Drop survey")

    show_close_chart(sidebar_settings)

    time_begin, time_end = make_time_slider(sidebar_settings)
    data_datetime = sidebar_settings.data["datetime"]
    selection = (time_begin <= data_datetime) & (data_datetime <= time_end)

    range_delay = st.slider(
        "Delay / hours", min_value=1, max_value=14 * 24, value=(1, 48)
    )
    range_percentage = st.slider("Drop / %", min_value=0, max_value=100, value=(1, 30))
    st.altair_chart(
        make_survey_chart(
            sidebar_settings.data.loc[selection].reset_index(),
            range_delay,
            range_percentage,
            sidebar_settings.coin,
            sidebar_settings.fiat,
        ),
        use_container_width=True,
    )


def make_trigger_ui(datastore, source, market, sidebar_settings, i) -> BuyTrigger:
    trigger_spec = {"fiat": sidebar_settings.fiat, "coin": sidebar_settings.coin}

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
        f"Volume / {sidebar_settings.fiat}",
        min_value=25,
        max_value=None,
        value=25,
        key=f"trigger_volume_{i}",
    )

    triggered_delegate_type = st.radio(
        "Triggered type", ["Drop", "Time"], key=f"triggered_delegate_type{i}"
    )

    if triggered_delegate_type == "Drop":
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

    return make_buy_trigger(datastore, source, market, parse_trigger_spec(trigger_spec))


def sub_trigger_simulation(sidebar_settings):
    st.title("Trigger simulation")

    datastore = make_datastore(None)
    source = InterpolatingSource(sidebar_settings.data)
    market = SimulationMarketplace(source)

    time_begin, time_end = make_time_slider(sidebar_settings)

    number_of_triggers = st.number_input(
        "Number of triggers", min_value=1, max_value=None, value=2
    )

    st.markdown("# Parameters")

    with st.form("triggers"):
        active_triggers = []
        for i in range(number_of_triggers):
            if i % 3 == 0:
                col = st.columns(min(number_of_triggers - i, 3))
            with col[i % 3]:
                active_triggers.append(
                    make_trigger_ui(datastore, source, market, sidebar_settings, i)
                )
        if not st.form_submit_button("Go!"):
            return

    st.markdown("# Run")

    st.markdown("Simulating triggers …")
    simulation_progress_bar = st.progress(0.0)

    data_datetime = sidebar_settings.data["datetime"]
    selection = (time_begin <= data_datetime) & (data_datetime <= time_end)

    trades = simulate_triggers(
        sidebar_settings.data.loc[selection].reset_index(),
        sidebar_settings.coin,
        sidebar_settings.fiat,
        active_triggers,
        datastore,
        lambda p: simulation_progress_bar.progress(p),
    )

    if len(trades) == 0:
        st.markdown("This trigger did not execute once.")
        st.stop()

    st.markdown("Accumulating value …")
    cumsum_progress_bar = st.progress(0.0)

    result = []
    for i, elem in enumerate(data_datetime.loc[selection]):
        for t in active_triggers:
            sel1 = trades["timestamp"] <= elem
            sel2 = trades["trigger_name"] == t.get_name()
            sel12 = sel1 & sel2
            cumsum_coin = np.sum(trades["volume_coin"][sel12])
            cumsum_fiat = np.sum(trades["volume_fiat"][sel12])
            value_fiat = cumsum_coin * sidebar_settings.data.loc[i, "close"]
            result.append(
                dict(
                    datetime=elem,
                    trigger_name=t.get_name(),
                    cumsum_coin=cumsum_coin,
                    cumsum_fiat=cumsum_fiat,
                    value_fiat=value_fiat,
                )
            )
        cumsum_progress_bar.progress((i + 1) / len(data_datetime.loc[selection]))
    value = pd.DataFrame(result)

    st.markdown("# Summary")

    summary_rows = []
    for t in active_triggers:
        sub_trades = trades[trades["trigger_name"] == t.get_name()]
        sub_values = value[value["trigger_name"] == t.get_name()]
        num_trigger_executions = len(sub_trades)
        cumsum_fiat = sub_values["cumsum_fiat"].iat[-1]
        cumsum_coin = sub_values["cumsum_coin"].iat[-1]
        value_fiat = sub_values["value_fiat"].iat[-1]
        average_price = cumsum_fiat / cumsum_coin
        gain = value_fiat / cumsum_fiat - 1
        period = (
            data_datetime.loc[selection].iat[-1] - data_datetime.loc[selection].iat[0]
        ).days
        yearly_gain = np.power(gain + 1, 365 / period) - 1
        row = {
            "Trigger": t.get_name(),
            "Days": period,
            "Trades": num_trigger_executions,
            f"{sidebar_settings.fiat} invested": cumsum_fiat,
            f"{sidebar_settings.coin} acquired": cumsum_coin,
            f"{sidebar_settings.fiat} value": value_fiat,
            f"Average {sidebar_settings.fiat}/{sidebar_settings.coin}": average_price,
            "Gain %": gain,
            "Gain %/a": yearly_gain,
        }
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)
    st.dataframe(summary)

    value_long = value.rename(
        {"cumsum_fiat": "Invested", "value_fiat": "Value"}, axis=1
    ).melt(["datetime", "trigger_name"], ["Invested", "Value"])

    gain_chart = (
        alt.Chart(value_long)
        .mark_line()
        .encode(
            x=alt.X("datetime", title="Time"),
            y=alt.Y("value", title=f"{sidebar_settings.fiat}"),
            strokeDash=alt.StrokeDash(
                "variable", title="Variable", legend=alt.Legend(orient="bottom")
            ),
            color=alt.Color(
                "trigger_name", title="Trigger", legend=alt.Legend(orient="bottom")
            ),
        )
        .interactive()
    )

    st.markdown("# Diagram with gains")
    st.altair_chart(gain_chart, use_container_width=True)

    st.markdown("# Table with trades")
    st.dataframe(trades)


def make_time_slider(sidebar_settings):
    time_begin = np.min(sidebar_settings.data["datetime"]).toordinal()
    time_end = np.max(sidebar_settings.data["datetime"]).toordinal()
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


def simulate_triggers(
    data: pd.DataFrame,
    coin: str,
    fiat: str,
    active_triggers,
    datastore: Datastore,
    progress_callback=lambda n: None,
) -> pd.DataFrame:
    for i in data.index:
        row = data.loc[i]
        now = row["datetime"]
        for trigger in active_triggers:
            if not (trigger.coin == coin and trigger.fiat == fiat):
                continue
            try:
                if trigger.is_triggered(now):
                    if trigger.has_cooled_off(now):
                        trigger.fire(now)
                    else:
                        pass
            except HistoricalError as e:
                pass
        progress_callback((i + 1) / len(data))

    all_trades = datastore.get_all_trades()
    trade_df = pd.DataFrame([trade.to_dict() for trade in all_trades])
    return trade_df


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
    if ("BTC", "EUR") not in available_pairs:
        available_pairs.append(("BTC", "EUR"))
    available_fiats = list({f for c, f in available_pairs})
    available_fiats.sort()
    fiat = st.sidebar.selectbox(
        "Fiat", available_fiats, index=available_fiats.index("EUR")
    )
    available_coins = list({c for c, f in available_pairs if f == fiat})
    available_coins.sort()
    coin = st.sidebar.selectbox(
        "Coin", available_coins, index=available_coins.index("BTC")
    )

    data = get_hourly_data(coin, fiat, api_key)
    data = make_dataframe_from_json(data)

    sidebar_settings = Namespace()
    sidebar_settings.coin = coin
    sidebar_settings.fiat = fiat
    sidebar_settings.data = data

    tools = {
        "Home": sub_home,
        "Price": sub_price,
        "Drop survey": sub_drop_survey,
        "Trigger simulation": sub_trigger_simulation,
    }

    nav = st.sidebar.radio("Tool", list(tools.keys()))
    tools[nav](sidebar_settings)


@st.cache(allow_output_mutation=True)
def make_survey_chart(data, range_delay, range_percentage, coin, fiat):
    hours, drops, factors = drop_survey(
        data, np.arange(*range_delay), np.linspace(*range_percentage, 15) / 100.0
    )
    x, y = np.meshgrid(hours, drops)
    survey_long = pd.DataFrame(
        {
            "hours": x.ravel(),
            "drop": [f"{yy:05.2f}" for yy in y.ravel() * 100],
            "factor": factors.ravel(),
        }
    )

    survey_chart = (
        alt.Chart(survey_long)
        .mark_rect()
        .encode(
            x=alt.X("hours:O", title="Delay / hours"),
            y=alt.Y("drop:O", title="Drop / %"),
            color=alt.Color(
                "factor:Q", title=f"{coin}/{fiat}", scale=alt.Scale(scheme="turbo")
            ),
        )
    )
    return survey_chart


if __name__ == "__main__" and st._is_running_with_streamlit:
    ui()


def main():
    migrations.run_migrations()
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(st_cli.main())
