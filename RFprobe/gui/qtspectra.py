# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'spectra.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SpectraViewer(object):
    def setupUi(self, SpectraViewer):
        SpectraViewer.setObjectName("SpectraViewer")
        SpectraViewer.resize(663, 666)
        self.centralwidget = QtWidgets.QWidget(SpectraViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 661, 51))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.header = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.header.setContentsMargins(0, 0, 0, 0)
        self.header.setObjectName("header")
        self.time = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(28)
        self.time.setFont(font)
        self.time.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.time.setAutoFillBackground(False)
        self.time.setAlignment(QtCore.Qt.AlignCenter)
        self.time.setObjectName("time")
        self.header.addWidget(self.time)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(0, 50, 661, 482))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.body = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setObjectName("body")
        self.spectra = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.spectra.setMinimumSize(QtCore.QSize(640, 480))
        self.spectra.setMaximumSize(QtCore.QSize(800, 600))
        self.spectra.setAlignment(QtCore.Qt.AlignCenter)
        self.spectra.setObjectName("spectra")
        self.body.addWidget(self.spectra)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(400, 530, 251, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.buttons = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.buttons.setContentsMargins(0, 0, 0, 0)
        self.buttons.setObjectName("buttons")
        self.stop = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.stop.setObjectName("stop")
        self.buttons.addWidget(self.stop)
        self.pause = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pause.setObjectName("pause")
        self.buttons.addWidget(self.pause)
        SpectraViewer.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SpectraViewer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 663, 25))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        SpectraViewer.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SpectraViewer)
        self.statusbar.setObjectName("statusbar")
        SpectraViewer.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(SpectraViewer)
        QtCore.QMetaObject.connectSlotsByName(SpectraViewer)

    def retranslateUi(self, SpectraViewer):
        _translate = QtCore.QCoreApplication.translate
        SpectraViewer.setWindowTitle(_translate("SpectraViewer", "Spectra Viewer"))
        self.time.setText(_translate("SpectraViewer", "00:00:00:00.00"))
        self.spectra.setText(_translate("SpectraViewer", "Spectra"))
        self.stop.setText(_translate("SpectraViewer", "Stop"))
        self.pause.setText(_translate("SpectraViewer", "Pause"))
        self.menuFile.setTitle(_translate("SpectraViewer", "File"))
        self.menuView.setTitle(_translate("SpectraViewer", "View"))
        self.menuHelp.setTitle(_translate("SpectraViewer", "Help"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SpectraViewer = QtWidgets.QMainWindow()
    ui = Ui_SpectraViewer()
    ui.setupUi(SpectraViewer)
    SpectraViewer.show()
    sys.exit(app.exec_())

