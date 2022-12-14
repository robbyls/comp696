import sys

from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QStackedLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog
)

from PyQt5.QtGui import QIntValidator,QFont,QIcon,QRegularExpressionValidator
from PyQt5.QtCore import Qt,QRegularExpression

from matplotlib.backends.backend_qtagg import FigureCanvas

from matplotlib.figure import Figure
import matplotlib as mpl

import os
import glob
from os.path import expanduser

from common import *
from data_picker_window import *
from overxy_view import PopupWindow


class MainForm(QDialog):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("Data Visualization Demo")
        self.setWindowIcon(QIcon('icons/chart_icon.png'))

        # Create a QVBoxLayout instance
        layout = QVBoxLayout()
        
        self.plotLayout = QStackedLayout()
        layout.addLayout(self.plotLayout)

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
                
        self.mainLabel = QLabel("Please load data files first.")
        font = self.mainLabel.font()
        font.setPointSize(30)
        self.mainLabel.setFont(font)
        self.mainLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                
        # layout.addWidget(self.canvas)
        self.plotLayout.addWidget(self.canvas)
        self.plotLayout.addWidget(self.mainLabel)
        
        subLayout = QGridLayout()

        self.loadButton = QPushButton("&Load Data")
        self.loadButton.setFont(QFont("Arial",12))
        self.loadButton.setIcon(QIcon('icons/openfile.png'))
        self.loadButton.clicked.connect(self.event_load_data)
                
        sampleNumberLabel = QLabel('&Current Sample# ')
        sampleNumberLabel.setFont(QFont("Arial",12))
        self.sampleNumberEdit = QLineEdit()
        self.sampleNumberEdit.setFont(QFont("Arial",12))

        self.sampleNumberEdit.setMaxLength(3)
        self.sampleNumberEdit.setText('0')
        self.sampleNumberEdit.setAlignment(Qt.AlignRight)
        self.sampleNumberEdit.setFont(QFont("Aria2",12))
            
        sampleNumberLabel.setBuddy(self.sampleNumberEdit)
        
        subLayout.addWidget(self.loadButton, 0,0)
        subLayout.addWidget(sampleNumberLabel, 0,1)
        subLayout.addWidget(self.sampleNumberEdit, 0,2)

        intervalLabel = QLabel('&Update Internval (milliseconds) #')
        intervalLabel.setFont(QFont("Arial",12))

        self.intervalEdit = QLineEdit()
        intervalValidator = QIntValidator(100, 10000)
        self.intervalEdit.setValidator(intervalValidator)
        self.intervalEdit.setMaxLength(5)
        self.intervalEdit.setText('1000')
        self.intervalEdit.setAlignment(Qt.AlignRight)
        self.intervalEdit.setFont(QFont("Arial",12))
        # self.intervalEdit.setAlignment(Qt.AlignRight)

        intervalLabel.setBuddy(self.intervalEdit)
        
        subLayout.addWidget(intervalLabel, 0,3)
        subLayout.addWidget(self.intervalEdit, 0,4)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        subLayout.addItem(spacerItem, 0,5, 1, 1)

        self.gotoButton = QPushButton("&Goto")
        self.gotoButton.setIcon(QIcon('icons/goto.png'))
        self.backButton = QPushButton("&Back")
        self.backButton.setIcon(QIcon('icons/backward.png'))
        self.forwardBotton = QPushButton("&Forward")
        self.forwardBotton.setIcon(QIcon('icons/forward.png'))
        self.playButton = QPushButton("P&lay")
        self.playButton.setIcon(QIcon('icons/play.png'))
        self.stopButton = QPushButton("Pause")
        self.stopButton.setIcon(QIcon('icons/pause.png'))

        self.gotoButton.setFont(QFont("Arial",12))
        self.backButton.setFont(QFont("Arial",12))
        self.forwardBotton.setFont(QFont("Arial",12))
        self.playButton.setFont(QFont("Arial",12))
        self.stopButton.setFont(QFont("Arial",12))

        self.gotoButton.clicked.connect(self.event_jumpto)
        self.playButton.clicked.connect(self.event_play)
        self.stopButton.clicked.connect(self.event_stop)
        self.backButton.clicked.connect(self.event_back)
        self.forwardBotton.clicked.connect(self.event_forward)

        # by default, they all are disabled
        self.gotoButton.setEnabled(False)
        self.playButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.backButton.setEnabled(False)
        self.forwardBotton.setEnabled(False)

        subLayout.addWidget(self.gotoButton, 0, 6)
        subLayout.addWidget(self.backButton, 0, 7)
        subLayout.addWidget(self.forwardBotton, 0, 8)
        subLayout.addWidget(self.playButton, 0, 9)
        subLayout.addWidget(self.stopButton, 0, 10)
        
        layout.addLayout(subLayout)
        
        # display the label
        self.plotLayout.setCurrentIndex(1)

        # Set the layout on the application's window
        self.setLayout(layout)

        self._timer = None
        self.artist = None
        self.title = None
        self.df_list = None
        self.value_min = 0
        self.value_max  = 0

        self.xAxisCol = None
        self.yAxisCol = None
        self.dataAxisCol = None

        self.xConfig, self.yConfig,self. dataConfig = None, None, None

        self.x_name = None
        self.y_name = None
        self.data_name = None

        self.x_unit = None
        self.y_unit = None
        self.data_unit = None

        self.canvas.mpl_connect('pick_event', self.onpick)


    def event_load_data(self):

        try:
            # read the data files
            df_list = self.load_data()

            # if no data found, simply exit it
            if df_list is None or len(df_list) == 0:
                return

            # use the first data file to config the plotting
            configForm = ConfigurationForm(df_list[0]['data'])
            configForm.exec()

            xConfig, yConfig, dataConfig = configForm.get_data()
            configForm.close()

            if xConfig is None or yConfig is None or dataConfig is None:
                return

            self.df_list = df_list

            validator = QIntValidator(0, len(self.df_list)-1)
            self.sampleNumberEdit.setValidator(validator)

            self.xConfig, self.yConfig,self. dataConfig = xConfig, yConfig, dataConfig
            
            # find min and max values:
            self.dataAxisCol = dataConfig[0]
            self.xAxisCol = xConfig[0]
            self.yAxisCol = yConfig[0]

            self.data_name = dataConfig[1]
            self.x_name =  xConfig[1]
            self.y_name = yConfig[1]
            
            self.data_unit = dataConfig[2]
            self.x_unit = xConfig[2]
            self.y_unit = yConfig[2]
                
            # find min and max value        
            self.value_min = 0
            self.value_max = 0

            for i in self.df_list:
                df_file = i['data']
                t_min = df_file[self.dataAxisCol].min()
                t_max = df_file[self.dataAxisCol].max()
                
                if self.value_min == 0 or t_min < self.value_min:
                    self.value_min = t_min

                if self.value_max == 0 or t_max > self.value_max:
                    self.value_max = t_max

            cmap = mpl.cm.cool
            norm = mpl.colors.Normalize(vmin=self.value_min, vmax=self.value_max)
            mappable = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

            validator = QIntValidator(0, len(self.df_list))
            self.sampleNumberEdit.setValidator(validator)

            # display the first sample
            df = self.df_list[0]['data']

            # self.ax.clear()
            self.canvas.figure.clear()

            self.ax = self.canvas.figure.subplots()

            self.artist = self.ax.scatter(df[self.xAxisCol], df[self.yAxisCol], c=df[self.dataAxisCol], 
                                          s=100, cmap =cmap, vmin=self.value_min, vmax=self.value_max, picker=True, pickradius=5)
            self.title = self.ax.set_title("", fontsize=18)

            self.colorbar = self.fig.colorbar(mappable, ax=self.ax)
            self.colorbar.set_label(f"{self.data_name} ({self.data_unit})")
            
            self.ax.set_xlabel(f"{self.x_name} ({self.x_unit})",fontsize=14)
            self.ax.set_ylabel(f"{self.y_name} ({self.y_unit})",fontsize=14)

            # the initial sample displayed is 0
            self.sampleNumberEdit.setText('0')
            self.event_jumpto()
            
            # display the plot
            self.plotLayout.setCurrentIndex(0)

            self.gotoButton.setEnabled(True)
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.backButton.setEnabled(True)
            self.forwardBotton.setEnabled(True)


        finally:
            pass


    def event_jumpto(self):

        if not self.sampleNumberEdit.hasAcceptableInput():
            self.sampleNumberEdit.setFocus()
            return

        # get the index 
        gotoIndex = int(self.sampleNumberEdit.text())

        df = self.df_list[gotoIndex]['data']
        self.artist.set_array(df[self.dataAxisCol])

        # update the title to show the sample #
        self.ax.title.set_text("{} Data - Sample #: {}".format(self.dataConfig[1],gotoIndex))

        self.artist.figure.canvas.draw()


    def event_play(self):

        if not self.intervalEdit.hasAcceptableInput():
            self.intervalEdit.setFocus()
            return

        if self._timer is not None:
            self._timer.stop()
    
        interval = int(self.intervalEdit.text()) 

        self._timer =  self.canvas.new_timer(interval)
        self._timer.add_callback(self._rolling_update)
        self._timer.start()

    def _rolling_update(self):

        # increase the index
        gotoIndex = int(self.sampleNumberEdit.text())

        if gotoIndex >= len(self.df_list) - 1:
            gotoIndex = 0
        else:
            gotoIndex =  gotoIndex  + 1
        
        self.sampleNumberEdit.setText(str(gotoIndex))

        self.event_jumpto()


    def event_stop(self):

        if self._timer != None:
            self._timer.stop()
            self._timer = None

    def event_back(self):

        # stop timer if existing
        if self._timer != None:
            self._timer.stop()
            self._timer = None
    
        # get the index 
        gotoIndex = int(self.sampleNumberEdit.text())
        if gotoIndex > 0:
            gotoIndex = gotoIndex - 1
        else:
            gotoIndex = len(self.df_list) -1
        
        self.sampleNumberEdit.setText(str(gotoIndex))

        self.event_jumpto()


    def event_forward(self):

        # stop timer if existing
        if self._timer != None:
            self._timer.stop()
            self._timer = None
    
        # get the index 
        gotoIndex = int(self.sampleNumberEdit.text())
        if gotoIndex < len(self.df_list) -1:
            gotoIndex = gotoIndex + 1
        else:
            gotoIndex = 0
        
        self.sampleNumberEdit.setText(str(gotoIndex))
        self.event_jumpto()


    def load_data(self):

        # p = re.compile('x_z_con(\d+)')

        while True:

            selected_dir = QFileDialog.getExistingDirectory(self,"Please select the folder that contains the data files",
            expanduser("~"), QFileDialog.ShowDirsOnly)

            # if user cancels the action
            if not selected_dir:
                return None
     
            csv_files = glob.glob(os.path.join(selected_dir, "*.*"))
            if len(csv_files) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("The selected diretory does not contain any file.")
                msg.exec()

                # prompt the dialog to the user again
                continue
                          
            # read the data and concentration from csv files
            # df_list,value_min,value_max = load_data_from_files(csv_files)
            df_list = load_data_from_files(csv_files)
            
            if len(df_list) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("The selected diretory does not contain the required data files.")
                msg.exec()
                # prompt the dialog to the user again
                continue

            # return df_list, value_min, value_max
            return df_list


    def onpick(self, event):

        xdata = event.mouseevent.xdata  
        ydata = event.mouseevent.ydata  

        self.event_stop()
        popup = PopupWindow(self.xConfig, self.yConfig, self.dataConfig, 
                            self.df_list, round(xdata,6), round(ydata,6), 
                            self.value_min, self.value_max)
        popup.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        popup.exec()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainForm()
    window.resize(1440,1024)
    window.show()
    sys.exit(app.exec_())