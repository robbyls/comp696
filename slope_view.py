import sys

from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog,
    QScrollBar
)

from PyQt5.QtGui import QIntValidator,QFont,QIcon
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qtagg import (
    FigureCanvas)

from matplotlib.figure import Figure

import matplotlib as mpl

from matplotlib import artist

import numpy as np
import os
import glob
import re
import pandas as pd
from os.path import expanduser
import math
import matplotlib.ticker as ticker
from common import FloatDial, load_data_from_files


class Window(QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("Data Change Slope Demo")
        self.setWindowIcon(QIcon('chart_icon.png'))


        # Create a QVBoxLayout instance
        layout = QVBoxLayout()

        # self.fig = Figure(figsize=(20, 16))
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()

        subLayout = QGridLayout()

        self.loadButton = QPushButton("Load Data")
        self.loadButton.setFont(QFont("Arial",14))
        self.loadButton.clicked.connect(self.event_load_data)
        subLayout.addWidget(self.loadButton, 0,0)


        # self.qBarX = QScrollBar(Qt.Horizontal)
        # self.qBarZ = QScrollBar(Qt.Horizontal)
        # self.qBarX.minimumSize = 100
        # self.qBarZ.minimumSize = 100

        self.dialX = FloatDial(0, 100, 100)
        self.dialZ = FloatDial(0, 100, 100)
        # self.dialX.enabled = False
        # self.dialZ.enabled = False

        self.dialX.floatValueChanged.connect(self.updateFloatXValue)
        self.dialZ.floatValueChanged.connect(self.updateFloatZValue)


        self.qBarXLabel = QLabel('X Value')
        self.qBarXLabel.setFont(QFont("Arial",14))

        self.qBarXValue = QLabel('0')
        self.qBarXValue.setFont(QFont("Arial",14))

        # self.qBarXLabel.setBuddy(self.qBarX)

        self.qBarZLabel = QLabel('Depth Value')
        self.qBarZLabel.setFont(QFont("Arial",14))
        # self.qBarZLabel.setBuddy(self.qBarZ)

        self.qBarZValue = QLabel('0')
        self.qBarZValue.setFont(QFont("Arial",14))

        # subLayout.addWidget(self.qBarXLabel, 1,0)
        # subLayout.addWidget(self.qBarXValue, 1,1)
        # # subLayout.addWidget(self.qBarX, 1,2)
        # subLayout.addWidget(self.dialX, 1,2)

        # subLayout.addWidget(self.qBarZLabel, 2,0)
        # subLayout.addWidget(self.qBarZValue, 2,1)
        # # subLayout.addWidget(self.qBarZ, 2,2)
        # subLayout.addWidget(self.dialZ, 2,2)

        # self.qBarX.valueChanged.connect(self.sliderval)
        # self.qBarZ.valueChanged.connect(self.sliderval)

        subLayout.addWidget(self.qBarXLabel, 1,0)
        subLayout.addWidget(self.qBarXValue, 1,1)

        subLayout.addWidget(self.qBarZLabel, 2,0)
        subLayout.addWidget(self.qBarZValue, 2,1)


    
        subLayout.addWidget(self.dialX, 1,1,2,1)
        subLayout.addWidget(self.dialZ, 1,2,2,1)
            
        layout.addLayout(subLayout)

        self.setLayout(layout)

        self.df_list = None
        self.concentration_min = 0
        self.concentration_max  = 0

        self.z_min = 0 
        self.z_max = 0 

        self.x_min = 0 
        self.x_max = 0 

        self.current_x = 0
        self.current_z = 0

        self.dataLoaded = False

    def event_load_data(self):

        try:
 
            # read the data
            self.df_list, self.concentration_min, self.concentration_max = self.load_data()

            # if no data found, simply exit it
            if self.df_list is None or self.concentration_min is None or self.concentration_max is None:
                return

            # use the first dataframe to get range of x and y
            df = self.df_list[0]['data']
            self.x_min = df['x'].min()
            self.x_max = df['x'].max()

            self.z_min = df['z'].min()
            self.z_max = df['z'].max()

            # self.qBarX.setMaximum(math.ceil(self.x_max * 10))
            # self.qBarX.setMinimum(math.floor(self.x_min  * 10))

            # self.qBarZ.setMaximum(math.ceil(self.z_max * 10))
            # self.qBarZ.setMinimum(math.floor(self.z_min * 10))

            self.dialX.setValueRange(self.x_min,self.x_max)
            self.dialZ.setValueRange(self.z_min,self.z_max)

            x_found = self.x_min
            z_found = self.z_min

            self.plot_xz(x_found, z_found)

            self.current_x = x_found
            self.current_z = z_found

        finally:
            pass


    def updateFloatXValue(self, value):
        if self.dataLoaded:
            self.current_x = value
            self.updateCommon()

    def updateFloatZValue(self, value):
        if self.dataLoaded:
            self.current_z = value
            self.updateCommon()


    def updateCommon(self):

        x = round(self.current_x,2)
        z = round(self.current_z,2)

        self.qBarXValue.setText(str(x))
        self.qBarZValue.setText(str(z))

        df = self.df_list[0]['data']

        a_x = df['x'].unique()
        a_z = df['z'].unique()

        x_found = a_x[0]
        z_found = a_z[0]
        for i in range(1, len(a_x)):
            if a_x[i -1] <= x and a_x[i] >= x:
                if x - a_x[i -1] < a_x[i] - x:
                    x_found = a_x[i -1]
                    break

        for i in range(1, len(a_z)):
            if a_z[i -1] <= z and a_z[i] >= z:
                if z - a_z[i -1] < a_z[i] - z:
                    z_found = a_z[i -1]
                    break

        self.plot_xz(x_found, z_found)

    
    def sliderval(self):

        x = self.qBarX.value() / 10
        z = self.qBarZ.value() / 10
        
        self.qBarXValue.setText(str(x))
        self.qBarZValue.setText(str(z))

        df = self.df_list[0]['data']

        a_x = df['x'].unique()
        a_z = df['z'].unique()

        x_found = a_x[0]
        z_found = a_z[0]
        for i in range(1, len(a_x)):
            if a_x[i -1] <= x and a_x[i] >= x:
                if x - a_x[i -1] < a_x[i] - x:
                    x_found = a_x[i -1]
                    break

        for i in range(1, len(a_z)):
            if a_z[i -1] <= z and a_z[i] >= z:
                if z - a_z[i -1] < a_z[i] - z:
                    z_found = a_z[i -1]
                    break

        self.plot_xz(x_found, z_found)

    def plot_xz(self, x, z):

        keys = []
        concentrations = []

        for dict in self.df_list:
            time = int(dict['key'])
            df = dict['data']
            df_sample = df[ (df['x'] == x ) & (df['z'] == z )]
            if df_sample.shape[0] > 0:
                keys.append(time)
                concentrations.append(df_sample['concentration'].iloc[0])


        self.ax.clear()
        self.ax.plot(keys, concentrations)
        self.ax.set_title("Concentration Over Time", fontsize=20)

        self.ax.set_xlabel('Point of Time',fontsize=14)
        self.ax.set_ylabel('Concentration',fontsize=14)

        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
        self.ax.xaxis.set_minor_locator(ticker.MultipleLocator(5))
        
        self.fig.canvas.draw()
    


    def load_data(self):


        while True:

            selected_dir = QFileDialog.getExistingDirectory(self,"Please select the folder that contains the data files",
            expanduser("~"), QFileDialog.ShowDirsOnly)

            # if user cancels the action
            if not selected_dir:
                return None, None, None
     
            csv_files = glob.glob(os.path.join(selected_dir, "*.*"))
            if len(csv_files) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("The selected diretory does not contain any file.")

                # prompt the dialog to the user again
                continue
                          
            # read the data and concentration from csv files
            df_list,concentration_min,concentration_max = load_data_from_files(csv_files)
            
            if len(df_list) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("The selected diretory does not contain the required data files.")

                # prompt the dialog to the user again
                continue

            self.dataLoaded = True
            return df_list, concentration_min, concentration_max


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.resize(1440,1024)
    window.show()
    sys.exit(app.exec_())