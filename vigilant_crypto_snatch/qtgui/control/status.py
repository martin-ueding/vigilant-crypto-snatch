import datetime
import threading
import time
from typing import Any
from typing import Optional

from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

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
from vigilant_crypto_snatch.watchloop import process_trigger


class StatusTabController:
    def __init__(self, ui: StatusTab):
        self.ui = ui
        self.config: Optional[Configuration] = None
        self.last_check: Optional[datetime.datetime] = None

        self.wire_ui()
        self.watch_worker = WatchWorker(self)
        self.watch_worker_thread = threading.Thread(target=self.watch_worker.run)
        self.watch_worker_thread.start()

    def wire_ui(self):
        self.spot_price_model = DumbTableModel()
        self.spot_price_model.columns_names = ["Coin", "Value", "Fiat"]
        self.ui.prices.setModel(self.spot_price_model)

        self.balances_model = DumbTableModel()
        self.balances_model.columns_names = ["Asset", "Value"]
        self.ui.balance.setModel(self.balances_model)

        self.trigger_table_model = DumbTableModel()
        self.ui.active_triggers.setModel(self.trigger_table_model)
        self.ui.active_triggers.verticalHeader().setVisible(True)

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

        # self.ui.active_triggers.verticalHeader().setFixedWidth(100)

        self.active_asset_pairs = {spec.asset_pair for spec in config.triggers}

    def _update_balance_worker(self):
        if self.ui.watch_triggers.isChecked():
            for trigger in self.active_triggers:
                process_trigger(trigger)

        self.balances_model.set_cells(
            [
                [coin, balance]
                for coin, balance in sorted(self.market.get_balance().items())
            ]
        )

        prices = {
            asset_pair: self.market.get_spot_price(asset_pair, datetime.datetime.now())
            for asset_pair in self.active_asset_pairs
        }
        self.spot_price_model.set_cells(
            [
                [asset_pair.coin, price.last, asset_pair.fiat]
                for asset_pair, price in sorted(prices.items())
            ]
        )

        buy_triggers = [
            trigger
            for trigger in self.active_triggers
            if isinstance(trigger, BuyTrigger)
        ]
        predicate_names = list(sorted(buy_triggers[0].triggered_delegates.keys()))
        trigger_cells = []
        trigger_colors = []
        trigger_names = []

        for trigger in buy_triggers:
            cells = []
            colors = []
            for predicate_name in predicate_names:
                predicate = trigger.triggered_delegates[predicate_name]
                if predicate is None:
                    cells.append("—")
                    colors.append("#afafaf")
                else:
                    if predicate.is_triggered(datetime.datetime.now()):
                        cells.append("Ready")
                        colors.append("#4daf4a")
                    else:
                        cells.append("Waiting")
                        colors.append("#e41a1c")
            trigger_cells.append(cells)
            trigger_colors.append(colors)
            trigger_names.append(trigger.get_name())

        self.trigger_table_model.columns_names = predicate_names
        self.trigger_table_model.row_names = trigger_names
        self.trigger_table_model.set_cells(trigger_cells, trigger_colors)

    def shutdown(self):
        if self.watch_worker is not None:
            self.watch_worker.running = False

    def ui_changed(self):
        if self.config is not None:
            if (
                self.last_check is None
                or self.last_check
                < datetime.datetime.now() - datetime.timedelta(seconds=30)
            ):
                self.last_check = datetime.datetime.now()
                self._update_balance_worker()


class WatchWorker:
    def __init__(
        self,
        status_tab_controller: StatusTabController,
    ):
        self.status_tab_controller = status_tab_controller
        self.running = True

    def run(self) -> None:
        while self.running:
            self.status_tab_controller.ui_changed()
            time.sleep(2)
            if not self.running:
                return


class DumbTableModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self.columns_names: list[str] = []
        self.row_names: list[str] = []
        self.cells: list[list[Any]] = []
        self.colors: list[list[str]] = []

    def set_cells(
        self, cells: list[list[Any]], colors: Optional[list[list[str]]] = None
    ):
        self.beginResetModel()
        self.cells = cells
        if colors is not None:
            self.colors = colors
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.cells)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.columns_names)

    def headerData(self, index, orientation, role=None):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if self.columns_names:
                    return self.columns_names[index]
                else:
                    return ""

            if orientation == Qt.Orientation.Vertical:
                if self.row_names:
                    return self.row_names[index]
                else:
                    return ""

    def data(self, index, role=None):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.cells[index.row()][index.column()]

        if role == Qt.ItemDataRole.DecorationRole and self.colors:
            return QColor(self.colors[index.row()][index.column()])
