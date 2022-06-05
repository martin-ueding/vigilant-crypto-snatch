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

from ..control.charts import make_qt_chart_from_data_frame
from ..control.charts import test_df


class TestChartView(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)


def main():
    app = QApplication(sys.argv)
    window = TestChartView()
    chart = make_qt_chart_from_data_frame(test_df)
    window.setChart(chart)
    window.show()
    retval = app.exec()
    sys.exit(retval)


if __name__ == "__main__":
    main()
