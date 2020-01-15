from PyQt5.QtWidgets import (QLabel, QDialog, QFormLayout, QGroupBox,
        QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget, QLineEdit,
        QTableWidget, QTableWidgetItem, QAction, QAbstractScrollArea, QFrame,
        QDialogButtonBox, QKeySequenceEdit)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QIntValidator

from signals import SignalBus


class LabelCreatorWidget(QWidget):

    def __init__(self):
        super(LabelCreatorWidget, self).__init__()
        self.title = 'Label Creator'
        self.comm = SignalBus.instance()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        self.createTable()

        self.addLabelButton = QPushButton()
        self.addLabelButton.setEnabled(True)
        self.addLabelButton.setIcon(
                self.style().standardIcon(QStyle.SP_ArrowForward))
        self.addLabelButton.clicked.connect(self.addLabel)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.addLabelButton)
        self.setLayout(self.layout)
        self.show()

    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setSizeAdjustPolicy(
                QAbstractScrollArea.AdjustToContents)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.setHorizontalHeaderLabels(['id', 'label', 'shortcut'])
        self.tableWidget.resizeColumnsToContents()

    @pyqtSlot()
    def addLabel(self):
        newLabelDialog = NewLabelDialog()
        if newLabelDialog.exec_():
            label = newLabelDialog.label.text()
            keySeq = newLabelDialog.shortcut.keySequence()
            index = self.tableWidget.rowCount() - 1
            self.tableWidget.setItem(index, 0, QTableWidgetItem(
                newLabelDialog.lid.text()))
            self.tableWidget.setItem(index, 1, QTableWidgetItem(label))
            self.tableWidget.setItem(index, 2, QTableWidgetItem(
                keySeq.toString()))
            self.comm.newLabelSignal.emit(keySeq, label)
            self.tableWidget.insertRow(index+1)


class NewLabelDialog(QDialog):

    def __init__(self):
        super(NewLabelDialog, self).__init__()
        self.title = 'Add New Label'
        self.initUI()

    def initUI(self):
        self.createFormGroupBox()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | \
                QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        dialogLayout = QVBoxLayout()
        dialogLayout.addWidget(self.formGroupBox)
        dialogLayout.addWidget(buttonBox)
        self.setLayout(dialogLayout)
        self.setWindowTitle(self.title)

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox('Label form')
        self.lid = QLineEdit()
        self.lid.setValidator(QIntValidator())
        self.label = QLineEdit()
        self.shortcut = QKeySequenceEdit()
        layout = QFormLayout()
        layout.addRow(QLabel('id:'), self.lid)
        layout.addRow(QLabel('label:'), self.label)
        layout.addRow(QLabel('shortcut:'), self.shortcut)
        self.formGroupBox.setLayout(layout)


