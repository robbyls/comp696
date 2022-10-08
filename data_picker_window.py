import sys

from PyQt5.QtGui import QIntValidator,QFont,QIcon
from PyQt5.QtWidgets import QWidget,QDialog,QMessageBox
from PyQt5.QtCore import QAbstractTableModel
from common import *
from config_view import *
import pandas as pd

class ConfigurationForm(QDialog):

    def __init__(self,df_sample:pd.DataFrame):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.model = PandasModel(df_sample)
        self.ui.tableData.setModel(self.model)

        cols = df_sample.columns
        self.tugs = ExclusiveComboGroup(self)
        self.tugs.addCombo(self.ui.comboBox_Col_X)
        self.tugs.addCombo(self.ui.comboBox_Col_Y)
        self.tugs.addCombo(self.ui.comboBox_Col_Data)

        self.ui.comboBox_Col_X.addItems(cols)
        self.ui.comboBox_Col_Y.addItems(cols)
        self.ui.comboBox_Col_Data.addItems(cols)

    def accept(self):

        xAxisCol = self.ui.comboBox_Col_X.currentText()
        yAxisCol = self.ui.comboBox_Col_Y.currentText()
        dataAxisCol = self.ui.comboBox_Col_Data.currentText()

        if not xAxisCol or not yAxisCol or not dataAxisCol:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Horizontal (X) Axis, Horizontal (Y) Axis, and Data (measurement) must be specified.")
            msg.exec()
            return

        elif xAxisCol == yAxisCol or  xAxisCol == dataAxisCol or yAxisCol == dataAxisCol:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Horizontal (X) Axis, Horizontal (Y) Axis, and Data (measurement) must be mapped to different fields.")
            msg.exec()
            return

        x_name = self.ui.lineEdit_Name_X.text()
        y_name = self.ui.lineEdit_Name_Y.text()
        data_name = self.ui.lineEdit_Name_Data.text()

        if not x_name or not y_name or not data_name:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Display names for Horizontal (X) Axis, Horizontal (Y) Axis, and Data (measurement) must be provided.")
            msg.exec()
            return

        x_unit = self.ui.lineEdit_Unit_X.text()
        y_unit = self.ui.lineEdit_Unit_Y.text()
        data_unit = self.ui.lineEdit_Unit_Data.text()

        if not x_unit or not y_unit or not data_unit:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Unit for Horizontal (X) Axis, Horizontal (Y) Axis, and Data (measurement) must be provided.")
            msg.exec()
            return

        self._output = [xAxisCol,x_name,x_unit], [yAxisCol,y_name,y_unit],[dataAxisCol,data_name,data_unit]
        super().accept()

    # def reject(self):
    #     pass
    
    def get_data(self):
        return self._output
        
