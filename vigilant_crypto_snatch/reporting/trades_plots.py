import altair as alt
import pandas as pd


def plot_gains_from_individual_trades(trades: pd.DataFrame) -> alt.Chart:
    chart = (
        alt.Chart(
            trades,
            title="Gains from individual trades",
        )
        .mark_bar()
        .encode(
            alt.X("timestamp", title="Time"),
            alt.Y("gains", title="Gains"),
            alt.Color("trigger_name", title="Trigger name"),
            [
                alt.Tooltip("timestamp", title="Time"),
                alt.Tooltip("trigger_name", title="Trigger name"),
                alt.Tooltip("coin", title="Coin"),
                alt.Tooltip("fiat", title="Fiat"),
                alt.Tooltip("buy_price", title="Buy price"),
            ],
        )
        .interactive()
    )
    return chart


def plot_gains_per_day(trades: pd.DataFrame) -> alt.Chart:
    chart = (
        alt.Chart(
            trades.groupby("day").sum().reset_index(),
            title="Gains per day",
        )
        .mark_bar()
        .encode(
            alt.X("day"),
            alt.Y("gains"),
        )
        .interactive()
    )
    return chart


def plot_gains_per_month(trades: pd.DataFrame) -> alt.Chart:
    chart = (
        alt.Chart(
            trades.groupby("month").sum().reset_index(),
            title="Gains per month",
        )
        .mark_bar()
        .encode(
            alt.X("month", title="Month"),
            alt.Y("gains", title="Gains / Fiat"),
            [
                alt.Tooltip("month", title="Month"),
                alt.Tooltip("gains", title="Gains / Fiat"),
            ],
        )
        .interactive()
    )
    return chart


def plot_gains_per_year(trades: pd.DataFrame) -> alt.Chart:
    (
        alt.Chart(
            trades.groupby("year").sum().reset_index(),
            title="Gains per year",
        )
        .mark_bar()
        .encode(
            alt.X("year"),
            alt.Y("gains"),
        )
        .interactive()
    )


def plot_fiat_spent_per_month(trades: pd.DataFrame) -> alt.Chart:
    chart = (
        alt.Chart(
            trades.groupby(["month", "fiat"]).sum().reset_index(),
            title="Spent fiat per month",
        )
        .mark_bar()
        .encode(
            alt.X("month", title="Month"),
            alt.Y("volume_fiat", title="Fiat volume"),
            alt.Column("fiat"),
            [
                alt.Tooltip("month", title="Month"),
                alt.Tooltip("volume_fiat", title="Fiat volume"),
            ],
        )
        .interactive()
    )
    return chart


def plot_value_and_investment(trades: pd.DataFrame) -> alt.Chart:
    chart = (
        alt.Chart(
            trades,
            title="Value and investment",
        )
        .mark_area(interpolate="step-after", opacity=0.5)
        .encode(
            alt.X("timestamp", title="Time"),
            alt.Y("volume_coin_cumsum_then_value", title="Coin value"),
            alt.Color("coin", title="Coin"),
        )
        + alt.Chart(trades)
        .mark_line(interpolate="step-after")
        .encode(
            alt.X("timestamp", title="Time"),
            alt.Y("volume_fiat_cumsum", title="Fiat spent"),
            alt.Color("coin", title="Coin"),
        )
        .interactive()
    ).interactive()
    return chart
