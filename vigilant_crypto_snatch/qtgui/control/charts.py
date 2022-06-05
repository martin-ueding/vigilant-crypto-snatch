import datetime

import pandas as pd
from PySide6.QtCharts import QChart
from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QDateTimeAxis
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt


test_df = pd.DataFrame(
    {
        "datetime": [
            datetime.datetime(2022, 1, 1, 4, 5),
            datetime.datetime(2022, 1, 4, 4, 5),
            datetime.datetime(2022, 2, 5, 0, 50),
            datetime.datetime(2022, 1, 4, 4, 5),
        ],
        "value": [1, 2, 3, 4],
        "label": ["Foo", "Foo", "Bar", "Bar"],
    }
)


def make_qt_chart_from_data_frame(df: pd.DataFrame, y_label: str) -> QChart:
    chart = QChart()

    axis_x = QDateTimeAxis()
    axis_y = QValueAxis()

    if "label" in df.columns:
        for index, group in df.groupby("label"):
            points = [
                QPointF(row["datetime"].timestamp(), row["value"])
                for i, row in group.iterrows()
            ]
            series = QLineSeries()
            series.setName(index)
            series.append(points)
            chart.addSeries(series)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
    else:
        points = [
            QPointF(row["datetime"].timestamp(), row["value"])
            for i, row in df.iterrows()
        ]
        series = QLineSeries()
        series.append(points)
        chart.addSeries(series)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

    axis_x.setTickCount(6)
    axis_x.setFormat("MM/dd HH:mm")
    axis_x.setTitleText("Date")

    axis_y.setTickCount(10)
    axis_y.setTitleText(y_label)

    axis_x.setMin(min(df["datetime"]))
    axis_x.setMax(max(df["datetime"]))
    axis_y.setMin(min(df["value"]))
    axis_y.setMax(max(df["value"]))

    chart.addAxis(axis_x, Qt.AlignBottom)
    chart.addAxis(axis_y, Qt.AlignLeft)

    return chart
