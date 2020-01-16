from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSlot, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget,
        QTableWidget, QTableWidgetItem, QMainWindow, QAction,
        QAbstractScrollArea, QShortcut)

from utils import create_action
from label_creator import LabelCreatorWidget
from label_editor import LabelEditorWidget
from signals import SignalBus

import sys
from functools import partial


class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Tofu Video Labeller")
        self.labels_state = {}
        self.comm = SignalBus.instance()
        self.comm.newLabelSignal.connect(self.bindLabelEvent)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()
        self.editorWidget = LabelEditorWidget()
        self.creatorWidget = LabelCreatorWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)
        openAction = create_action('open.png', '&Open', 'Ctrl+O', 'Open video',
                self.openFile, self)
        exitAction = create_action('exit.png', '&Exit', 'Ctrl+Q', 'Exit',
                self.exitCall, self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        wid = QWidget(self)
        self.setCentralWidget(wid)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        labellingLayout = QVBoxLayout()
        labellingLayout.addWidget(self.creatorWidget)
        labellingLayout.addWidget(self.editorWidget)

        videoAreaLayout = QVBoxLayout()
        videoAreaLayout.addWidget(videoWidget)
        videoAreaLayout.addLayout(controlLayout)
        videoAreaLayout.addWidget(self.errorLabel)

        layout = QHBoxLayout()
        layout.addLayout(videoAreaLayout, 4)
        layout.addLayout(labellingLayout)

        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open video",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def bindLabelEvent(self, keySeq, label):
        bind = QAction(label, self)
        bind.setShortcut(keySeq)
        bind.triggered.connect(partial(self.createMark, label))
        self.labels_state[label] = False
        self.addAction(bind)

    @pyqtSlot()
    def createMark(self, label):
        state = self.mediaPlayer.state()
        if state == QMediaPlayer.PlayingState or state == \
                QMediaPlayer.PausedState:
            self.editorWidget.new_mark(self.mediaPlayer.position()/1000,
                    label, self.labels_state[label])
            self.labels_state[label] = not self.labels_state[label]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(940, 480)
    player.show()
    sys.exit(app.exec_())


