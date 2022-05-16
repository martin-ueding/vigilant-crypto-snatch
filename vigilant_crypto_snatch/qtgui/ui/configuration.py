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
        layout.addWidget(MarketplacePane())
        layout.addWidget(TriggerPane())
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
        self.poll_interval_edit = QLineEdit("60")
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

        layout.addRow(QLabel("API Key:"), QLineEdit())
        layout.addRow(QLabel("API Secret:"), QLineEdit())
        layout.addRow(QLabel("Prefer fee in base currency:"), QCheckBox())


class MarketplacePane(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Marketplace")
        layout = QVBoxLayout()
        self.setLayout(layout)

        tabs = QTabWidget()
        tab1 = KrakenPane()
        tab2 = QWidget()
        tab3 = QWidget()

        # Add tabs
        tabs.addTab(tab1, "Kraken")
        tabs.addTab(tab2, "Bitstamp")
        tabs.addTab(tab3, "CCXT")

        layout.addWidget(tabs)

        tab1_layout = QVBoxLayout()
        tab1.setLayout(tab1_layout)

        # layout.addWidget(QLabel("Withdrawal"))


class TriggerPane(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Triggers")
        layout = QVBoxLayout()
        self.setLayout(layout)

        list = QListWidget()
        layout.addWidget(list)

        list.addItem("Large Drops")
        list.addItem("Small Drops")
        list.addItem("Regular Buys")

        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Add"))
        button_layout.addWidget(QPushButton("Edit"))
        button_layout.addWidget(QPushButton("Delete"))
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
