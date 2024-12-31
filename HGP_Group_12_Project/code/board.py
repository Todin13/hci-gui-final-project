from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap
from piece import Piece
import os



class Board(QFrame):  # base the board on a QFrame widget
    updateTimerSignal = pyqtSignal(int)  # signal sent when the timer is updated
    clickLocationSignal = pyqtSignal(str)  # signal sent when there is a new click location

    # TODO set the board width and height to be square
    boardWidth = 8  # board is 8 squares wide not 7 because 7 will create a 8x8 game and we want a 9x9 game
    boardHeight = 8  # board is 8 squares high not 7 because 7 will create a 8x8 game and we want a 9x9 game
    timerSpeed = 1000  # the timer updates every 1 second
    player1Time = 60  # player 1 has 60 seconds to play
    player2Time = 60  # player 2 has 60 seconds to play
    player_turn = 0  # player turn 0 for nobody game not started
    isStarted = False  # game is not currently started

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()
        self.ko = None  # Variable to keep track of the last capture
        self.setStyleSheet("background-color: #D2B48C;")  # Set background color
        self.white_stone_pixmap = QPixmap(os.path.join("images", "white_stone.jpg"))
        self.black_stone_pixmap = QPixmap(os.path.join("images", "black_stone.jpg"))

        if self.white_stone_pixmap.isNull():
            print("Failed to load white_stone.jpg")
        if self.black_stone_pixmap.isNull():
            print("Failed to load black_stone.jpg")

    def initBoard(self):
        """initiates board"""
        self.timer = QTimer(self)  # create a timer for the game
        self.timer.timeout.connect(self.timerEvent)  # connect timeout signal to timerEvent method
        self.boardArray = [[Piece(0, r, c) for c in range(self.boardWidth+1)] for r in range(self.boardHeight+1)]  # create a 2d int/Piece array to store the state of the game of size board game + 1 as we play on intersections 
        self.printBoardArray() # for debug

    def printBoardArray(self):
        """prints the boardArray in an attractive way"""
        print("boardArray:")
        print("\n".join(["\t".join([str(cell) for cell in row]) for row in self.boardArray]))

    def squareWidth(self):
        """returns the width of one square in the board"""
        return self.contentsRect().width() / self.boardWidth

    def squareHeight(self):
        """returns the height of one square of the board"""
        return self.contentsRect().height() / self.boardHeight

    def start(self):
        """starts game"""
        self.isStarted = True  # set the boolean which determines if the game has started to TRUE
        self.resetGame()  # reset the game
        self.timer.start(self.timerSpeed)  # start the timer with the correct speed
        print("start () - timer is started")
        self.player_turn = 1  # Start with white piece
        self.print_player_turn()

    def timerEvent(self):
        """this event is automatically called when the timer is updated. based on the timerSpeed variable"""
        if self.player_turn == 1:
            self.player1Time -= 1
            if self.player1Time <= 0:
                self.player1Time = 60  # reset timer for player 1
                self.player_turn = 2  # switch to player 2
        else:
            self.player2Time -= 1
            if self.player2Time <= 0:
                self.player2Time = 60  # reset timer for player 2
                self.player_turn = 1  # switch to player 1

        self.updateTimerSignal.emit(
            self.player1Time if self.player_turn == 1 else self.player2Time
        )
        self.print_player_turn()

    def paintEvent(self, event):
        """paints the board and the pieces of the game"""
        painter = QPainter(self)
        self.drawBoardSquares(painter)
        self.drawPieces(painter)

    def mousePressEvent(self, event):
        """this event is automatically called when the mouse is pressed"""
        # Convert the mouse click position to a row and column
        col = int(event.position().x() // self.squareWidth())
        row = int(event.position().y() // self.squareHeight())

        # Ensure the click is within the board boundaries
        if 0 <= row < self.boardHeight and 0 <= col < self.boardWidth:
            # Get the piece at the clicked position
            piece = self.boardArray[row][col]

    def resetGame(self):
        self.boardArray = [[Piece(0, r, c) for c in range(self.boardWidth+1)] for r in range(self.boardHeight+1)]
        self.printBoardArray() # for debug
        self.player1Time = 120  # reset player 1 timer
        self.player2Time = 120  # reset player 2 timer

    def drawBoardSquares(self, painter):
        """draw all the square on the board"""
        squareWidth = self.squareWidth()
        squareHeight = self.squareHeight()
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                painter.save()
                painter.translate(col * squareWidth, row * squareHeight)
                painter.setBrush(QBrush(QColor(238, 238, 210)))  # Light brown color
                painter.drawRect(0, 0, int(squareWidth), int(squareHeight))
                painter.restore()

    def drawPieces(self, painter):
        """draw the pieces on the board"""
        for row in range(len(self.boardArray)):
            for col in range(len(self.boardArray[0])):
                painter.save()
                painter.translate(col * self.squareWidth(), row * self.squareHeight())

                # Set the piece color based on its state
                piece = self.boardArray[row][col]
                if piece.state == 1:
                    pixmap = self.white_stone_pixmap
                elif piece.state == 2:
                    pixmap = self.black_stone_pixmap
                else:
                    pixmap = QPixmap()

                if not pixmap.isNull():
                    painter.drawPixmap(0, 0, pixmap.scaled(self.squareWidth(), self.squareHeight(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                painter.restore()

    def print_player_turn(self):
        """Print for debug the player turn"""
        color = "black" if self.player_turn == 2 else "white"
        print(f"player {self.player_turn} ({color}) turn")

    def sizeHint(self):
        return QSize(800, 800)
