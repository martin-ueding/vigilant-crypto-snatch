import sys

from PySide6.QtCharts import QChart
from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QLineSeries
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication


class TestChartView(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)


class TestChartController:
    def __init__(self, ui: TestChartView):
        self.ui = ui

        chart = QChart()
        series = QLineSeries()
        series.setName("Test Data")
        series.append([QPointF(x, y) for x, y in zip([1, 2, 3, 4], [4, 9, -3, 0])])
        chart.addSeries(series)
        chart.createDefaultAxes()
        self.ui.setChart(chart)


def main():
    app = QApplication(sys.argv)
    window = TestChartView()
    controller = TestChartController(window)
    window.show()
    retval = app.exec()
    sys.exit(retval)


if __name__ == "__main__":
    main()
