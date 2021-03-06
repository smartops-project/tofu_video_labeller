from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSlot, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget,
        QTableWidget, QTableWidgetItem, QMainWindow, QAction,
        QAbstractScrollArea, QShortcut)

from utils import create_action, format_time
from label_creator import LabelCreatorWidget
from label_editor import LabelEditorWidget
from label_slider import LabelSliderWidget
from signals import SignalBus

import sys
import os
import csv
from functools import partial


class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("tofu")
        self.setWindowIcon(QIcon('src/static/img/tofu.png'))
        self.comm = SignalBus.instance()
        self.comm.newLabelSignal.connect(self.bindLabelEvent)
        self.comm.delLabelSignal.connect(self.unbindLabelEvent)
        self.rate = 1
        self.initUI()
        self.set_default_shortcuts()
        self.shortcuts = {}

    def initUI(self):
        videoWidget = self.create_player()
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)
        self.create_menu_bar()
        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.set_layout(videoWidget, wid)
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def create_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()
        self.editorWidget = LabelEditorWidget()
        self.creatorWidget = LabelCreatorWidget()
        self.create_control()

        self.playButton.clicked.connect(self.play)
        self.speedUpButton.clicked.connect(self.speed)
        self.slowDownButton.clicked.connect(self.slow)
        self.adv3Button.clicked.connect(partial(self.advance, 3))
        self.goBack3Button.clicked.connect(partial(self.back, 3))
        self.advanceButton.clicked.connect(partial(self.advance, 10))
        self.goBackButton.clicked.connect(partial(self.back, 10))
        self.positionSlider.sliderMoved.connect(self.setPosition)

        return videoWidget

    def set_default_shortcuts(self):
        self.playButton.setShortcut(QKeySequence(Qt.Key_Space))
        self.speedUpButton.setShortcut(QKeySequence(Qt.Key_Up))
        self.slowDownButton.setShortcut(QKeySequence(Qt.Key_Down))
        self.advanceButton.setShortcut(QKeySequence(Qt.Key_Right))
        self.goBackButton.setShortcut(QKeySequence(Qt.Key_Left))

    def create_control(self):
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.speedUpButton = QPushButton()
        self.speedUpButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.speedUpButton.setEnabled(False)

        self.slowDownButton = QPushButton()
        self.slowDownButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.slowDownButton.setEnabled(False)

        self.adv3Button = QPushButton()
        self.adv3Button.setIcon(
                self.style().standardIcon(QStyle.SP_ArrowRight))
        self.adv3Button.setEnabled(False)

        self.advanceButton = QPushButton()
        self.advanceButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.advanceButton.setEnabled(False)

        self.goBack3Button = QPushButton()
        self.goBack3Button.setIcon(
                self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.goBack3Button.setEnabled(False)

        self.goBackButton = QPushButton()
        self.goBackButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.goBackButton.setEnabled(False)

        self.timeBox = QLabel(format_time(0), self)
        self.timeBox.setAlignment(Qt.AlignCenter)
        self.rateBox = QLabel(str(self.rate)+'x', self)
        self.rateBox.setAlignment(Qt.AlignCenter)

        self.labelSlider = LabelSliderWidget()

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)

    def create_menu_bar(self):
        openAction = create_action('open.png', '&Open', 'Ctrl+O', 'Open video',
                self.openFile, self)
        csvAction = create_action('save.png', '&Export', 'Ctrl+S',
                'Export to csv', self.exportCsv, self)
        exitAction = create_action('exit.png', '&Exit', 'Ctrl+Q', 'Exit',
                self.exitCall, self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(csvAction)
        fileMenu.addAction(exitAction)

    def set_layout(self, videoWidget, wid):
        labellingLayout = QVBoxLayout()
        labellingLayout.addWidget(self.creatorWidget)
        labellingLayout.addWidget(self.editorWidget)

        controlLayout = self.make_control_layout()

        videoAreaLayout = QVBoxLayout()
        videoAreaLayout.addWidget(videoWidget)
        videoAreaLayout.addLayout(controlLayout)
        videoAreaLayout.addWidget(self.errorLabel)

        layout = QHBoxLayout()
        layout.addLayout(videoAreaLayout, 4)
        layout.addLayout(labellingLayout)

        wid.setLayout(layout)

    def make_control_layout(self):
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setContentsMargins(0, 0, 0, 0)

        buttonsLayout.addWidget(self.timeBox)
        buttonsLayout.addWidget(self.slowDownButton)
        buttonsLayout.addWidget(self.goBackButton)
        buttonsLayout.addWidget(self.goBack3Button)
        buttonsLayout.addWidget(self.playButton)
        buttonsLayout.addWidget(self.adv3Button)
        buttonsLayout.addWidget(self.advanceButton)
        buttonsLayout.addWidget(self.speedUpButton)
        buttonsLayout.addWidget(self.rateBox)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.positionSlider)
        layout.addWidget(self.labelSlider)
        layout.addLayout(buttonsLayout)
        return layout

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open video",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.openedFile = os.path.basename(fileName)
            self.setWindowTitle("tofu - " + self.openedFile)
            self.playButton.setEnabled(True)
            self.speedUpButton.setEnabled(True)
            self.slowDownButton.setEnabled(True)
            self.advanceButton.setEnabled(True)
            self.adv3Button.setEnabled(True)
            self.goBackButton.setEnabled(True)
            self.goBack3Button.setEnabled(True)
            self.rate = 1

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def slow(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.rate -= 0.5
            # TODO: Workaround pt 1
            # https://forum.qt.io/topic/88490/change-playback-rate-at-...
            # ...runtime-problem-with-position-qmediaplayer/8
            currentPos = self.mediaPlayer.position()
            # TODO: Workaround pt 1
            self.mediaPlayer.setPlaybackRate(self.rate)
            # TODO: Workaround pt 2
            self.mediaPlayer.setPosition(currentPos)
            # TODO: Workaround pt 2: end
            self.rateBox.setText(str(self.rate)+'x')

    def speed(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.rate += 0.5
            # TODO: Workaround pt 1
            # https://forum.qt.io/topic/88490/change-playback-rate-at-...
            # ...runtime-problem-with-position-qmediaplayer/8
            currentPos = self.mediaPlayer.position()
            # TODO: Workaround pt 1
            self.mediaPlayer.setPlaybackRate(self.rate)
            # TODO: Workaround pt 2
            self.mediaPlayer.setPosition(currentPos)
            # TODO: Workaround pt 2: end
            self.rateBox.setText(str(self.rate)+'x')

    def advance(self, t=10):
        currentPos = self.mediaPlayer.position()
        nextPos  = currentPos + t*1000
        self.setPosition(nextPos)

    def back(self, t=10):
        currentPos = self.mediaPlayer.position()
        nextPos  = max(currentPos - t*1000, 0)
        self.setPosition(nextPos)

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        self.timeBox.setText(format_time(int(position/1000)))

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.speedUpButton.setEnabled(False)
        self.slowDownButton.setEnabled(False)
        self.advanceButton.setEnabled(False)
        self.goBackButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def bindLabelEvent(self, keySeq, label):
        bind = QAction(label, self)
        bind.setShortcut(keySeq)
        bind.triggered.connect(partial(self.createMark, label))
        self.shortcuts[keySeq.toString()] = bind
        self.addAction(bind)

    def unbindLabelEvent(self, keySeqStr):
        self.removeAction(self.shortcuts[keySeqStr])
        del self.shortcuts[keySeqStr]

    def exportCsv(self):
        suggestedName = os.path.splitext(self.openedFile)[0] + '.csv'
        fileUrl, _ = QFileDialog.getSaveFileUrl(self, QDir.homePath(),
                QUrl.fromLocalFile(suggestedName))
        fileName = fileUrl.toLocalFile()

        if fileName != '':
            with open(fileName, mode='w') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
                marks = self.editorWidget.get_marks()
                writer.writerows(marks)

    @pyqtSlot()
    def createMark(self, label):
        state = self.mediaPlayer.state()
        if state == QMediaPlayer.PlayingState or state == \
                QMediaPlayer.PausedState:
            self.editorWidget.new_mark(self.mediaPlayer.position()/1000, label)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(940, 480)
    player.show()
    sys.exit(app.exec_())


