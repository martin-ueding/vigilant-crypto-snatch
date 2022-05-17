from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QFormLayout
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QListWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


class ConfigurationTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.general_panel = GeneralPanel()
        layout.addWidget(self.general_panel)
        self.crypto_compare_panel = CryptoComparePanel()
        layout.addWidget(self.crypto_compare_panel)
        self.marketplace_pane = MarketplacePane()
        layout.addWidget(self.marketplace_pane)
        self.trigger_pane = TriggerPane()
        layout.addWidget(self.trigger_pane)
        self.telegram_panel = TelegramPane()
        layout.addWidget(self.telegram_panel)

        self.save_button = QPushButton("Save")

        layout.addWidget(self.save_button)
        layout.addWidget(QPushButton("Test drive"))


class GeneralPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("General")
        layout = QFormLayout()
        self.setLayout(layout)
        self.poll_interval_edit = QLineEdit("30")
        layout.addRow(QLabel("Poll interval (seconds):"), self.poll_interval_edit)


class CryptoComparePanel(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Crypto Compare")
        layout = QFormLayout()
        self.setLayout(layout)
        self.api_key_line_edit = QLineEdit()
        layout.addRow(QLabel("API key:"), self.api_key_line_edit)


class KrakenPane(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)

        self.api_key = QLineEdit()
        self.api_secret = QLineEdit()
        self.prefer_fee = QCheckBox()

        layout.addRow(QLabel("API Key:"), self.api_key)
        layout.addRow(QLabel("API Secret:"), self.api_secret)
        layout.addRow(QLabel("Prefer fee in base currency:"), self.prefer_fee)


class MarketplacePane(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Marketplace")
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.kraken_pane = KrakenPane()

        tabs = QTabWidget()
        tab2 = QWidget()
        tab3 = QWidget()

        # Add tabs
        tabs.addTab(self.kraken_pane, "Kraken")
        tabs.addTab(tab2, "Bitstamp")
        tabs.addTab(tab3, "CCXT")

        layout.addWidget(tabs)

        # layout.addWidget(QLabel("Withdrawal"))


class TriggerPane(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Triggers")
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.list = QListWidget()
        self.add = QPushButton("Add")
        self.edit = QPushButton("Edit")
        self.delete = QPushButton("Delete")

        layout.addWidget(self.list)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add)
        button_layout.addWidget(self.edit)
        button_layout.addWidget(self.delete)
        layout.addLayout(button_layout)


class TelegramPane(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Telegram")
        layout = QFormLayout()
        self.setLayout(layout)

        self.token_line_edit = QLineEdit()
        self.chat_id_line_edit = QLineEdit()
        self.log_level_combo_box = QComboBox()

        layout.addRow(QLabel("Token:"), self.token_line_edit)
        layout.addRow(QLabel("Chat ID:"), self.chat_id_line_edit)

        self.log_level_combo_box.addItem("info")
        self.log_level_combo_box.addItem("warning")
        self.log_level_combo_box.addItem("error")
        self.log_level_combo_box.addItem("critical")
        layout.addRow(QLabel("Log level:"), self.log_level_combo_box)


class TriggerEditWindow(QWidget):
    def __init__(self):
        super().__init__()
        # self.resize(500, 200)
        self.setWindowTitle("Edit Trigger")

        layout = QFormLayout()
        self.setLayout(layout)

        self.name = QLineEdit()
        layout.addRow(QLabel("Name:"), self.name)
        self.coin = QLineEdit()
        layout.addRow(QLabel("Coin:"), self.coin)
        self.fiat = QLineEdit()
        layout.addRow(QLabel("Fiat:"), self.fiat)
        self.cooldown_minutes = QLineEdit()
        layout.addRow(QLabel("Cooldown (minutes):"), self.cooldown_minutes)
        self.volume_fiat = QLineEdit()
        self.volume_fiat_type = QComboBox()
        self.volume_fiat_type.addItem("absolute")
        self.volume_fiat_type.addItem("percent")
        volume_fiat_layout = QHBoxLayout()
        volume_fiat_layout.addWidget(self.volume_fiat)
        volume_fiat_layout.addWidget(self.volume_fiat_type)
        layout.addRow(QLabel("Volume fiat:"), volume_fiat_layout)

        self.delay_minutes = QLineEdit()
        layout.addRow(QLabel("Delay (minutes):"), self.delay_minutes)
        self.fear_and_greed_index_below = QLineEdit()
        layout.addRow(QLabel("Fear & Greed below:"), self.fear_and_greed_index_below)

        button_layout = QHBoxLayout()
        self.save = QPushButton("Save")
        self.cancel = QPushButton("Cancel")
        button_layout.addWidget(self.save)
        button_layout.addWidget(self.cancel)
        layout.addRow(button_layout)
