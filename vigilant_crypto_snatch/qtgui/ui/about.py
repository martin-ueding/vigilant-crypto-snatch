from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from ... import __version__


class AboutTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("Vigilant Crypto Snatch"))
        layout.addWidget(QLabel(f"Version {__version__}"))
        layout.addWidget(
            QLabel("https://martin-ueding.github.io/vigilant-crypto-snatch/")
        )
