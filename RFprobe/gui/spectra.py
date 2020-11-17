from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QPalette, QPixmap, QImage
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMainWindow, QMenu, QAction
import numpy as np


class GUIspectra(QMainWindow):

    def __init__(self):
        super(GUIspectra, self).__init__()

        self.printer = QPrinter()
        self.scaleFactor = 0.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Spectra Viewer")
        self.resize(800, 600)


    def createActions(self):

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)


    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addSeparator()

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addSeparator()

        self.helpMenu = QMenu("&Help", self)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def publish(self, triplet):
        data, width, height = triplet
        self.imageLabel.setGeometry(QRect(0, 0, width, height))
        image = QImage(width, height, QImage.Format_RGB32)
        image.fromData(data)

        self.imageLabel.setPixmap(QPixmap.fromImage(image))



