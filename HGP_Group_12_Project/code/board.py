from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap
from piece import Piece
from game_logic import GameLogic


class Board(QFrame):
    updateTimerSignal = pyqtSignal(int)
    clickLocationSignal = pyqtSignal(str)

    boardWidth = 9  # 9x9 Goban
    boardHeight = 9
    player_turn = 1  # 1 for white, 2 for black
    isStarted = False

    def __init__(self, parent=None, scoreBoard=None):
        super().__init__(parent)
        self.margin = 40
        self.scoreBoard = scoreBoard  # Store the scoreBoard reference
        self.initBoard()
        self.ko = None

        # Load assets
        self.background_pixmap = QPixmap(
            "HGP_Group_12_Project/Assets/Goban_background.png"
        )
        self.white_stone_pixmap = QPixmap("HGP_Group_12_Project/Assets/white_stone.png")
        self.black_stone_pixmap = QPixmap("HGP_Group_12_Project/Assets/black_stone.png")

        if self.background_pixmap.isNull():
            print("Failed to load Goban_background.png")
        if self.white_stone_pixmap.isNull():
            print("Failed to load white_stone.png")
        if self.black_stone_pixmap.isNull():
            print("Failed to load black_stone.png")

        self.captured_pieces = []  # List to track captured pieces
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(
            self.slideOutCapturedPieces
        )  # Timer for sliding animation

        self.hover_row = -1  # Default no hover
        self.hover_col = -1  # Default no hover
        self.transparent_piece_color = (
            1  # Default hover as white (1 for white, 2 for black)
        )
        self.setMouseTracking(True)  # Enable mouse tracking

    def initBoard(self):
        """Initializes the board."""
        self.boardArray = [
            [Piece(0, r, c) for c in range(self.boardWidth)]
            for r in range(self.boardHeight)
        ]
        self.logic = GameLogic(self.boardArray)
        self.printBoardArray()

    def printBoardArray(self):
        """Prints the boardArray for debugging."""
        print("boardArray:")
        print(
            "\n".join(
                [
                    "\t".join([str(cell.state) for cell in row])
                    for row in self.boardArray
                ]
            )
        )

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

        # Draw hover pieces
        self.drawHoverPiece(painter)

        # Draw captured pieces
        self.drawCapturedPieces(painter)

    def drawBackground(self, painter):
        """Draw the background image covering the entire widget."""
        if not self.background_pixmap.isNull():
            painter.drawPixmap(
                self.rect(),
                self.background_pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ),
            )

    def mousePressEvent(self, event):
        """This event is automatically called when the mouse is pressed"""
        assert self.logic.board == self.boardArray

        if not (
            self.top_left_x
            <= event.position().x()
            <= self.top_left_x + self.square_side
            and self.top_left_y
            <= event.position().y()
            <= self.top_left_y + self.square_side
        ):
            return  # Ignore clicks outside the square board

        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)
        col = round((event.position().x() - self.top_left_x) / square_width)
        row = round((event.position().y() - self.top_left_y) / square_height)

        # Ensure the click is within the board boundaries
        if self.logic.existing_position(row, col):

            piece = self.boardArray[row][col]

            if piece.state == 0:

                new_piece = Piece(self.player_turn, row, col)

                if self.logic.check_piece_placement(new_piece):
                    # Set the piece state based on the player turn
                    piece.change_state(self.player_turn)
                    # self.printBoardArray()  # to debug

                    captured_positions = self.logic.capturing_territory(new_piece)

                    if captured_positions:
                        self.setMouseTracking(False)
                        self.handleCapturedPieces(captured_positions)
                        self.setMouseTracking(True)

                    # Log the click and update the board
                    clickLoc = f"({row}, {col})"
                    print("mousePressEvent() -  Location :" + clickLoc)
                    self.clickLocationSignal.emit(
                        clickLoc
                    )  # prof put it but i don't like it need modification
                    self.update()  # Redraw the board

                    # Update prisoners and territory
                    prisoners_p1, prisoners_p2 = self.logic.count_prisoners()
                    territory_p1, territory_p2 = self.logic.count_territory()
                    self.scoreBoard.updatePrisoners(prisoners_p1, prisoners_p2)
                    self.scoreBoard.updateTerritory(territory_p1, territory_p2)

                    # Alternate the player turn
                    if self.player_turn == 1:
                        self.player_turn = 2
                        self.player2Time = 60  # reset timer for player 2
                    else:
                        self.player_turn = 1
                        self.player1Time = 60  # reset timer for player 1

                    # Update the turn display
                    self.scoreBoard.updateTurn(self.player_turn)

    def mouseMoveEvent(self, event):
        """Track the mouse position and determine the hovered position."""
        mouse_x, mouse_y = event.position().x(), event.position().y()

        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        col = round((mouse_x - self.top_left_x) / square_width)
        row = round((mouse_y - self.top_left_y) / square_height)

        # Validate hover position
        if self.logic.existing_position(row, col):
            if (
                self.logic.check_piece_placement(
                    Piece(self.player_turn, row, col), hover=True
                )
                and self.boardArray[row][col].state == 0
            ):  # Only hover if position is empty and respect game rules
                self.hover_row = row
                self.hover_col = col
            else:
                self.hover_row = -1
                self.hover_col = -1
        else:
            self.hover_row = -1
            self.hover_col = -1

        self.update()  # Trigger repaint

    def drawHoverPiece(self, painter):
        """Draw a semi-transparent piece at the hovered position if valid."""
        if self.hover_row == -1 or self.hover_col == -1:
            return

        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        center_x = self.top_left_x + self.hover_col * square_width
        center_y = self.top_left_y + self.hover_row * square_height
        size = min(square_width, square_height) * 0.9

        self.transparent_piece_color = self.player_turn

        pixmap = (
            self.white_stone_pixmap
            if self.transparent_piece_color == 1
            else self.black_stone_pixmap
        )

        x = center_x - size / 2
        y = center_y - size / 2

        painter.setOpacity(0.5)  # Semi-transparent effect
        painter.drawPixmap(int(x), int(y), int(size), int(size), pixmap)
        painter.setOpacity(1.0)  # Reset opacity to normal

    def handleCapturedPieces(self, captured_positions):
        """
        Animate captured pieces. First, move them slightly upward.
        Then, slide them out of the board.

        :param captured_positions: List of (row, col) tuples representing captured pieces.
        """
        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        # Prepare captured pieces for animation
        for row, col in captured_positions:
            piece = self.boardArray[row][col]
            center_x = self.top_left_x + col * square_width
            center_y = self.top_left_y + row * square_height
            self.captured_pieces.append({"piece": piece, "x": center_x, "y": center_y})

        # Trigger the upward animation
        self.animateCapturedPiecesUpward()

    def animateCapturedPiecesUpward(self):
        """Animate captured pieces upward slightly."""
        for captured in self.captured_pieces:
            captured["y"] -= 10  # Move upward slightly

        self.update()  # Redraw the board to reflect changes

        # After a short delay, slide pieces out of the board
        self.capture_timer.start(700)  # 1 second delay before sliding out

    def slideOutCapturedPieces(self):
        """Animate all captured pieces sliding out of the board over 0.5 seconds."""
        self.animation_step = 0
        total_steps = 200  # Divide the 0.5 seconds into 100 steps (5ms per step)

        def animateStep():
            """Perform one step of the sliding animation."""
            for captured in self.captured_pieces:
                captured["x"] += self.square_side / total_steps  # Gradual movement

            self.update()  # Redraw to reflect changes
            self.animation_step += 1

            if self.animation_step >= total_steps:
                self.capture_timer.stop()
                self.captured_pieces = []  # Clear captured pieces after animation

        # Set up the timer for the animation
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(animateStep)
        self.capture_timer.start(5)  # Update every 5ms (100 frames for 0.5 seconds)

    def drawCapturedPieces(self, painter):
        """Draw captured pieces at their current positions."""
        for captured in self.captured_pieces:
            pixmap = (
                self.white_stone_pixmap
                if self.player_turn == 1
                else self.black_stone_pixmap
            )
            if pixmap.isNull():
                continue

            size = min(self.squareWidth(), self.squareHeight()) * 0.9
            x = captured["x"] - size / 2
            y = captured["y"] - size / 2

            painter.drawPixmap(int(x), int(y), int(size), int(size), pixmap)

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
        star_positions = [(3, 3), (7, 3), (5, 5), (3, 7), (7, 7)]

        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        painter.setBrush(Qt.GlobalColor.black)
        painter.setPen(Qt.GlobalColor.black)

        for row, col in star_positions:
            x = self.top_left_x + (col - 1) * square_width
            y = self.top_left_y + (row - 1) * square_height
            size = (
                min(square_width, square_height) * 0.1
            )  # Star size as a fraction of square size
            painter.drawEllipse(
                int(x - size / 2), int(y - size / 2), int(size), int(size)
            )

    def print_player_turn(self):
        color = "white" if self.player_turn == 1 else "black"
        print(f"Player {self.player_turn} ({color}) turn")

    def sizeHint(self):
        return QSize(800, 800)
