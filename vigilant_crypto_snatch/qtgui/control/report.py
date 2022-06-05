import pandas as pd
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import Qt

from ...reporting import get_user_trades_df
from ...reporting.trades import aggregates_per_asset_pair
from ...reporting.trades import aggregates_per_asset_pair_and_trigger
from ..ui.report import ReportTab


class ReportTabController:
    def __init__(self, ui: ReportTab):
        self.ui = ui
        self.ui.update_report.clicked.connect(self.update_report)

        self.all_trades_table_model = PandasTableModel()
        self.ui.all_trades.setModel(self.all_trades_table_model)

        self.pairs_table_model = PandasTableModel()
        self.ui.pairs_table.setModel(self.pairs_table_model)

        self.pairs_triggers_table_model = PandasTableModel()
        self.ui.pairs_triggers_table.setModel(self.pairs_triggers_table_model)

    def update_report(self):
        trades = get_user_trades_df()
        trades_copy = trades.copy()
        trades_copy["timestamp"] = trades_copy["timestamp"].dt
        self.all_trades_table_model.set_data_frame(trades)

        per_asset_pair = aggregates_per_asset_pair(trades)
        self.pairs_table_model.set_data_frame(per_asset_pair)

        per_asset_pair_and_trigger = aggregates_per_asset_pair_and_trigger(trades)
        self.pairs_triggers_table_model.set_data_frame(per_asset_pair_and_trigger)


class PandasTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.df: pd.DataFrame = pd.DataFrame()

    def set_data_frame(self, df: pd.DataFrame):
        self.beginResetModel()
        self.df = df.astype("object")
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.df)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.df.columns)

    def headerData(self, index, orientation, role=None):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.df.columns[index]

            if orientation == Qt.Orientation.Vertical:
                return self.df.index[index]

    def data(self, index, role=None):
        if role == Qt.ItemDataRole.DisplayRole:
            entry = self.df.iloc[index.row(), index.column()]
            return entry
