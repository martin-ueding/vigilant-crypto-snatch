import datetime
import threading

from vigilant_crypto_snatch.configuration import Configuration
from vigilant_crypto_snatch.configuration import get_used_currencies
from vigilant_crypto_snatch.datastorage import make_datastore
from vigilant_crypto_snatch.historical import CachingHistoricalSource
from vigilant_crypto_snatch.historical import CryptoCompareHistoricalSource
from vigilant_crypto_snatch.historical import DatabaseHistoricalSource
from vigilant_crypto_snatch.historical import MarketSource
from vigilant_crypto_snatch.marketplace import make_marketplace
from vigilant_crypto_snatch.marketplace import Marketplace
from vigilant_crypto_snatch.paths import user_db_path
from vigilant_crypto_snatch.qtgui.ui.status import StatusTab
from vigilant_crypto_snatch.triggers import make_triggers


class StatusTabController:
    def __init__(self, ui: StatusTab):
        self.ui = ui
        self.wire_ui()

    def wire_ui(self):
        self.ui.refresh.clicked.connect(self.refresh)

    def config_updated(self, config: Configuration):
        self.market = make_marketplace(
            config.marketplace, config.bitstamp, config.kraken, config.ccxt
        )
        datastore = make_datastore(user_db_path)

        database_source = DatabaseHistoricalSource(
            datastore, datetime.timedelta(minutes=5)
        )
        crypto_compare_source = CryptoCompareHistoricalSource(config.crypto_compare)
        market_source = MarketSource(self.market)
        caching_source = CachingHistoricalSource(
            database_source, [market_source, crypto_compare_source], datastore
        )
        self.active_triggers = make_triggers(
            config.triggers, datastore, caching_source, self.market
        )

        self.active_asset_pairs = [spec.asset_pair for spec in config.triggers]

        self.refresh()

    def refresh(self) -> None:
        thread = threading.Thread(target=self._update_balance_worker)
        thread.start()

    def _update_balance_worker(self):
        self.ui.marketplace_name.setText(self.market.get_name())
        self.ui.balance.setText(
            "\n".join(
                f"{coin}: {balance}"
                for coin, balance in sorted(self.market.get_balance().items())
            )
        )

        prices = {
            asset_pair: self.market.get_spot_price(asset_pair, datetime.datetime.now())
            for asset_pair in self.active_asset_pairs
        }
        self.ui.prices.setText(
            "\n".join(
                f"{asset_pair.coin}: {price.last} {asset_pair.fiat}"
                for asset_pair, price in sorted(prices.items())
            )
        )

        self.ui.last_refresh.setText(datetime.datetime.now().isoformat())
