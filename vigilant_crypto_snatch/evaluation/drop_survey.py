from typing import Tuple

import numpy as np
import pandas as pd


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
