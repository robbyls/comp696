import numpy as np
import re
import pandas as pd
from PyQt5.QtWidgets import QDial

from PyQt5.QtCore import QAbstractTableModel,pyqtSignal,Qt,QObject

# def load_data_from_files(csv_files):

#     # p = re.compile('x_z_con(\d+)')

#     df_list = []
#     value_max = 0
#     value_min = 0
#     sample_number = 1

#     # loop over the list of csv files
#     for f in csv_files:
        
#         # m = p.search(f)
#         # if m:
#         # con = m.group(1)

#         # read the csv file
#         df = pd.read_csv(f,sep=' ',names=['col1','col2','col3'])

#         # update concentration max and min value
#         t_min = df['col3'].min()
#         t_max = df['col3'].max()

#         if value_min == 0 or t_min < value_min:
#             value_min = t_min

#         if value_max == 0 or t_max > value_max:
#             value_max = t_max

#         df_list.append({'key':sample_number, 'data':df})
#         sample_number += 1

#     return df_list, value_min, value_max

def load_data_from_files(csv_files):

    df_list = []
    sample_number = 1

    # loop over the list of csv files
    for f in csv_files:
   
        # read the csv file
        df = pd.read_csv(f,sep=' ',names=['col1','col2','col3'])

        df_list.append({'key':sample_number, 'data':df})
        sample_number += 1

    return df_list



class FloatDial(QDial):

    floatValueChanged = pyqtSignal(float)

    def __init__(self, minimum, maximum, stepCount=1001):
        super(FloatDial, self).__init__()
        self.minimumFloat = minimum
        self.maximumFloat = maximum
        self.floatRange = maximum - minimum
        self.stepCount = stepCount
        self.setMaximum(stepCount - 1)
        self.valueChanged.connect(self.computeFloat)

    def setValueRange(self, minimum, maximum):
        self.minimumFloat = minimum
        self.maximumFloat = maximum
        self.floatRange = maximum - minimum

    def computeFloat(self, value):
        ratio = float(value) / self.maximum()
        self.floatValueChanged.emit(self.floatRange * ratio + self.minimumFloat)

    def setFloatValue(self, value):
        # compute the "step", based on the stepCount then use the same concept
        # as in the StepDial.setFloatValue function
        step = (self.maximumFloat - self.minimumFloat) / self.stepCount
        index = (value - self.minimumFloat) // step
        self.setValue(int(round(index)))



# class DataFrameModel(QtCore.QAbstractTableModel):

#     DtypeRole = QtCore.Qt.UserRole + 1000
#     ValueRole = QtCore.Qt.UserRole + 1001

#     def __init__(self, df=pd.DataFrame(), parent=None):
#         super(DataFrameModel, self).__init__(parent)
#         self._dataframe = df

#     def setDataFrame(self, dataframe):
#         self.beginResetModel()
#         self._dataframe = dataframe.copy()
#         self.endResetModel()

#     def dataFrame(self):
#         return self._dataframe

#     dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

#     @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
#     def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
#         if role == QtCore.Qt.DisplayRole:
#             if orientation == QtCore.Qt.Horizontal:
#                 return self._dataframe.columns[section]
#             else:
#                 return str(self._dataframe.index[section])
#         return QtCore.QVariant()

#     def rowCount(self, parent=QtCore.QModelIndex()):
#         if parent.isValid():
#             return 0
#         return len(self._dataframe.index)

#     def columnCount(self, parent=QtCore.QModelIndex()):
#         if parent.isValid():
#             return 0
#         return self._dataframe.columns.size

#     def data(self, index, role=QtCore.Qt.DisplayRole):
#         if not index.isValid() or not (0 <= index.row() < self.rowCount() \
#             and 0 <= index.column() < self.columnCount()):
#             return QtCore.QVariant()
#         row = self._dataframe.index[index.row()]
#         col = self._dataframe.columns[index.column()]
#         dt = self._dataframe[col].dtype

#         val = self._dataframe.iloc[row][col]
#         if role == QtCore.Qt.DisplayRole:
#             return str(val)
#         elif role == DataFrameModel.ValueRole:
#             return val
#         if role == DataFrameModel.DtypeRole:
#             return dt
#         return QtCore.QVariant()

#     def roleNames(self):
#         roles = {
#             QtCore.Qt.DisplayRole: b'display',
#             DataFrameModel.DtypeRole: b'dtype',
#             DataFrameModel.ValueRole: b'value'
#         }
#         return roles


class PandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class ExclusiveComboGroup(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._combos = []
        self._role = Qt.UserRole + 500

    def addCombo(self, combo):
        combo.activated.connect(lambda: self.handleActivated(combo))
        self._combos.append(combo)

    def handleActivated(self, target):
        index = target.currentIndex()
        groupid = id(target)
        for combo in self._combos:
            if combo is target:
                continue
            previous = combo.findData(groupid, self._role)
            if previous >= 0:
                combo.view().setRowHidden(previous, False)
                combo.setItemData(previous, None, self._role)
            if index > 0:
                combo.setItemData(index, groupid, self._role)
                combo.view().setRowHidden(index, True)
