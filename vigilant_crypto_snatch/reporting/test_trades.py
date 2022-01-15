import datetime

from ..core import AssetPair
from ..core import Trade
from ..datastorage import ListDatastore
from .trades import add_gains
from .trades import gather_trades


def test_add_gains() -> None:
    datastore = ListDatastore()
    datastore.add_trade(
        Trade(
            timestamp=datetime.datetime(2022, 1, 15, 9, 24),
            trigger_name="test-trigger",
            volume_coin=10.0,
            volume_fiat=10.0,
            asset_pair=AssetPair("BTC", "EUR"),
        )
    )
    trades = gather_trades(datastore)
    add_gains(trades)
