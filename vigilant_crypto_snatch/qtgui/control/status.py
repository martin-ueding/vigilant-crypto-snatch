import datetime
import threading
import time
from typing import List
from typing import Optional

from PyQt6.QtCore import QAbstractTableModel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from vigilant_crypto_snatch.configuration import Configuration
from vigilant_crypto_snatch.datastorage import make_datastore
from vigilant_crypto_snatch.historical import CachingHistoricalSource
from vigilant_crypto_snatch.historical import CryptoCompareHistoricalSource
from vigilant_crypto_snatch.historical import DatabaseHistoricalSource
from vigilant_crypto_snatch.historical import MarketSource
from vigilant_crypto_snatch.marketplace import make_marketplace
from vigilant_crypto_snatch.paths import user_db_path
from vigilant_crypto_snatch.qtgui.ui.status import StatusTab
from vigilant_crypto_snatch.triggers import BuyTrigger
from vigilant_crypto_snatch.triggers import make_triggers
from vigilant_crypto_snatch.triggers import Trigger
from vigilant_crypto_snatch.watchloop import process_trigger


class StatusTabController:
    def __init__(self, ui: StatusTab):
        self.ui = ui
        self.wire_ui()
        self.watch_worker: Optional[WatchWorker] = None

    def wire_ui(self):
        self.ui.refresh.clicked.connect(self.refresh)
        self.ui.watch_triggers.stateChanged.connect(self.watch_triggers_changed)

    def config_updated(self, config: Configuration):
        self.config = config
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

        self.trigger_table_model = TriggerTableModel(
            [
                trigger
                for trigger in self.active_triggers
                if isinstance(trigger, BuyTrigger)
            ]
        )
        self.ui.active_triggers.setModel(self.trigger_table_model)
        self.ui.active_triggers.verticalHeader().setVisible(True)
        # self.ui.active_triggers.verticalHeader().setFixedWidth(100)

        self.active_asset_pairs = {spec.asset_pair for spec in config.triggers}

        self.toggle_worker_thread(self.ui.watch_triggers.isChecked())

        self.refresh()

    def watch_triggers_changed(self):
        self.toggle_worker_thread(self.ui.watch_triggers.isChecked())

    def toggle_worker_thread(self, desired_state: bool) -> None:
        if self.watch_worker is not None:
            self.watch_worker.running = False

        if desired_state:
            self.watch_worker = WatchWorker(
                self.config.polling_interval, self.active_triggers
            )
            self.watch_worker_thread = threading.Thread(target=self.watch_worker.run)
            self.watch_worker_thread.start()
        else:
            self.watch_worker = None

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

    def shutdown(self):
        if self.watch_worker is not None:
            self.watch_worker.running = False


class WatchWorker:
    def __init__(self, sleep: int, triggers: List[Trigger]):
        self.running = True
        self.sleep = sleep
        self.triggers = triggers

    def run(self) -> None:
        while self.running:
            for trigger in self.triggers:
                process_trigger(trigger)
            for i in range(self.sleep):
                time.sleep(2)
                if not self.running:
                    return


class TriggerTableModel(QAbstractTableModel):
    def __init__(self, triggers: List[BuyTrigger]):
        super().__init__()
        self.triggers = triggers
        self.keys = list(sorted(triggers[0].triggered_delegates.keys()))

    def data(self, index, role=None):
        trigger = self.triggers[index.row()]
        key = self.keys[index.column()]
        delegate = trigger.triggered_delegates[key]

        if role == Qt.ItemDataRole.DisplayRole:
            if delegate is None:
                return "—"
            if delegate.is_triggered(datetime.datetime.now()):
                return "Ready"
            else:
                return "Waiting"

        if role == Qt.ItemDataRole.DecorationRole:
            if delegate is None:
                return QColor("#afafaf")
            if delegate.is_triggered(datetime.datetime.now()):
                return QColor("#4daf4a")
            else:
                return QColor("#e41a1c")

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.triggers)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.keys)

    def headerData(self, index, orientation, role=None):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.keys[index]

            if orientation == Qt.Orientation.Vertical:
                return self.triggers[index].get_name()
