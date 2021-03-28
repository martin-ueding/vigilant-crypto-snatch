import datetime
import logging
import os
import json
import typing
import subprocess
import platform
import sys

import requests
import pandas as pd
import matplotlib.pyplot as pl
import tqdm
import numpy as np
import sqlalchemy.orm
import scipy.interpolate

from . import rendering
from . import datamodel
from . import configuration
from . import historical
from . import triggers
from . import marketplace

logger = logging.getLogger("vigilant_crypto_snatch")


def make_interpolator(data: pd.DataFrame):
    x = data["time"]
    y = data["close"]
    return scipy.interpolate.interp1d(x, y)


class InterpolatingSource(historical.HistoricalSource):
    def __init__(self, data: pd.DataFrame):
        self.interpolator = make_interpolator(data)
        self.start = np.min(data['datetime'])
        self.end = np.max(data['datetime'])

    def get_price(
        self, then: datetime.datetime, coin: str, fiat: str
    ) -> datamodel.Price:
        try:
            last = self.interpolator(then.timestamp())
        except ValueError as e:
            raise historical.HistoricalError(e)

        return datamodel.Price(
            timestamp=then,
            last=last,
            coin=coin,
            fiat=fiat,
        )


def open_file_with_default_application(path: str) -> None:
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.run(["open", path])
    elif platform.system() == "Linux":
        subprocess.run(["xdg-open", path])
    else:
        raise RuntimeError(f"Unsupported platform {platform.system()}")


class SimulationMarketplace(marketplace.Marketplace):
    def __init__(self, source: historical.HistoricalSource):
        super().__init__()
        self.source = source

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        pass

    def get_name(self) -> str:
        return "Simulation"

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> datamodel.Price:
        return self.source.get_price(now, coin, fiat)


def simulate_triggers(data: pd.DataFrame, coin: str, fiat: str) -> pd.DataFrame:
    session = datamodel.open_memory_db_session()
    source = InterpolatingSource(data)
    config = configuration.load_config()
    market = SimulationMarketplace(source)
    active_triggers = triggers.make_buy_triggers(config, session, source, market)

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


def make_report(coin: str, fiat: str, api_key: str):
    data = get_hourly_data(coin, fiat, api_key)
    data = make_dataframe_from_json(data)
    trade_df = simulate_triggers(data, coin, fiat)
    print(trade_df)

    data.to_json('prices.js')
    trade_df.to_json('trades.js')



    sys.exit(0)

    plot_close(data)
    plot_drop_survey(data)
    renderer = rendering.Renderer()
    renderer.render_md("evaluation.md")
    open_file_with_default_application(os.path.join(rendering.report_dir))


def get_hourly_data(coin: str, fiat: str, api_key: str) -> typing.List[dict]:
    cache_file = f"~/.cache/vigilant-crypto-snatch/hourly_{coin}_{fiat}.js"
    cache_file = os.path.expanduser(cache_file)
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    if os.path.exists(cache_file):
        logger.info("Cached historic data exists.")
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
        if mtime > datetime.datetime.now() - datetime.timedelta(days=1):
            logger.info("Cached historic data is recent. Loading that.")
            with open(cache_file) as f:
                return json.load(f)

    logger.info("Requesting historic data from Crypto Compare.")
    timestamp = int(datetime.datetime.now().timestamp())
    url = (
        f"https://min-api.cryptocompare.com/data/histohour"
        f"?api_key={api_key}"
        f"&fsym={coin}&tsym={fiat}"
        f"&limit=2000&toTs={timestamp}"
    )
    r = requests.get(url)
    data = r.json()["Data"]
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data


def json_to_database(
    data: typing.List[dict], coin: str, fiat: str, session: sqlalchemy.orm.session
) -> None:
    logger.info(f"Writing {len(data)} prices to the DB …")
    for elem in data:
        price = datamodel.Price(
            timestamp=datetime.datetime.fromtimestamp(elem["time"]),
            last=elem["close"],
            coin=coin,
            fiat=fiat,
        )
        session.add(price)
    session.commit()


def make_dataframe_from_json(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data)
    df["datetime"] = list(map(datetime.datetime.fromtimestamp, df["time"]))
    return df


def plot_close(data: pd.DataFrame) -> None:
    fig, ax = pl.subplots()
    ax.plot(data["datetime"], data["close"])
    ax.set_title("Close Price")
    ax.set_xlabel("Time")
    ax.set_ylabel("Close")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(True)
    save_figure(fig, "close")


def save_figure(fig: pl.Figure, name: str) -> None:
    os.makedirs(rendering.report_dir, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(rendering.report_dir, f"{name}.pdf"))
    fig.savefig(os.path.join(rendering.report_dir, f"{name}.png"), dpi=300)
    fig.savefig(os.path.join(rendering.report_dir, f"{name}.svg"))


def plot_drop_hist(data: pd.DataFrame) -> None:
    pl.clf()
    pl.hist(data["close"].shift() / data["close"], bins="sturges")
    pl.show()

    pl.clf()
    pl.hist(data["close"].shift(2) / data["close"], bins="sturges")
    pl.show()

    pl.clf()
    pl.hist(data["close"].shift(3) / data["close"], bins="sturges")
    pl.show()

    pl.clf()
    pl.hist(data["close"].shift(24) / data["close"], bins="sturges")
    pl.show()

    pl.clf()
    pl.hist(data["close"].shift(7 * 24) / data["close"], bins="sturges")
    pl.show()


def plot_drop_survey(data):
    hours, drops, factor = drop_survey(data)
    fig, ax = pl.subplots()
    img = ax.pcolormesh(hours, drops * 100, factor, cmap="turbo", shading="nearest")
    pl.colorbar(img, ax=ax)
    ax.set_title("BTC / EUR")
    ax.set_xlabel("Delay / h")
    ax.set_ylabel("Drop / %")
    save_figure(fig, "survey")


def drop_survey(data: pd.DataFrame) -> typing.Tuple[np.array, np.array, np.array]:
    hours = np.arange(1, 49)
    drops = np.linspace(0.0, 0.30, 30)
    factor = np.zeros(hours.shape + drops.shape)
    for i, hour in enumerate(tqdm.tqdm(hours)):
        for j, drop in enumerate(drops):
            factor[i, j] = compute_gains(data, hour, drop)[2]
    return hours, drops, factor.T


def compute_gains(
    df: pd.DataFrame, hours: int, drop: float
) -> typing.Tuple[float, float, float]:
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


def compute_dca(df: pd.DataFrame, hours: int) -> typing.Tuple[float, float, float]:
    btc = 0.0
    eur = 0.0
    last = -hours
    for i in range(len(df)):
        if last + hours <= i:
            last = i
            btc += 1.0 / df["close"][i]
            eur += 1.0
    return btc, eur, btc / eur if eur > 0 else 0.0
