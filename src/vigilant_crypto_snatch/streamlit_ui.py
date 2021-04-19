import sys

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.cli as st_cli

from vigilant_crypto_snatch import configuration
from vigilant_crypto_snatch import datamodel
from vigilant_crypto_snatch import evaluation
from vigilant_crypto_snatch import historical
from vigilant_crypto_snatch import triggers


def sub_home(sidebar_settings):
    st.title("Home")

    st.markdown(
        """
    Welcome to the evaluation toolbox. Select a currency pair in the sidebar and then use the various tools.
    """
    )


def sub_price(sidebar_settings):
    st.title("Close price")

    close_chart = (
        alt.Chart(sidebar_settings.data)
        .mark_line()
        .encode(
            x=alt.X("datetime", title="Date"),
            y=alt.X(
                "close", title=f"Close {sidebar_settings.fiat}/{sidebar_settings.coin}"
            ),
        )
    )
    st.altair_chart(close_chart, use_container_width=True)


def sub_drop_survey(sidebar_settings):
    st.markdown("# Drop survey")

    range_delay = st.slider(
        "Delay / hours", min_value=1, max_value=14 * 24, value=(1, 48)
    )
    range_percentage = st.slider("Drop / %", min_value=0, max_value=100, value=(1, 30))
    st.altair_chart(
        make_survey_chart(
            sidebar_settings.data,
            range_delay,
            range_percentage,
            sidebar_settings.coin,
            sidebar_settings.fiat,
        ),
        use_container_width=True,
    )


def sub_trigger_simulation(sidebar_settings):
    st.title("Trigger simulation")

    st.markdown('# Parameters')

    trigger_type = st.radio("Trigger type", ["Drop", "Time"])
    trigger_delay = st.slider("Delay / hours", min_value=1, max_value=14 * 24, value=24)
    if trigger_type == "Drop":
        trigger_percentage = st.slider("Drop / %", min_value=0, max_value=100, value=30)
    trigger_volume = st.number_input(
        f"Volume / {sidebar_settings.fiat}", min_value=25, max_value=None, value=25
    )

    session = datamodel.open_memory_db_session()
    source = evaluation.InterpolatingSource(sidebar_settings.data)
    market = evaluation.SimulationMarketplace(source)

    active_triggers = []
    if trigger_type == "Drop":
        active_triggers.append(
            triggers.DropTrigger(
                session,
                source,
                market,
                sidebar_settings.coin,
                sidebar_settings.fiat,
                trigger_volume,
                trigger_delay * 60,
                trigger_percentage,
            )
        )
    elif trigger_type == "Time":
        active_triggers.append(
            triggers.TrueTrigger(
                session,
                source,
                market,
                sidebar_settings.coin,
                sidebar_settings.fiat,
                trigger_volume,
                trigger_delay * 60,
            )
        )

    trades = simulate_triggers(
        sidebar_settings.data,
        sidebar_settings.coin,
        sidebar_settings.fiat,
        active_triggers,
        session,
    )

    if len(trades) == 0:
        st.markdown("This trigger did not execute once.")
        st.stop()

    value = pd.DataFrame(
        dict(
            datetime=sidebar_settings.data["datetime"],
            cumsum_coin=0.0,
            cumsum_fiat=0.0,
            value_fiat=0.0,
        )
    )

    for i, elem in enumerate(sidebar_settings.data["datetime"]):
        selection = trades["timestamp"] <= elem
        value.loc[i, "cumsum_coin"] = np.sum(trades["volume_coin"][selection])
        value.loc[i, "cumsum_fiat"] = np.sum(trades["volume_fiat"][selection])
        value.loc[i, "value_fiat"] = (
            value.loc[i, "cumsum_coin"] * sidebar_settings.data.loc[i, "close"]
        )

    st.markdown('# Summary')
    num_trigger_executions = len(trades)
    cumsum_fiat = value["cumsum_fiat"].iat[-1]
    cumsum_coin = value["cumsum_coin"].iat[-1]
    value_fiat = value["value_fiat"].iat[-1]
    gain = value_fiat / cumsum_fiat - 1
    period = (sidebar_settings.data["datetime"].iat[-1] - sidebar_settings.data["datetime"].iat[0]).days
    yearly_gain = np.power(gain + 1, 365/period) - 1
    st.markdown(f'''
    - {period} days simulated
    - {num_trigger_executions} trades
    - {cumsum_fiat:.2f} {sidebar_settings.fiat} invested
    - {cumsum_coin:.8f} {sidebar_settings.coin} acquired
    - {value_fiat:.2f} {sidebar_settings.fiat} value
    - {gain*100:.1f} % gain in {period} days
    - {yearly_gain*100:.1f} % estimated yearly gain
    ''')

    value_long = value.rename(
        {"cumsum_fiat": "Invested", "value_fiat": "Value"}, axis=1
    ).melt(["datetime"], ["Invested", "Value"])

    gain_chart = (
        alt.Chart(value_long)
        .mark_line()
        .encode(
            x=alt.X("datetime", title="Delay / hours"),
            y=alt.Y("value", title="xx"),
            color="variable",
        )
    )

    st.markdown('# Diagram with gains')
    st.altair_chart(gain_chart, use_container_width=True)

    st.markdown('# Table with trades')
    st.dataframe(trades)


def simulate_triggers(
    data: pd.DataFrame, coin: str, fiat: str, active_triggers, session
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
            except historical.HistoricalError as e:
                pass

    all_trades = session.query(datamodel.Trade).all()
    trade_df = pd.DataFrame([trade.to_dict() for trade in all_trades])
    return trade_df


class Namespace(object):
    pass


def ui():
    config = configuration.load_config()
    st.sidebar.title("Vigilant Crypto Snatch Evaluation")

    coin = st.sidebar.selectbox("Coin", ["BTC", "ETH"])
    fiat = st.sidebar.selectbox("Fiat", ["EUR", "USD"])

    data = historical.get_hourly_data(
        coin, fiat, config["cryptocompare"]["api_key"]
    )
    data = evaluation.make_dataframe_from_json(data)

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
    hours, drops, factors = evaluation.drop_survey(
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


def main(options):
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(st_cli.main())
