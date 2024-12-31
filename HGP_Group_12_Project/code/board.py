from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap
from piece import Piece
import os



class Board(QFrame):  # base the board on a QFrame widget
    updateTimerSignal = pyqtSignal(int)  # signal sent when the timer is updated
    clickLocationSignal = pyqtSignal(str)  # signal sent when there is a new click location

    # TODO set the board width and height to be square
    boardWidth = 7  # board is 7 squares wide
    boardHeight = 7  # board is 7 squares high
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
        self.boardArray = [[Piece(0, r, c) for c in range(self.boardWidth)] for r in range(self.boardHeight)]  # create a 2d int/Piece array to store the state of the game
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

            # Check if the piece is already placed
            if piece.state == 0:
                # Set the piece state based on the player turn
                piece.change_state(self.player_turn)
                self.printBoardArray()
                captured = self.capture_pieces(row, col)
                if captured:
                    self.ko = (row, col)
                if self.ko and self.ko == (row, col):
                    print("Ko rule applied. Cannot capture immediately.")
                    piece.change_state(0)
                    self.ko = None
                else:
                    for r, c in captured:
                        self.boardArray[r][c].change_state(0)
                    clickLoc = f"({row}, {col})"
                    print("mousePressEvent() -  Location :" + clickLoc)
                    self.clickLocationSignal.emit(clickLoc)
                    self.update()
                    if self.player_turn == 1:
                        self.player_turn = 2
                        self.player2Time = 60
                    else:
                        self.player_turn = 1
                        self.player1Time = 60

                    if self.is_game_over():
                        black_score, white_score = self.count_score()
                        print(f"Game over! Black score: {black_score}, White score: {white_score}")
                        # Add logic to display the winner

    def resetGame(self):
        self.boardArray = [[Piece(0, r, c) for c in range(self.boardWidth)] for r in range(self.boardHeight)]
        self.printBoardArray() # for debug
        self.player1Time = 60  # reset player 1 timer
        self.player2Time = 60  # reset player 2 timer

    def capture_pieces(self, row, col):
        captured = []
        to_visit = [(row, col)]
        visited = set()
        liberties = 0

        while to_visit:
            r, c = to_visit.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            piece = self.boardArray[r][c]
            if piece.state == 0:
                liberties += 1
            else:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.boardHeight and 0 <= nc < self.boardWidth:
                        if (nr, nc) not in visited:
                            to_visit.append((nr, nc))

        if liberties == 0:
            for r, c in visited:
                if self.boardArray[r][c].state != 0:
                    captured.append((r, c))

        return captured

    def is_game_over(self):
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                if self.boardArray[row][col].state == 0:
                    return False
        return True

    def count_score(self):
        black_score = 0
        white_score = 0
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                piece = self.boardArray[row][col]
                if piece.state == 1:
                    white_score += 1
                elif piece.state == 2:
                    black_score += 1
        return black_score, white_score

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
