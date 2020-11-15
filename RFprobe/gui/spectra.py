from PyQt5.QtGui import QPalette, QPixmap
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMainWindow, QMenu, QAction


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

        self.setWindowTitle("Image Viewer")
        self.resize(500, 400)


    def createActions(self):
#        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
#                triggered=self.open)

#        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P",
#                enabled=False, triggered=self.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

#        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++",
#                enabled=False, triggered=self.zoomIn)

#        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-",
#                enabled=False, triggered=self.zoomOut)

#        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S",
#                enabled=False, triggered=self.normalSize)

#        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False,
#                checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)

#        self.aboutAct = QAction("&About", self, triggered=self.about)

 #       self.aboutQtAct = QAction("About &Qt", self,
#                triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
#        self.fileMenu.addAction(self.openAct)
#        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
#        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
#        self.viewMenu.addAction(self.zoomInAct)
#        self.viewMenu.addAction(self.zoomOutAct)
#        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
#        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QMenu("&Help", self)
#        self.helpMenu.addAction(self.aboutAct)
#        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def publish(self, data):
        print(data)
        #self.imageLabel.setPixmap(QPixmap.loadFromData(data, format="RGB"))
        #self.printAct.setEnabled(True)
        #self.fitToWindowAct.setEnabled(True)
        #self.updateActions()


