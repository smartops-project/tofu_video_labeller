from PyQt5.QtWidgets import (QLabel, QDialog, QFormLayout, QGroupBox,
        QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget, QLineEdit,
        QTableWidget, QTableWidgetItem, QAction, QAbstractScrollArea, QFrame,
        QDialogButtonBox)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon


class LabelEditorWidget(QWidget):

    def __init__(self):
        super(LabelEditorWidget, self).__init__()
        self.title = 'Label Editor'
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
        self.tableWidget.setHorizontalHeaderLabels(['time', 'label', 'type'])
        self.tableWidget.resizeColumnsToContents()


