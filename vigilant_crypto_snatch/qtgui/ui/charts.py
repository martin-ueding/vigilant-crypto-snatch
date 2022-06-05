import datetime
import sys

from PySide6.QtCharts import QChart
from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QDateTimeAxis
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


class TestChartView(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)


class TestChartController:
    def __init__(self, ui: TestChartView):
        self.ui = ui

        chart = QChart()

        xs = [
            datetime.datetime(2022, 1, 1, 4, 5),
            datetime.datetime(2022, 1, 4, 4, 5),
            datetime.datetime(2022, 2, 5, 0, 50),
        ]
        xs_int = [x.timestamp() for x in xs]

        series_1 = QLineSeries()
        series_1.setName("Test Data")
        series_1.append([QPointF(x, y) for x, y in zip(xs_int, [4, 9, -3])])
        chart.addSeries(series_1)

        series_2 = QLineSeries()
        series_2.setName("Test Data")
        series_2.append([QPointF(x, y) for x, y in zip(xs_int, [5, 3, -1])])
        chart.addSeries(series_2)

        axis_x = QDateTimeAxis()
        axis_x.setTickCount(5)
        axis_x.setFormat("MM/dd HH:mm")
        axis_x.setTitleText("Date")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series_1.attachAxis(axis_x)
        series_2.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTickCount(10)
        axis_y.setTitleText("Fiat")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series_1.attachAxis(axis_y)
        series_2.attachAxis(axis_y)

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
