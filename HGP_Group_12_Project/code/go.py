from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QSize
from board import Board
from score_board import ScoreBoard
from start_page import StartPage
from player_names_page import PlayerNamesPage

class Go(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initiates application UI"""
        self.stackedWidget = QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        self.startPage = StartPage()
        self.playerNamesPage = PlayerNamesPage()
        self.board = Board(self)
        self.scoreBoard = ScoreBoard()

        self.stackedWidget.addWidget(self.startPage)
        self.stackedWidget.addWidget(self.playerNamesPage)
        self.stackedWidget.addWidget(self.board)

        self.startPage.newGameSignal.connect(self.showPlayerNamesPage)
        self.playerNamesPage.startGameSignal.connect(self.startGame)

        self.adjustSize()  # Ajuste la taille de la fenêtre en fonction du contenu
        self.center()
        self.setWindowTitle("Go")
        self.show()

    def center(self):
        """Centers the window on the screen"""
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def showPlayerNamesPage(self):
        self.stackedWidget.setCurrentWidget(self.playerNamesPage)
        self.adjustSize()  # Ajuste la taille de la fenêtre en fonction du contenu
        self.resize(self.playerNamesPage.sizeHint())  # Ajuste la taille de la fenêtre en fonction de la taille de la page

    def startGame(self, player1, player2):
        self.stackedWidget.setCurrentWidget(self.board)
        self.board.start()
        self.scoreBoard.make_connection(self.board)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.scoreBoard)
        print(f"Game started with players: {player1} vs {player2}")
        self.adjustSize()  # Ajuste la taille de la fenêtre en fonction du contenu
        self.resize(QSize(800, 800))  # Définir les dimensions initiales pour la page du jeu de Go

    def resizeEvent(self, event):
        """Adjust the size of the window based on the current page"""
        current_widget = self.stackedWidget.currentWidget()
        if current_widget:
            self.resize(current_widget.sizeHint())
        super().resizeEvent(event)
