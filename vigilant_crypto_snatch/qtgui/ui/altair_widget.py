# Taken from https://stackoverflow.com/a/60215423/653152, MIT licensed via Stack Overflow policy. Adapted to PyQt6.
from io import StringIO
from typing import Optional

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget


class WebEngineView(QWebEngineView):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.page().profile().downloadRequested.connect(self.onDownloadRequested)
        self.windows = []

    @QtCore.Slot(QWebEngineDownloadRequest)
    def onDownloadRequested(self, download: QWebEngineDownloadRequest) -> None:
        if (
            download.state()
            == QWebEngineDownloadRequest.DownloadState.DownloadRequested
        ):
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save as", download.downloadFileName()
            )
            if path:
                download.setDownloadFileName(path)
                download.accept()

    def createWindow(
        self, web_window_type: QWebEnginePage.WebWindowType
    ) -> Optional[QWebEngineView]:
        if web_window_type == QWebEnginePage.WebWindowType.WebBrowserTab:
            window = QtWidgets.QMainWindow(self)
            view = QWebEngineView(window)
            window.resize(640, 480)
            window.setCentralWidget(view)
            window.show()
            return view

    def set_chart(self, chart, **kwargs) -> None:
        output = StringIO()
        chart.save(output, "html", **kwargs)
        self.setHtml(output.getvalue())
