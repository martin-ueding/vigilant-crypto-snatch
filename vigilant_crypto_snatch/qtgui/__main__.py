import sys
from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QFormLayout
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QListWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QSlider
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


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
        self.configuration_tab = ConfigurationTab()
        self.tab3 = QWidget()
        self.tabs.resize(400, 400)

        # Add tabs
        self.tabs.addTab(self.configuration_tab, "Configuration")
        self.tabs.addTab(self.tab1, "Status")
        self.tabs.addTab(self.tab3, "About")

        layout.addWidget(self.tabs)


class MainWindowController:
    def __init__(self, main_window: MainWindow):
        self.main_window = main_window
        self.configuration_tab_controller = ConfigurationTabController(
            self.main_window.configuration_tab
        )


class ConfigurationTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.general_panel = GeneralPanel()

        layout.addWidget(self.general_panel)
        layout.addWidget(CryptoComparePanel())
        layout.addWidget(MarketplacePane())
        layout.addWidget(TriggerPane())
        layout.addWidget(TelegramPane())

        self.save_button = QPushButton("Save")

        layout.addWidget(self.save_button)
        layout.addWidget(QPushButton("Test drive"))


class ConfigurationTabController:
    def __init__(self, widget: ConfigurationTab):
        self.widget = widget
        self.general_panel_controller = GeneralPanelController(
            self.widget.general_panel
        )

        self.widget.save_button.clicked.connect(self.save)

    def save(self) -> None:
        config_dict = {}
        config_dict.update(self.general_panel_controller.get_config())
        print(config_dict)


class GeneralPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("General")
        layout = QFormLayout()
        self.setLayout(layout)
        self.poll_interval_edit = QLineEdit()
        layout.addRow(QLabel("Poll interval (seconds):"), self.poll_interval_edit)


class GeneralPanelController:
    def __init__(self, general_panel: GeneralPanel):
        self.general_panel = general_panel

    def get_config(self) -> Dict:
        return {"sleep": self.general_panel.poll_interval_edit.text()}


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
    controller = MainWindowController(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
