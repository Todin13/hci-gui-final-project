from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QMessageBox,
    QVBoxLayout,
    QWidget,
    QPushButton,
)
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
        self.scoreBoard = ScoreBoard()
        self.board = Board(self, self.scoreBoard)  # Pass the scoreBoard to the Board

        self.stackedWidget.addWidget(self.startPage)
        self.stackedWidget.addWidget(self.playerNamesPage)
        self.stackedWidget.addWidget(self.board)

        self.startPage.newGameSignal.connect(self.showPlayerNamesPage)
        self.playerNamesPage.startGameSignal.connect(self.startGame)

        self.board.resetGameSignal.connect(
            self.resetGame
        )  # Connecter le signal de réinitialisation
        self.scoreBoard.resetGameSignal.connect(
            self.resetGame
        )  # Connecter le signal de réinitialisation
        self.scoreBoard.resignSignal.connect(
            self.confirmResign
        )  # Connecter le signal de résignation
        self.scoreBoard.disputeNotSuccessingSignal.connect(
            self.confirmDisputeNotSuccessful
        )  # Connecter le signal de dispute
        # self.board.returnToMenuSignal.connect(self.showStartPage)  # Connecter le signal pour retourner au menu

        self.adjustSize()  # Ajuste la taille de la fenêtre en fonction du contenu
        self.center()
        self.setWindowTitle("Go game")
        self.show()

    def center(self):
        """Centers the window on the screen"""
        current_widget = self.stackedWidget.currentWidget()
        if current_widget:
            size = current_widget.sizeHint()
            self.resize(size)

        screen = QApplication.primaryScreen().availableGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def showPlayerNamesPage(self, gamemode):
        self.stackedWidget.setCurrentWidget(self.playerNamesPage)
        self.adjustSize()  # Ajuste la taille de la fenêtre en fonction du contenu
        self.center()  # Centre la fenêtre
        self.board.gamemode = gamemode

    def startGame(self, player1=None, player2=None):
        if player1 and player2:
            self.stackedWidget.setCurrentWidget(self.board)
            self.board.start()
            self.scoreBoard.make_connection(self.board)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.scoreBoard)
            self.scoreBoard.passTurnSignal.connect(self.pass_turn)
            self.scoreBoard.gamemode = self.board.gamemode
            self.scoreBoard.updatePlayerNames(player1, player2)  # Update player names
            print(f"Game started with players: {player1} vs {player2}")
        else:
            self.stackedWidget.setCurrentWidget(self.board)
            self.board.start()
            self.scoreBoard.make_connection(self.board)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.scoreBoard)
            self.scoreBoard.passTurnSignal.connect(self.pass_turn)
            self.scoreBoard.gamemode = self.board.gamemode
            self.scoreBoard.updatePlayerNames(
                "White Player", "Black Player"
            )  # Update player names
            print("New game started")

        self.adjustSize()  # Ajuste la taille de la fenêtre en fonction du contenu
        self.center()  # Centre la fenêtre

    def pass_turn(self):
        self.board.update_turn(True)

    def resetGame(self):
        self.board.start()
        self.board.print_player_turn()
        self.scoreBoard.updatePrisoners(0, 0)
        self.scoreBoard.updateTerritory(0, 0)
        self.scoreBoard.updateTurn(self.board.player_turn)

    def confirmResign(self):
        reply = QMessageBox.question(
            self,
            "Confirm Resign",
            "Are you sure you want to resign?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.resignGame()

    def confirmDisputeNotSuccessful(self):
        reply = QMessageBox.question(
            self,
            "Confirm Dispute Not Successful",
            "Are you sure you want to select : Dispute not successful?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.disputeNotSuccessing()

    # def showStartPage(self):
    #     self.stackedWidget.setCurrentWidget(self.startPage)
    #     self.adjustSize()  # Ajuste la taille de la fenêtre en fonction du contenu
    #     self.center()  # Centre la fenêtre

    def resignGame(self):
        self.board.resignGame()

    def disputeNotSuccessing(self):
        self.board.disputeNotSuccessing()

    def resizeEvent(self, event):
        """Adjust the size of the window based on the current page"""
        current_widget = self.stackedWidget.currentWidget()
        if current_widget:
            self.resize(current_widget.sizeHint())
        super().resizeEvent(event)
