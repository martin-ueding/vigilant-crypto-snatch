import datetime

import pandas as pd

from vigilant_crypto_snatch.configuration import YamlConfiguration
from vigilant_crypto_snatch.datastorage import Datastore
from vigilant_crypto_snatch.datastorage import make_datastore
from vigilant_crypto_snatch.historical import CryptoCompareHistoricalSource
from vigilant_crypto_snatch.paths import user_db_path


def gather_trades(datastore: Datastore) -> pd.DataFrame:
    trades = datastore.get_all_trades()
    df = pd.DataFrame(trades)
    return df


def add_gains(trades: pd.DataFrame):
    config = YamlConfiguration()
    historical_source = CryptoCompareHistoricalSource(
        config.get_crypto_compare_config()
    )
    unique_currency_pairs = set(zip(trades["coin"], trades["fiat"]))

    now = datetime.datetime.now()
    current_prices = {
        (coin, fiat): historical_source.get_price(now, coin, fiat).last
        for coin, fiat in unique_currency_pairs
    }

    trades["buy_price"] = trades["volume_fiat"] / trades["volume_coin"]
    trades["current_value"] = [
        row["volume_coin"] * current_prices[(row["coin"], row["fiat"])]
        for index, row in trades.iterrows()
    ]
    trades["gains"] = trades["current_value"] - trades["volume_fiat"]


def main() -> None:
    datastore = make_datastore(user_db_path)
    trades = gather_trades(datastore)
    add_gains(trades)

    print(trades)
    trades.to_json("trades.js")
