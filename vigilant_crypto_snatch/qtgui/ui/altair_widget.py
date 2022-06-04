# Taken from https://stackoverflow.com/a/60215423/653152, MIT licensed via Stack Overflow policy. Adapted to PyQt6.
from io import StringIO

from PyQt6 import QtCore
from PyQt6 import QtWebEngineWidgets
from PyQt6 import QtWidgets
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWebEngineCore import QWebEnginePage


class WebEngineView(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page().profile().downloadRequested.connect(self.onDownloadRequested)
        self.windows = []

    @QtCore.pyqtSlot(QWebEngineDownloadRequest)
    def onDownloadRequested(self, download):
        if (
            download.state()
            == QWebEngineDownloadRequest.DownloadState.DownloadRequested
        ):
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, self.tr("Save as"), download.path()
            )
            if path:
                download.setPath(path)
                download.accept()

    def createWindow(self, type_):
        if type_ == QWebEnginePage.WebWindowType.WebBrowserTab:
            window = QtWidgets.QMainWindow(self)
            view = QtWebEngineWidgets.QWebEngineView(window)
            window.resize(640, 480)
            window.setCentralWidget(view)
            window.show()
            return view

    def updateChart(self, chart, **kwargs):
        output = StringIO()
        chart.save(output, "html", **kwargs)
        self.setHtml(output.getvalue())
