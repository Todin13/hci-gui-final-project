from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap
from piece import Piece
from game_logic import GameLogic
import os

# Dummy Piece class for demonstration
class Piece:
    def __init__(self, state, row, col):
        self.state = state  # 0 for empty, 1 for white, 2 for black
        self.row = row
        self.col = col

class Board(QFrame):
    updateTimerSignal = pyqtSignal(int)
    clickLocationSignal = pyqtSignal(str)

    boardWidth = 9  # 9x9 Goban
    boardHeight = 9
    player_turn = 1  # 1 for white, 2 for black
    isStarted = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.margin = 40
        self.initBoard()
        self.ko = None

        # Load assets
        self.background_pixmap = QPixmap("HGP_Group_12_Project/Assets/Goban_background.png")
        self.white_stone_pixmap = QPixmap("HGP_Group_12_Project/Assets/white_stone.png")
        self.black_stone_pixmap = QPixmap("HGP_Group_12_Project/Assets/black_stone.png")

        if self.background_pixmap.isNull():
            print("Failed to load Goban_background.png")
        if self.white_stone_pixmap.isNull():
            print("Failed to load white_stone.png")
        if self.black_stone_pixmap.isNull():
            print("Failed to load black_stone.png")

    def initBoard(self):
        """Initializes the board."""
        self.boardArray = [[Piece(0, r, c) for c in range(self.boardWidth)] for r in range(self.boardHeight)]
        self.logic = GameLogic(self.boardArray)
        self.printBoardArray()

    def printBoardArray(self):
        """Prints the boardArray for debugging."""
        print("boardArray:")
        print("\n".join(["\t".join([str(cell.state) for cell in row]) for row in self.boardArray]))

    def squareWidth(self):
        return self.contentsRect().width() / self.boardWidth

    def squareHeight(self):
        return self.contentsRect().height() / self.boardHeight

    def paintEvent(self, event):
        painter = QPainter(self)

        # Calculate the square playable area within the margins
        side = min(self.width() - 2 * self.margin, self.height() - 2 * self.margin)
        self.square_side = side
        self.top_left_x = (self.width() - side) // 2
        self.top_left_y = (self.height() - side) // 2

        # Draw the background to fill the entire widget
        self.drawBackground(painter)

        # Draw the board grid and pieces
        self.drawBoardLines(painter)
        self.drawStars(painter)
        self.drawPieces(painter)

    def drawBackground(self, painter):
        """Draw the background image covering the entire widget."""
        if not self.background_pixmap.isNull():
            painter.drawPixmap(self.rect(), self.background_pixmap.scaled(
                self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))


    def mousePressEvent(self, event):
        """this event is automatically called when the mouse is pressed"""
        assert self.logic.board == self.boardArray

        # Convert the mouse click position to a row and column
        col = int(event.position().x() // self.squareWidth())
        row = int(event.position().y() // self.squareHeight())

        # Ensure the click is within the board boundaries
        if self.logic.existing_position(row, col):
            
            piece = self.boardArray[row][col]
            if piece.state == 0:  # Only place if the intersection is empty
                piece.state = self.player_turn
                self.player_turn = 3 - self.player_turn  # Toggle turn
                self.update()  # Trigger repaint

            if piece.state == 0:

                new_piece = Piece(self.player_turn, row, col)

                if self.logic.check_piece_placement(new_piece):
                    # Set the piece state based on the player turn
                    piece.change_state(self.player_turn)
                    # self.printBoardArray()  # to debug

                    # Log the click and update the board
                    clickLoc = f"({row}, {col})"
                    print("mousePressEvent() -  Location :" + clickLoc)
                    self.clickLocationSignal.emit(
                        clickLoc
                    )  # prof put it but i don't like it need moddification
                    self.update()  # Redraw the board

                    # Alternate the player turn
                    if self.player_turn == 1:
                        self.player_turn = 2
                        self.player2Time = 60  # reset timer for player 2
                    else:
                        self.player_turn = 1
                        self.player1Time = 60  # reset timer for player 1



    def resetGame(self):
        self.initBoard()
        self.player_turn = 1
        self.isStarted = False
        self.update()

    def start(self):
        self.isStarted = True
        self.resetGame()
        print("Game started")

    def drawBoardLines(self, painter):
        """Draw the Go board lines (9x9 grid for intersections) within the margins."""
        painter.setPen(Qt.GlobalColor.black)

        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        for col in range(self.boardWidth):
            x = int(self.top_left_x + col * square_width)
            painter.drawLine(x, self.top_left_y, x, self.top_left_y + self.square_side)

        for row in range(self.boardHeight):
            y = int(self.top_left_y + row * square_height)
            painter.drawLine(self.top_left_x, y, self.top_left_x + self.square_side, y)


    def drawPieces(self, painter):
        """Draw pieces centered on intersections within the square board."""
        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        for row in range(len(self.boardArray)):
            for col in range(len(self.boardArray[0])):
                piece = self.boardArray[row][col]
                if piece.state == 1:  # White stone
                    pixmap = self.white_stone_pixmap
                elif piece.state == 2:  # Black stone
                    pixmap = self.black_stone_pixmap
                else:
                    continue

                # Calculate the center of the intersection
                center_x = self.top_left_x + col * square_width
                center_y = self.top_left_y + row * square_height
                size = min(square_width, square_height) * 0.9

                x = center_x - size / 2
                y = center_y - size / 2
                painter.drawPixmap(int(x), int(y), int(size), int(size), pixmap)

    def drawStars(self, painter):
        """Draw black dots (stars) at specific intersections on the board."""
        star_positions = [
            (3, 3),
            (7, 3),
            (5, 5),
            (3, 7),
            (7, 7)
        ]

        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        painter.setBrush(Qt.GlobalColor.black)
        painter.setPen(Qt.GlobalColor.black)

        for row, col in star_positions:
            x = self.top_left_x + (col - 1) * square_width
            y = self.top_left_y + (row - 1) * square_height
            size = min(square_width, square_height) * 0.1  # Star size as a fraction of square size
            painter.drawEllipse(int(x - size / 2), int(y - size / 2), int(size), int(size))

    def print_player_turn(self):
        color = "white" if self.player_turn == 1 else "black"
        print(f"Player {self.player_turn} ({color}) turn")

    def sizeHint(self):
        return QSize(800, 800)
