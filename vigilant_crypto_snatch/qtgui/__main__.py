import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSlider
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget, QScrollArea, QComboBox, QFormLayout


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 200)
        self.setWindowTitle("Vigilant Crypto Snatch")
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = ConfigurationTab()
        self.tab3 = QWidget()
        self.tabs.resize(400, 400)

        # Add tabs
        self.tabs.addTab(self.tab2, "Configuration")
        self.tabs.addTab(self.tab1, "Status")
        self.tabs.addTab(self.tab3, "About")

        layout.addWidget(self.tabs)


class ConfigurationTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label_general = QLabel("General")
        label_general.setStyleSheet('font-weight: bold;')
        layout.addWidget(label_general)

        general_pane = QWidget()
        general_layout = QVBoxLayout()
        general_pane.setLayout(general_layout)

        general_layout_poll = QHBoxLayout()
        general_layout_poll.addWidget(QLabel("Poll interval (seconds):"))
        general_layout_poll.addWidget(QLineEdit())
        general_layout.addLayout(general_layout_poll)
        layout.addWidget(general_pane)


        heading = QLabel("Marketplace")
        layout.addWidget(heading)
        heading.setStyleSheet('font-weight: bold;')

        layout.addWidget(MarketplacePane())



        heading = QLabel("Telegram")
        layout.addWidget(heading)
        heading.setStyleSheet('font-weight: bold;')
        layout.addWidget(TelegramPane())


        heading = QLabel("Crypto Compare")
        layout.addWidget(heading)
        heading.setStyleSheet('font-weight: bold;')

        crypto_compare_layout = QFormLayout()
        crypto_compare_layout.addRow(QLabel("API key:"), QLineEdit())
        layout.addLayout(crypto_compare_layout)

        layout.addWidget(QPushButton("Save"))
        layout.addWidget(QPushButton("Test drive"))


class MarketplacePane(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)


        tabs = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()

        # Add tabs
        tabs.addTab(tab1, "Kraken")
        tabs.addTab(tab2, "Bitstamp")
        tabs.addTab(tab3, "CCXT")

        layout.addWidget(tabs)

        tab1_layout = QVBoxLayout()
        tab1.setLayout(tab1_layout)

        layout_api_key = QHBoxLayout()
        layout_api_key.addWidget(QLabel("API Key:"))
        layout_api_key.addWidget(QLineEdit())
        tab1_layout.addLayout(layout_api_key)

        layout_api_secret = QHBoxLayout()
        layout_api_secret.addWidget(QLabel("API Secret:"))
        layout_api_secret.addWidget(QLineEdit())
        tab1_layout.addLayout(layout_api_secret)

        layout_fee = QHBoxLayout()
        layout_fee.addWidget(QLabel("Prefer fee in base currency:"))
        layout_fee.addWidget(QCheckBox())
        tab1_layout.addLayout(layout_fee)

        #layout.addWidget(QLabel("Withdrawal"))


class TelegramPane(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        form_layout.addRow(QLabel("Token:"), QLineEdit())
        form_layout.addRow(QLabel("Chat ID:"), QLineEdit())

        log_level_combo_box = QComboBox()
        log_level_combo_box.addItem("info")
        log_level_combo_box.addItem("warning")
        log_level_combo_box.addItem("error")
        log_level_combo_box.addItem("critical")
        form_layout.addRow(QLabel("Log level:"), log_level_combo_box)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
