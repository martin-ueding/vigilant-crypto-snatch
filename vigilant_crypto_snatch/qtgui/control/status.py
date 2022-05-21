import threading

from vigilant_crypto_snatch.configuration import Configuration
from vigilant_crypto_snatch.datastorage import make_datastore
from vigilant_crypto_snatch.marketplace import make_marketplace
from vigilant_crypto_snatch.marketplace import Marketplace
from vigilant_crypto_snatch.paths import user_db_path
from vigilant_crypto_snatch.qtgui.ui.status import StatusTab


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
        self.datastore = make_datastore(user_db_path)
        self.refresh()

    def refresh(self) -> None:
        thread = threading.Thread(target=self._update_balance_worker)
        thread.start()

    def _update_balance_worker(self):
        self.ui.marketplace_name.setText(self.market.get_name())
        self.ui.balance.setText(str(self.market.get_balance()))
