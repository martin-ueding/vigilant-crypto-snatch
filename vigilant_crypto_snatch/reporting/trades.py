import datetime
from typing import Optional

import pandas as pd

from vigilant_crypto_snatch.configuration import YamlConfiguration
from vigilant_crypto_snatch.core import AssetPair
from vigilant_crypto_snatch.datastorage import Datastore
from vigilant_crypto_snatch.datastorage import make_datastore
from vigilant_crypto_snatch.historical import CryptoCompareHistoricalSource
from vigilant_crypto_snatch.paths import user_db_path


def gather_trades(datastore: Datastore) -> pd.DataFrame:
    trades = datastore.get_all_trades()
    df = pd.DataFrame(trades)
    return df.drop(columns="asset_pair").assign(**df["asset_pair"].apply(pd.Series))


def add_gains(trades: pd.DataFrame):
    config = YamlConfiguration()
    historical_source = CryptoCompareHistoricalSource(
        config.get_crypto_compare_config()
    )
    unique_currency_pairs = set(
        AssetPair(coin, fiat) for coin, fiat in zip(trades["coin"], trades["fiat"])
    )

    now = datetime.datetime.now()
    current_prices = {
        (asset_pair.coin, asset_pair.fiat): historical_source.get_price(
            now, asset_pair
        ).last
        for asset_pair in unique_currency_pairs
    }

    trades["buy_price"] = trades["volume_fiat"] / trades["volume_coin"]
    trades["current_value"] = [
        row["volume_coin"] * current_prices[(row["coin"], row["fiat"])]
        for index, row in trades.iterrows()
    ]
    trades["gains"] = trades["current_value"] - trades["volume_fiat"]
    trades["day"] = [
        datetime.datetime.combine(ts.date(), datetime.time.min)
        for ts in trades["timestamp"]
    ]
    trades["month"] = [
        datetime.datetime(ts.year, ts.month, 1) for ts in trades["timestamp"]
    ]
    trades["year"] = [ts.year for ts in trades["timestamp"]]
    trades["gains_cumsum"] = trades["gains"].cumsum()
    trades["volume_fiat_cumsum"] = trades.groupby("coin")["volume_fiat"].cumsum()
    trades["volume_coin_cumsum"] = trades.groupby("coin")["volume_coin"].cumsum()
    trades["volume_coin_cumsum_then_value"] = (
        trades["volume_coin_cumsum"] * trades["buy_price"]
    )


def get_user_trades_df() -> Optional[pd.DataFrame]:
    if user_db_path.exists():
        datastore = make_datastore(user_db_path)
        trades = gather_trades(datastore)
        add_gains(trades)
        return trades
    else:
        return None


def main() -> None:
    trades = get_user_trades_df()
    assert trades is not None
    print(trades)
    trades.to_json("trades.js")
