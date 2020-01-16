from PyQt5.QtWidgets import (QLabel, QDialog, QFormLayout, QGroupBox,
        QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget, QLineEdit,
        QTableWidget, QTableWidgetItem, QAction, QAbstractScrollArea, QFrame,
        QDialogButtonBox)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QColor


class LabelEditorWidget(QWidget):

    def __init__(self):
        super(LabelEditorWidget, self).__init__()
        self.title = 'Label Editor'
        self.default_color = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        self.createTable()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)


    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setSizeAdjustPolicy(
                QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setHorizontalHeaderLabels(['label', 'begin', 'end'])
        self.tableWidget.resizeColumnsToContents()

    def new_mark(self, time, label, mode):
        if not mode:
            start_or_stop = 1
            index = self.tableWidget.rowCount()-1
            self.tableWidget.setItem(index, 0, QTableWidgetItem(str(label)))
            self.tableWidget.setItem(index, 2, QTableWidgetItem('...'))
            if not self.default_color:
                self.default_color = \
                        self.tableWidget.item(index, 0).background()
            self.tableWidget.insertRow(index+1)
        else:
            start_or_stop = 2
            matches = self.tableWidget.findItems(label, Qt.MatchExactly)
            index = matches[-1].row()
        self.tableWidget.setItem(index, start_or_stop,
                QTableWidgetItem(str(time)))
        self.set_row_color(index, mode)

    def set_row_color(self, index, mode):
        t = self.tableWidget
        if not mode:
            self.__row_colors(index, QColor(64, 249, 107))
        else:
            self.__row_colors(index, self.default_color)

    def __row_colors(self, i, color):
        for ii in range(self.tableWidget.columnCount()):
            self.tableWidget.item(i, ii).setBackground(color)


