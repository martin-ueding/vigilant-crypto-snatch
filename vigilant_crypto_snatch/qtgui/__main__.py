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
from PyQt6.QtWidgets import QWidget, QScrollArea, QComboBox, QFormLayout, QGroupBox


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

        layout.addWidget(GeneralPanel())
        layout.addWidget(CryptoComparePanel())
        layout.addWidget(MarketplacePane())
        layout.addWidget(TriggerPane())
        layout.addWidget(TelegramPane())

        layout.addWidget(QPushButton("Save"))
        layout.addWidget(QPushButton("Test drive"))

class GeneralPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("General")
        layout = QFormLayout()
        self.setLayout(layout)
        layout.addRow(QLabel("Poll interval (seconds):"), QLineEdit())


class CryptoComparePanel(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Crypto Compare")
        layout = QFormLayout()
        self.setLayout(layout)
        layout.addRow(QLabel("API key:"), QLineEdit())


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

        #layout.addWidget(QLabel("Withdrawal"))


class TriggerPane(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Trigger")
        layout = QFormLayout()
        self.setLayout(layout)

class TelegramPane(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Telegram")
        layout = QFormLayout()
        self.setLayout(layout)

        layout.addRow(QLabel("Token:"), QLineEdit())
        layout.addRow(QLabel("Chat ID:"), QLineEdit())

        log_level_combo_box = QComboBox()
        log_level_combo_box.addItem("info")
        log_level_combo_box.addItem("warning")
        log_level_combo_box.addItem("error")
        log_level_combo_box.addItem("critical")
        layout.addRow(QLabel("Log level:"), log_level_combo_box)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
