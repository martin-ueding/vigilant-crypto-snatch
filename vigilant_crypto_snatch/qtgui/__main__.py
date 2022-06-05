import sys

from PySide6.QtWidgets import QApplication

from .control.main import MainWindowController
from .ui.main import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = MainWindowController(window)
    window.show()
    retval = app.exec()
    controller.shutdown()
    sys.exit(retval)


if __name__ == "__main__":
    main()
