import sys

from PyQt5.QtGui import QIntValidator,QFont,QIcon
from PyQt5.QtWidgets import QWidget,QDialog,QMessageBox
from PyQt5.QtCore import QAbstractTableModel
from common import *
from config_view import *
import pandas as pd
import json 
from pathlib import Path
import os

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

        # set default values anyway
        if len(cols) > 0:
            self.ui.comboBox_Col_X.setCurrentIndex(0)

        if len(cols) > 1:
            self.ui.comboBox_Col_Y.setCurrentIndex(1)

        if len(cols) > 2:
            self.ui.comboBox_Col_Data.setCurrentIndex(2)

        # load the saved configuration
        home_dir = Path.home()
        config_file_path = os.path.join(home_dir, ".data_visualizer.config")
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r') as f:
                saved_config = json.load(f)
                
                l_cols = list(cols)
                
                if 'x' in saved_config:
                    config_x = saved_config['x']
                    self.ui.lineEdit_Name_X.setText(config_x.get('name','X'))
                    self.ui.lineEdit_Unit_X.setText(config_x.get('unit','x unit'))
                    if 'col' in config_x and config_x['col'] in l_cols:
                        idx = l_cols.index(config_x['col'] )
                        self.ui.comboBox_Col_X.setCurrentIndex(idx)
                
                if 'y' in saved_config:
                    config_y = saved_config['y']
                    self.ui.lineEdit_Name_Y.setText(config_y.get('name','Y'))
                    self.ui.lineEdit_Unit_Y.setText(config_y.get('unit','y unit'))
                    if 'col' in config_y and config_y['col'] in l_cols:
                        idx = l_cols.index(config_y['col'] )
                        self.ui.comboBox_Col_Y.setCurrentIndex(idx)
                
                if 'data' in saved_config:
                    config_data = saved_config['data']
                    self.ui.lineEdit_Name_Data.setText(config_data.get('name','Data'))
                    self.ui.lineEdit_Unit_Data.setText(config_data.get('unit','data unit'))
                    if 'col' in config_data and config_data['col'] in l_cols:
                        idx = l_cols.index(config_data['col'] )
                        self.ui.comboBox_Col_Data.setCurrentIndex(idx)
            
        else:
            self.ui.lineEdit_Unit_X.setText("x unit")
            self.ui.lineEdit_Unit_Y.setText("y unit")
            self.ui.lineEdit_Unit_Data.setText("data unit")

            self.ui.lineEdit_Name_X.setText("X")
            self.ui.lineEdit_Name_Y.setText("Y")
            self.ui.lineEdit_Name_Data.setText("Data")
                

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
        
        # save the result to a json file
        config_map={}
        config_map['x']={'name':x_name,'col':xAxisCol,'unit':x_unit}
        config_map['y']={'name':y_name,'col':yAxisCol,'unit':y_unit}
        config_map['data']={'name':data_name,'col':dataAxisCol,'unit':data_unit}
        
        home_dir = Path.home()
        config_file_path = os.path.join(home_dir, ".data_visualizer.config")
        with open(config_file_path, 'w') as f:
            json.dump(config_map, f)
                
        super().accept()

    def reject(self):
        self._output = None, None, None
    
    def get_data(self):
        return self._output
        
