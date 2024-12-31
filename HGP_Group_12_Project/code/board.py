from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap
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
        self.initBoard()
        self.ko = None

        # Load assets
        self.background = QPixmap("HGP_Group_12_Project/Assets/Goban_background.png")
        self.white_stone_pixmap = QPixmap("HGP_Group_12_Project/Assets/white_stone.png")
        self.black_stone_pixmap = QPixmap("HGP_Group_12_Project/Assets/black_stone.png")

        if self.background.isNull():
            print("Failed to load Goban_background.png")
        if self.white_stone_pixmap.isNull():
            print("Failed to load white_stone.png")
        if self.black_stone_pixmap.isNull():
            print("Failed to load black_stone.png")

    def initBoard(self):
        """Initializes the board."""
        self.boardArray = [[Piece(0, r, c) for c in range(self.boardWidth)] for r in range(self.boardHeight)]
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

        # Calculate the square playable area
        side = min(self.width(), self.height()) - 40  # Ensure space for borders
        self.square_side = side
        self.top_left_x = (self.width() - side) // 2
        self.top_left_y = (self.height() - side) // 2

        # Set clipping region to ensure we draw only within the square
        painter.setClipRect(self.top_left_x, self.top_left_y, side, side)

        self.drawBackground(painter)
        self.drawBoardLines(painter)
        self.drawPieces(painter)


    def drawBackground(self, painter):
        """Draw the background image."""
        painter.drawPixmap(self.rect(), self.background)

    def mousePressEvent(self, event):
        """Handle clicks within the square board area."""
        if not (self.top_left_x <= event.position().x() <= self.top_left_x + self.square_side and
                self.top_left_y <= event.position().y() <= self.top_left_y + self.square_side):
            return  # Ignore clicks outside the square board

        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        col = round((event.position().x() - self.top_left_x) / square_width)
        row = round((event.position().y() - self.top_left_y) / square_height)

        if 0 <= row < self.boardHeight and 0 <= col < self.boardWidth:
            piece = self.boardArray[row][col]
            if piece.state == 0:  # Only place if the intersection is empty
                piece.state = self.player_turn
                self.player_turn = 3 - self.player_turn  # Toggle turn
                self.update()  # Trigger repaint



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
        """Draw the grid lines within the square board."""
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
                size = min(square_width, square_height) * 0.6  # Scale stone size slightly smaller

                x = center_x - size / 2
                y = center_y - size / 2
                painter.drawPixmap(int(x), int(y), int(size), int(size), pixmap)


    def print_player_turn(self):
        color = "white" if self.player_turn == 1 else "black"
        print(f"Player {self.player_turn} ({color}) turn")

    def sizeHint(self):
        return QSize(800, 800)
