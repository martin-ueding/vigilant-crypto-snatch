from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


class LogTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.log_level = QComboBox()
        self.log_level.addItems(["Critical", "Error", "Warning", "Info", "Debug"])
        self.log_level.setCurrentText("Debug")
        layout.addWidget(self.log_level)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.clear = QPushButton("Clear")
        layout.addWidget(self.clear)
        self.setLayout(layout)
