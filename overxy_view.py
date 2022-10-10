
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QDialog
)

from PyQt5.QtGui import QFont,QIcon

from PyQt5.QtCore import Qt


from matplotlib.backends.backend_qtagg import (
    FigureCanvas)

from matplotlib.figure import Figure

import matplotlib as mpl

from matplotlib import artist

import numpy as np
import pandas as pd
from os.path import expanduser
import matplotlib.ticker as ticker
from common import FloatDial, take_closest


class PopupWindow(QDialog):

    def __init__(self, xConfig, yConfig, dataConfig, df_list, xValue, yValue):

        super().__init__()
        self.setWindowTitle("Data Change Visualization")
        self.setWindowIcon(QIcon('chart_icon.png'))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint,False) 
        
        self.xConfig, self.yConfig, self.dataConfig = xConfig, yConfig, dataConfig

        self.df_list = df_list
        self.xValue = xValue
        self.yValue = yValue

        # Create a QVBoxLayout instance
        layout = QVBoxLayout()

        # self.fig = Figure(figsize=(20, 16))
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        self.ax = self.canvas.figure.subplots()

        subLayout = QGridLayout()

        self.qBarXLabel = QLabel(f"{xConfig[1]} ({xConfig[2]})")
        self.qBarXLabel.setFont(QFont("Arial",14))
        self.qBarXLabel.setAlignment(Qt.AlignHCenter)

        self.qBarXValue = QLabel(f"{xValue}")
        self.qBarXValue.setFont(QFont("Arial",14))
        self.qBarXValue.setAlignment(Qt.AlignHCenter)

        x_min, x_max = self.find_x_min_max()
        y_min, y_max = self.find_y_min_max()

        self.dialX = FloatDial(x_min, x_max)

        subLayout.addWidget(self.qBarXLabel, 1,0)
        subLayout.addWidget(self.qBarXValue, 2,0)
        subLayout.addWidget(self.dialX, 3,0)

        self.qBarYLabel = QLabel(f"{yConfig[1]} ({yConfig[2]})")
        self.qBarYLabel.setFont(QFont("Arial",14))
        self.qBarYLabel.setAlignment(Qt.AlignHCenter)
        
        self.qBarYValue = QLabel(f"{yValue}")
        self.qBarYValue.setFont(QFont("Arial",14))
        self.qBarYValue.setAlignment(Qt.AlignHCenter)

        self.dialY = FloatDial(y_min, y_max)
        
        subLayout.addWidget(self.qBarYLabel, 1,1)
        subLayout.addWidget(self.qBarYValue, 2,1)
        subLayout.addWidget(self.dialY, 3,1)

        layout.addLayout(subLayout)
        self.setLayout(layout)

        self.dialX.floatValueChanged.connect(self.updateFloatXValue)
        self.dialY.floatValueChanged.connect(self.updateFloatYValue)

        self.dialX.setFloatValue(self.xValue)
        self.dialY.setFloatValue(self.yValue)
       
         # translate to the existing x and y values in the data

        self.plot_sample_over_position(self.xValue, self.yValue)

        # self.value_min = 0
        # self.value_max = 0

        # self.z_min = 0 
        # self.z_max = 0 

        # self.x_min = 0 
        # self.x_max = 0 

        # self.current_x = 0
        # self.current_z = 0

        # self.dataLoaded = False
   

    def updateFloatXValue(self, value):
        self.xValue = round(value,6)
        self.qBarXValue.setText(f"{self.xValue}")
        self.plot_sample_over_position(self.xValue, self.yValue)
            

    def updateFloatYValue(self, value):
        self.yValue = round(value,6)
        self.qBarYValue.setText(f"{self.yValue}")
        self.plot_sample_over_position(self.xValue, self.yValue)


    def find_min_max_base(self, col_name):

        min_values = []
        max_values = []

        for df_item in self.df_list:
            df_sample = df_item['data']
            min_values.append(df_sample[col_name].min())
            max_values.append(df_sample[col_name].max())
        
        return min(min_values), max(max_values)

    def find_x_min_max(self):
        col_name = self.xConfig[0]
        return self.find_min_max_base(col_name)

    def find_y_min_max(self):
        col_name = self.yConfig[0]
        return self.find_min_max_base(col_name)

    def locate_xy_values(self, df, x, y):

        a_x = df[self.xConfig[0]].unique()
        a_y = df[self.yConfig[0]].unique()

        x_found = take_closest(a_x, x)
        y_found = take_closest(a_y, y)

        return x_found, y_found

    
    # def sliderval(self):

    #     x = self.qBarX.value() / 10
    #     z = self.qBarZ.value() / 10
        
    #     self.qBarXValue.setText(str(x))
    #     self.qBarYValue.setText(str(z))

    #     df = self.df_list[0]['data']

    #     a_x = df['x'].unique()
    #     a_z = df['z'].unique()

    #     x_found = a_x[0]
    #     z_found = a_z[0]
    #     for i in range(1, len(a_x)):
    #         if a_x[i -1] <= x and a_x[i] >= x:
    #             if x - a_x[i -1] < a_x[i] - x:
    #                 x_found = a_x[i -1]
    #                 break

    #     for i in range(1, len(a_z)):
    #         if a_z[i -1] <= z and a_z[i] >= z:
    #             if z - a_z[i -1] < a_z[i] - z:
    #                 z_found = a_z[i -1]
    #                 break

    #     self.plot_xz(x_found, z_found)

    def plot_sample_over_position(self, x_input, y_input):

        keys = []
        data = []

        for dict in self.df_list:
            sample_index = int(dict['key'])
            df = dict['data']

            x, y = self.locate_xy_values(df, x_input, y_input)

            df_sample = df[ (df[self.xConfig[0]] == x ) & (df[self.yConfig[0]] == y )]
            if df_sample.shape[0] > 0:
                keys.append(sample_index)
                data.append(df_sample[self.dataConfig[0]].iloc[0])

        self.ax.clear()
        self.ax.plot(keys, data)
        self.ax.set_title(f"{self.dataConfig[1]} Data", fontsize=18)
        self.ax.set_xlabel('Sample #',fontsize=10)

        self.ax.set_ylabel(f"{self.dataConfig[1]} ({self.dataConfig[2]})",fontsize=10)

        # self.ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
        # self.ax.xaxis.set_minor_locator(ticker.MultipleLocator(5))
        
        self.fig.canvas.draw()
    

