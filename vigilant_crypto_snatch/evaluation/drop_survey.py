from typing import Tuple

import altair as alt
import numpy as np
import pandas as pd

from vigilant_crypto_snatch.core import AssetPair


def drop_survey(
    data: pd.DataFrame, hours, drops
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    factor = np.zeros(hours.shape + drops.shape)
    for i, hour in enumerate(hours):
        for j, drop in enumerate(drops):
            factor[i, j] = compute_gains(data, hour, drop)[2]
    return hours, drops, factor.T


def compute_gains(
    df: pd.DataFrame, hours: int, drop: float
) -> Tuple[float, float, float]:
    close_shift = df["close"].shift(hours)
    ratio = df["close"] / close_shift
    btc = 0.0
    eur = 0.0
    last = -hours
    for i in range(len(df)):
        if ratio[i] < (1 - drop) and last + hours <= i:
            last = i
            btc += 1.0 / df["close"][i]
            eur += 1.0
    return btc, eur, btc / eur if eur > 0 else 0.0


def make_survey_chart(
    data: pd.DataFrame,
    range_delay: Tuple[int, int],
    range_percentage: Tuple[float, float],
    asset_pair: AssetPair,
) -> alt.Chart:
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
                "factor:Q",
                title=f"{asset_pair.coin}/{asset_pair.fiat}",
                scale=alt.Scale(scheme="turbo"),
            ),
        )
    )
    return survey_chart
