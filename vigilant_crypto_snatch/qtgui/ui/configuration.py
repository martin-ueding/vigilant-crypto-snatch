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
from PyQt6.QtWidgets import QToolBox
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


class ConfigurationTab(QWidget):
    def __init__(self):
        super().__init__()

        self.general_panel = GeneralPanel()
        self.crypto_compare_panel = CryptoComparePanel()
        self.trigger_pane = TriggerPane()
        self.telegram_panel = TelegramPane()
        self.kraken_pane = KrakenPane()
        self.bitstamp_pane = BitstampPane()

        self.save_button = QPushButton("Save")
        self.test_drive_button = QPushButton("Test drive")

        toolbox = QToolBox()
        toolbox.addItem(self.general_panel, "General")
        toolbox.addItem(self.crypto_compare_panel, "Crypto Compare")
        toolbox.addItem(self.kraken_pane, "Kraken Marketplace")
        toolbox.addItem(self.bitstamp_pane, "Bitstamp Marketplace")
        toolbox.addItem(self.trigger_pane, "Triggers")
        toolbox.addItem(self.telegram_panel, "Telegram")

        layout = QVBoxLayout()
        layout.addWidget(toolbox)
        layout.addWidget(self.test_drive_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)


class GeneralPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.poll_interval_edit = QLineEdit("30")
        self.marketplace_edit = QComboBox()
        self.marketplace_edit.addItem("kraken")
        self.marketplace_edit.addItem("bitstamp")

        layout = QFormLayout()
        self.setLayout(layout)
        layout.addRow(QLabel("Poll interval (seconds):"), self.poll_interval_edit)
        layout.addRow(QLabel("Active marketplace:"), self.marketplace_edit)


class CryptoComparePanel(QWidget):
    def __init__(self):
        super().__init__()
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

        self.kraken_withdrawal_pane = KrakenWithdrawalPane()
        layout.addRow(self.kraken_withdrawal_pane)


class KrakenWithdrawalPane(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Withdrawal")
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


class KrakenWithdrawalEditWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Kraken Withdrawal")

        layout = QFormLayout()
        self.setLayout(layout)

        self.coin = QLineEdit()
        layout.addRow(QLabel("Coin:"), self.coin)
        self.target = QLineEdit()
        layout.addRow(QLabel("Target:"), self.target)
        self.fee_limit = QLineEdit()
        layout.addRow(QLabel("Fee limit (percent):"), self.fee_limit)

        button_layout = QHBoxLayout()
        self.save = QPushButton("Save")
        self.cancel = QPushButton("Cancel")
        button_layout.addWidget(self.save)
        button_layout.addWidget(self.cancel)
        layout.addRow(button_layout)


class BitstampPane(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)

        self.key = QLineEdit()
        self.secret = QLineEdit()
        self.username = QLineEdit()

        layout.addRow(QLabel("API Key:"), self.key)
        layout.addRow(QLabel("API Secret:"), self.secret)
        layout.addRow(QLabel("Username:"), self.username)


class TriggerPane(QWidget):
    def __init__(self):
        super().__init__()
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


class TelegramPane(QWidget):
    def __init__(self):
        super().__init__()
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
