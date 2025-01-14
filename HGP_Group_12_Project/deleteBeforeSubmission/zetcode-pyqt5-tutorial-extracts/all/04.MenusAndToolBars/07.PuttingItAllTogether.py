"""
ZetCode PyQt5 tutorial-deleteBeforeSubmission

This program creates a skeleton of
a classic GUI application with a menubar,
toolbar, statusbar, and a central widget.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""

import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        textEdit = QTextEdit()
        self.setCentralWidget(textEdit)

        exitAct = QAction(QIcon("exit24.png"), "Exit", self)
        exitAct.setShortcut("Ctrl+Q")
        exitAct.setStatusTip("Exit application")
        exitAct.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar("Exit")
        toolbar.addAction(exitAct)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle("Main window")
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
