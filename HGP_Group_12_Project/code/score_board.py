from PyQt6.QtWidgets import (
    QDockWidget,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QPushButton,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot


class ScoreBoard(QDockWidget):
    """Base the score_board on a QDockWidget"""

    passTurnSignal = pyqtSignal()
    resetGameSignal = pyqtSignal()
    endGameSignal = pyqtSignal(
        int
    )  # Signal to end the game with the winner's player number

    def __init__(self):
        super().__init__()
        self.initUI()
        self.pass_count = 0  # Counter for consecutive passes
        self.last_player_passed = None  # Track the last player who passed
        self.board = None  # Attribute to store the Board object

    def initUI(self):
        """Initiates ScoreBoard UI"""
        self.resize(300, 400)
        self.setWindowTitle("ScoreBoard")

        # Create a widget to hold other widgets
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()

        # Create labels and buttons
        self.label_clickLocation = QLabel("Click Location: ")
        self.label_timeRemaining = QLabel("Time remaining: ")
        self.label_player1 = QLabel("Player 1: ")
        self.label_player2 = QLabel("Player 2: ")
        self.label_prisoners_p1 = QLabel("Prisoners P1: 0")
        self.label_prisoners_p2 = QLabel("Prisoners P2: 0")
        self.label_territory_p1 = QLabel("Territory P1: 0")
        self.label_territory_p2 = QLabel("Territory P2: 0")
        self.label_turn = QLabel("Turn: ")

        self.button_pass = QPushButton("Pass")
        self.button_reset = QPushButton("Reset Game")

        self.mainWidget.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.label_clickLocation)
        self.mainLayout.addWidget(self.label_timeRemaining)

        playerLayout = QHBoxLayout()
        playerLayout.addWidget(self.label_player1)
        playerLayout.addWidget(self.label_player2)
        self.mainLayout.addLayout(playerLayout)

        prisonersLayout = QHBoxLayout()
        prisonersLayout.addWidget(self.label_prisoners_p1)
        prisonersLayout.addWidget(self.label_prisoners_p2)
        self.mainLayout.addLayout(prisonersLayout)

        territoryLayout = QHBoxLayout()
        territoryLayout.addWidget(self.label_territory_p1)
        territoryLayout.addWidget(self.label_territory_p2)
        self.mainLayout.addLayout(territoryLayout)

        self.mainLayout.addWidget(self.label_turn)
        self.mainLayout.addWidget(self.button_pass)
        self.mainLayout.addWidget(self.button_reset)

        self.setWidget(self.mainWidget)

    def make_connection(self, board):
        """This handles a signal sent from the board class"""
        self.board = board  # Store the Board object
        # When the clickLocationSignal is emitted in board the setClickLocation slot receives it
        board.clickLocationSignal.connect(self.setClickLocation)
        # When the updateTimerSignal is emitted in the board the setTimeRemaining slot receives it
        board.updateTimerSignal.connect(self.setTimeRemaining)
        self.button_pass.clicked.connect(self.pass_turn)
        self.button_reset.clicked.connect(self.resetGameSignal.emit)

    @pyqtSlot(
        str
    )  # Checks to make sure that the following slot is receiving an argument of the type 'int'
    def setClickLocation(self, clickLoc):
        """Updates the label to show the click location"""
        self.label_clickLocation.setText("Click Location: " + clickLoc)
        # print("slot " + clickLoc)

    @pyqtSlot(int)
    def setTimeRemaining(self, timeRemaining):
        """Updates the time remaining label to show the time remaining"""
        update = "Time Remaining: " + str(timeRemaining)
        self.label_timeRemaining.setText(update)
        # print("slot " + str(timeRemaining))
        # self.redraw()

    def updatePrisoners(self, prisoners_p1, prisoners_p2):
        self.label_prisoners_p1.setText(f"Prisoners P1: {prisoners_p1}")
        self.label_prisoners_p2.setText(f"Prisoners P2: {prisoners_p2}")

    def updateTerritory(self, territory_p1, territory_p2):
        self.label_territory_p1.setText(f"Territory P1: {territory_p1}")
        self.label_territory_p2.setText(f"Territory P2: {territory_p2}")

    def updateTurn(self, player_turn):
        color = "black" if player_turn == 2 else "white"
        self.label_turn.setText(f"Turn: Player {player_turn} ({color}) to play")

    def pass_turn(self):
        if self.last_player_passed is None:
            self.last_player_passed = self.board.player_turn
            self.pass_count = 1
        elif self.last_player_passed == self.board.player_turn:
            self.pass_count += 1
        else:
            self.last_player_passed = self.board.player_turn
            self.pass_count = 1

        if self.pass_count >= 3:
            self.endGameSignal.emit(3 - self.board.player_turn)  # The other player wins
        elif self.pass_count == 2:
            self.endGameSignal.emit(0)  # The game ends in a draw

        self.passTurnSignal.emit()

    def reset_pass_count(self):
        self.pass_count = 0
        self.last_player_passed = None
