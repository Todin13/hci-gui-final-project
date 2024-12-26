from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush
from piece import Piece


class Board(QFrame):  # base the board on a QFrame widget
    updateTimerSignal = pyqtSignal(int)  # signal sent when the timer is updated
    clickLocationSignal = pyqtSignal(
        str
    )  # signal sent when there is a new click location

    # TODO set the board width and height to be square
    boardWidth = 7  # board is 7 squares wide 
    boardHeight = 7  #board is 7 squares high
    timerSpeed = 1000  # the timer updates every 1 second
    counter = 10  # the number the counter will count down from
    player_turn = 0 # player turn 0 for nobody game not started
    isStarted = False  # game is not currently started

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()

    def initBoard(self):
        """initiates board"""
        self.timer = QTimer(self)  # create a timer for the game
        self.timer.timeout.connect(
            self.timerEvent
        )  # connect timeout signal to timerEvent method
        # self.start()  # start the game which will start the timer we will use a button
        self.boardArray = (
            [[Piece(0, r, c) for c in range(7)] for r in range(7)]
        )  # create a 2d int/Piece array to store the state of the game
        self.printBoardArray() # for debug

    def printBoardArray(self):
        """prints the boardArray in an attractive way"""
        print("boardArray:")
        print(
            "\n".join(
                ["\t".join([str(cell) for cell in row]) for row in self.boardArray]
            )
        )

    def mousePosToColRow(self, event):
        """convert the mouse click event to a row and column"""
        pass  # Implement this method according to your logic

    def squareWidth(self):
        """returns the width of one square in the board"""
        return self.contentsRect().width() / self.boardWidth

    def squareHeight(self):
        """returns the height of one square of the board"""
        return self.contentsRect().height() / self.boardHeight

    def start(self):
        """starts game"""
        self.isStarted = (
            True  # set the boolean which determines if the game has started to TRUE
        )
        self.resetGame()  # reset the game
        self.timer.start(self.timerSpeed)  # start the timer with the correct speed
        print("start () - timer is started")
        self.player_turn = 2
        self.print_player_turn()
        self.play_game()
        

    def timerEvent(self):
        """this event is automatically called when the timer is updated. based on the timerSpeed variable"""
        # TODO adapt this code to handle your timers
        if Board.counter == 0:
            print("Game over")
        self.counter -= 1
        print("timerEvent()", self.counter)
        self.updateTimerSignal.emit(self.counter)

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
            # Toggle the state of the piece at the clicked position
            piece = self.boardArray[row][col]
            piece.change_state(1)
            self.printBoardArray() # to debug
            
            # Log the click and update the board
            clickLoc = f"({row}, {col})"
            print("mousePressEvent() -  Location :" + clickLoc)
            self.clickLocationSignal.emit(clickLoc) # prof put it but i don't like it need moddification
            self.update()  # Redraw the board

    def resetGame(self):
        """clears pieces from the board"""
        # TODO write code to reset game

    def tryMove(self, newX, newY):
        """tries to move a piece"""
        pass  # Implement this method according to your logic

    def drawBoardSquares(self, painter):
        """draw all the square on the board"""
        squareWidth = self.squareWidth()
        squareHeight = self.squareHeight()
        for row in range(0, Board.boardHeight):
            for col in range(0, Board.boardWidth):
                painter.save()
                painter.translate(col * squareWidth, row * squareHeight)
                painter.setBrush(QBrush(QColor(255, 255, 255)))  # Set brush color
                painter.drawRect(0, 0, int(squareWidth), int(squareHeight))  # Draw rectangles
                painter.restore()

    def drawPieces(self, painter):
        """draw the pieces on the board"""
        for row in range(0, len(self.boardArray)):
            for col in range(0, len(self.boardArray[0])):
                painter.save()
                painter.translate(col * self.squareWidth(), row * self.squareHeight())
                # TODO draw some pieces as ellipses
                # TODO choose your color and set the painter brush to the correct color
                radius = (self.squareWidth() - 2) / 2
                center = QPoint(int(radius), int(radius))

                # Set color based on player_turn and piece state
                if self.player_turn == 0:  # Player turn 0: all circles white
                    painter.setPen(QColor(255, 255, 255))  # Black outline
                    painter.setBrush(QBrush(QColor(255, 255, 255)))  # White
                elif self.player_turn == 1:  # Player turn 1: outline in black
                    painter.setPen(QColor(0, 0, 0))  # Black outline
                elif self.player_turn == 2:  # Player turn 2: fill circle in black
                    painter.setBrush(QBrush(QColor(0, 0, 0)))  # Black fill


                painter.drawEllipse(center, int(radius), int(radius))
                painter.restore()

    def print_player_turn(self):
        """
        Print for debug the player turn
        """
        color = "black" if self.player_turn == 2 else "white" 
        print(f"player {self.player_turn} ({color}) turn")