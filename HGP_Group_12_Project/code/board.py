from PyQt6.QtWidgets import QFrame, QDialog
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap
from piece import Piece
from game_logic import GameLogic
from copy import deepcopy
from PyQt6.QtWidgets import QMessageBox
from handicap import HandicapDialog


class Board(QFrame):
    updateTimerSignal = pyqtSignal(int)
    clickLocationSignal = pyqtSignal(str)

    boardWidth = 9  # 9x9 Goban
    boardHeight = 9

    def __init__(self, parent=None, scoreBoard=None):
        super().__init__(parent)
        self.margin = 40
        self.scoreBoard = scoreBoard  # Store the scoreBoard reference
        self.pending_moves = []  # List to track all pending moves
        self.current_pending_index = -1  # Index of the currently viewed pending move

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

        self.handicap = {"player": 0, "type": None, "value": None, "komi": "6.5"}

    def initBoard(self):
        """Initializes the board."""
        self.boardArray = [
            [Piece(0, r, c) for c in range(self.boardWidth)]
            for r in range(self.boardHeight)
        ]
        self.ask_handicap()
        self.logic = GameLogic(self.boardArray, self.handicap)
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

        if hasattr(self, "highlight_positions") and self.highlight_positions:
            self.highlightPieces(painter, self.highlight_positions)

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

            if self.logic.game_state() == 1 and piece.state == 0:

                new_piece = Piece(self.player_turn, row, col)

                if self.logic.check_piece_placement(new_piece):
                    # Set the pending move
                    if self.pending_moves:
                        if (
                            row == self.pending_moves[self.current_pending_index]["row"]
                            and col
                            == self.pending_moves[self.current_pending_index]["col"]
                        ):
                            self.confirmMove()
                            return

                    self.pending_moves.append(
                        {"row": row, "col": col, "piece": new_piece}
                    )
                    self.current_pending_index = len(self.pending_moves) - 1
                    self.update()

            elif self.logic.game_state() == 2 and piece.state == 3 - self.player_turn:

                neighbor_pieces_positions = self.logic.select_neighboor_piece(
                    deepcopy(piece)
                )

                # TODO implement glowing piece like surround them in blue ?
                self.triggerHighlight(neighbor_pieces_positions)

                captured_positions = self.logic.remove_dead_pieces_box(
                    self.player_turn, neighbor_pieces_positions
                )

                if captured_positions:
                    self.setMouseTracking(False)
                    self.handleCapturedPieces(captured_positions)
                    self.setMouseTracking(True)

                    self.update_turn()

                else:
                    self.logic.dead_pieces_debate()

    def PreviousPendingMove(self):
        """Go to the previous pending move."""
        if not self.pending_moves:
            return

        if self.current_pending_index > 0:
            self.current_pending_index -= 1

        self.update()

    def NextPendingMove(self):
        """Go to the next pending move."""
        if not self.pending_moves:
            return

        if self.current_pending_index < len(self.pending_moves) - 1:
            self.current_pending_index += 1

        self.update()

    def confirmMove(self):
        """Confirm the pending move and finalize the turn."""
        if self.current_pending_index == -1:
            return  # No pending move to confirm

        # Apply the currently displayed move to the board
        move = self.pending_moves[self.current_pending_index]

        row, col = move["row"], move["col"]
        piece = self.boardArray[row][col]
        piece.change_state(self.player_turn)  # Finalize the move

        # Handle capturing logic
        captured_positions = self.logic.capturing_territory(move["piece"])

        if captured_positions:
            self.handleCapturedPieces(captured_positions)

        # Log the click and update the board
        clickLoc = f"({row}, {col})"
        print("mousePressEvent() -  Location :" + clickLoc)
        self.clickLocationSignal.emit(clickLoc)

        self.update_turn()

    def mouseMoveEvent(self, event):
        """Track the mouse position and determine the hovered position."""
        if self.logic.game_state() == 1:
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
        if self.hover_row == -1 or self.hover_col == -1 or self.logic.game_state() != 1:
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
        self.player_turn = 2  # black start
        self.conssecutive_passing_turn = 0
        self.update()

    def start(self):
        self.resetGame()
        self.handicap_piece_player = self.logic.start()

        if self.handicap_piece_player:
            self.player_turn = self.handicap_piece_player

            message_box = QMessageBox()
            message_box.setWindowTitle("Placing Handicap Stone")
            message_box.setText(
                f"{Piece(self.player_turn).name} need to place {self.logic.handicap_pieces_left}, before starting the game."
            )
            message_box.exec()

        else:
            message_box = QMessageBox()
            message_box.setWindowTitle("Starting Game")
            message_box.setText("No handicap stones, starting the game.")
            message_box.exec()

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
        # Draw the pending move, if any
        if self.pending_moves:
            row, col = (
                self.pending_moves[self.current_pending_index]["row"],
                self.pending_moves[self.current_pending_index]["col"],
            )
            pixmap = (
                self.white_stone_pixmap
                if self.player_turn == 1
                else self.black_stone_pixmap
            )
            center_x = self.top_left_x + col * square_width
            center_y = self.top_left_y + row * square_height
            size = min(square_width, square_height) * 0.9
            x = center_x - size / 2
            y = center_y - size / 2

            painter.setOpacity(0.8)  # Semi-transparent effect
            painter.drawPixmap(int(x), int(y), int(size), int(size), pixmap)
            painter.setOpacity(1.0)  # Reset opacity

    def triggerHighlight(self, positions):
        """Trigger a new paint event specifically for highlighting."""
        self.highlight_positions = positions
        self.repaint()
        self.highlight_positions = None

    def highlightPieces(self, painter, positions):
        """Highlight pieces at the given list of (row, col) positions."""
        square_width = self.square_side / (self.boardWidth - 1)
        square_height = self.square_side / (self.boardHeight - 1)

        highlight_color = QColor(255, 255, 0, 128)  # Yellow with transparency
        brush = QBrush(highlight_color)
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        for row, col in positions:
            # Calculate the center of the intersection
            center_x = self.top_left_x + col * square_width
            center_y = self.top_left_y + row * square_height
            size = min(square_width, square_height) * 1.0  # Slightly larger highlight

            x = center_x - size / 2
            y = center_y - size / 2

            # Draw the highlight circle
            painter.drawEllipse(int(x), int(y), int(size), int(size))

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

    def update_turn(self, pass_turn=False):

        if pass_turn:
            self.conssecutive_passing_turn += 1
        else:
            self.conssecutive_passing_turn = 0  # reset if not passing turn

        if self.conssecutive_passing_turn >= 2:
            if self.logic.game_state() == 1:
                self.conssecutive_passing_turn = 0
                self.logic.end_game()
            elif self.logic.game_state() == 2:
                self.conssecutive_passing_turn = 0
                self.game_ended()

        if self.handicap_piece_player:

            if self.logic.handicap_pieces_left > 1:

                self.logic.handicap_pieces_left -= 1

            elif self.logic.handicap_pieces_left == 1:

                self.logic.handicap_pieces_left = None
                self.handicap_piece_player = None

                message_box = QMessageBox()
                message_box.setWindowTitle("Starting Game")
                message_box.setText(
                    f"{Piece(self.player_turn).name} player finished placing his handicap pieces.\nNow starting the game."
                )
                message_box.exec()

                self.player_turn = 2

        else:
            # Alternate the player turn
            self.player_turn = 3 - self.player_turn

            # Update the turn display
            self.scoreBoard.updateTurn(self.player_turn)

            # Update prisoners and territory
            prisoners_p1, prisoners_p2 = self.logic.count_prisoners()
            territory_p1, territory_p2 = self.logic.count_territory()
            self.scoreBoard.updatePrisoners(prisoners_p1, prisoners_p2)
            self.scoreBoard.updateTerritory(territory_p1, territory_p2)

        # Clear pending move and update board
        self.pending_moves.clear()
        self.current_pending_index = -1
        self.update()

    def game_ended(self):
        self.logic.stop()

        white_score, black_score = self.logic.territory_scoring()

        if white_score > black_score:
            msg = f"White player win by {white_score - black_score} points.\nWhite points: {white_score}\nBlack points: {black_score}"
        elif black_score > white_score:
            msg = f"Black palyer win by {black_score - white_score} points.\nWhite points: {white_score}\nBlack points: {black_score}"
        else:
            msg = "Equality"

        message_box = QMessageBox()
        message_box.setWindowTitle("Winner")
        message_box.setText(msg)

        message_box.exec()

    def ask_handicap(self):
        """
        Aking box to choose handicaps
        """

        dialog = HandicapDialog(self.handicap)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.handicap = dialog.get_results()
        else:
            self.handicap = {
                "player": 0,
                "type": None,
                "value": None,
                "komi": "6.5",
            }
