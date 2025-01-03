from piece import Piece
from copy import deepcopy
from PyQt6.QtWidgets import QMessageBox

class GameLogic:

    __ko_state = False  # ko state round before, init as false
    __prisoners_p1 = 0  # Counter for Player 1's prisoners
    __prisoners_p2 = 0  # Counter for Player 2's prisoners
    __territory_p1 = 0  # Territory count for player 1
    __territory_p2 = 0  # Territory cunt for player 2
    __score_p1 = 0
    __score_p2 = 0
    __game_state = 0  # not playing
    __final_board = None
    __handicap_player = None

    def __init__(self, board: list[list[Piece]], handicaps):
        """
        Init of game logic, komi is the point compensation given to white player as it's black who start here 6.5 as we follow japanese rules
        """
        self.board = board  # saving the pointing to the board
        self.__top = len(board)  # getting the max index + 1
        self.__init_handicap(handicaps)

    def __init_handicap(self, handicaps):

        self.__komi_p1 = float(handicaps["komi"])
        self.__komi_p2 = 0

        if handicaps["player"] != 0 and handicaps["type"]:
            if handicaps["type"] == "Points" and handicaps["player"] == 1:
                self.__komi_p1 += float(handicaps["value"])
            elif handicaps["type"] == "Points" and handicaps["player"] == 2:
                self.__komi_p2 += float(handicaps["value"])
            elif handicaps["type"] == "Pieces":
                self.__game_state = -1
                self.__handicap_player = handicaps["player"]
                self.handicap_pieces_left = int(handicaps["value"])

    def start(self):
        self.__game_state = 1
        self.__count_prisoner = True
        return self.__handicap_player

    def stop(self):
        self.__game_state = 0
        self.__count_prisoner = False

    def game_state(self):
        return self.__game_state

    def check_piece_placement(self, new_piece: Piece, hover=False):
        """
        Function that will check a movement's validity
        """
        is_in_ko = self.ko(new_piece)  # check if the move create a ko or is in a ko

        # check if move is suicidal
        if self.suicide(new_piece):
            return False

        # check if the last move created a ko and if this move is in the ko
        if self.__ko_state and is_in_ko:
            return False

        # if the move is ko or if  last move is ko changing ko state
        if (is_in_ko or self.__ko_state) and not hover:
            self.__ko_state = not self.__ko_state

        return True

    def ko(self, new_piece: Piece):
        """
        Implementation of the ko rule
        """

        board_game = deepcopy(self.board)
        row, col = new_piece.position
        board_game[row][col] = new_piece
        deleted_pieces = []

        for dir_row, dir_col in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]:
            new_row, new_col = row + dir_row, col + dir_col
            if self.existing_position(new_row, new_col):
                oposite_piece = board_game[new_row][new_col]
                if oposite_piece.state == 3 - new_piece.state:
                    res = self.is_encircled(oposite_piece, game_board=board_game)
                    if res[0] and len(res[1]) == 1:
                        del_piece = deepcopy(res[1][0])
                        deleted_pieces.append(del_piece)
                        del_row, del_col = del_piece.position
                        board_game[del_row][del_col] = Piece(0, del_row, del_col)

        if len(deleted_pieces) != 1:
            return False
        else:
            piece = deleted_pieces[0]
            old_row, old_col = piece.position
            board_game[old_row][old_col] = piece
            for dir_row, dir_col in [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ]:
                new_row, new_col = old_row + dir_row, old_col + dir_col
                if self.existing_position(new_row, new_col):
                    oposite_piece = board_game[new_row][new_col]
                    if oposite_piece.state == 3 - piece.state:
                        res = self.is_encircled(oposite_piece, game_board=board_game)
                        if res[0] and len(res[1]) == 1:
                            del_piece = deepcopy(res[1][0])
                            del_row, del_col = del_piece.position
                            board_game[del_row][del_col] = Piece(0, del_row, del_col)

            new_board_state = tuple(
                tuple(piece.state for piece in row) for row in board_game
            )
            old_board_state = tuple(
                tuple(piece.state for piece in row) for row in self.board
            )

            if new_board_state == old_board_state:
                # print("KO") # debug
                return True
            else:
                return False

    def suicide(self, new_piece: Piece):
        """
        Check if the movement is suicidal
        """

        # check if piece or territory is encircled
        if self.is_encircled(new_piece)[0]:
            row, col = new_piece.position

            game_board = deepcopy(self.board)  # do not work coz copy pointer ?
            game_board[row][col] = new_piece

            # if encircled place hypothetically the piece to check if it encircled at least one opposite piece that encircle it now
            for dir_row, dir_col in [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ]:
                new_row, new_col = row + dir_row, col + dir_col
                if self.existing_position(new_row, new_col):
                    oposite_piece = self.board[new_row][new_col]
                    if oposite_piece.state == 3 - new_piece.state:
                        if self.is_encircled(oposite_piece, game_board=game_board)[0]:
                            return False

            # if not encircling at least one piece with the new piece then suicidal move
            return True

        else:
            return False

    def is_encircled(self, piece: Piece, visited=None, visit=None, game_board=None):
        """
        Say if a piece or a group of piece is encircled, may return the encircled pieces to delete them
        """

        oposite_state = 3 - piece.state
        state = piece.state

        if visited == None:
            visited = set()

        if visit == None:
            visit = set()

        if piece in visited:
            raise ValueError(f"{piece} cannot be in visited")

        if game_board == None:
            game_board = deepcopy(self.board)  # do not work coz copy pointer ?

        visited.add(piece)

        row, col = piece.position
        encircled = 0
        same_color = 0
        for dir_row, dir_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dir_row, col + dir_col
            if self.existing_position(new_row, new_col):
                neighbor_piece = game_board[new_row][new_col]
                if neighbor_piece.state == 0:
                    return False, [p for p in visited]
                elif neighbor_piece.state == oposite_state:
                    encircled += 1
                elif neighbor_piece.state == state:
                    if neighbor_piece in visit or neighbor_piece in visited:
                        continue
                    else:
                        visit.add(neighbor_piece)
            else:
                encircled += 1

        if encircled == 4:
            return True, [p for p in visited]
        else:
            if not visit == set():
                neighbor_piece = visit.pop()
                game_board[row][col] = piece
                return self.is_encircled(neighbor_piece, visited, visit, game_board)
            else:
                return True, [p for p in visited]

    def existing_position(self, row, col):
        """
        Function that check if the given position exist on the board
        """
        if 0 <= col < self.__top and 0 <= row < self.__top:
            return True
        else:
            return False

    def capturing_territory(self, new_piece: Piece):
        """
        Capture pieces encircled implementation
        """

        captured_positions = []

        row, col = new_piece.position

        for dir_row, dir_col in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]:
            new_row, new_col = row + dir_row, col + dir_col
            if self.existing_position(new_row, new_col):
                oposite_piece = deepcopy(self.board[new_row][new_col])
                if oposite_piece.state == 3 - new_piece.state:
                    res = self.is_encircled(oposite_piece)
                    if res[0]:
                        for captured_piece in res[1]:
                            captured_row, captured_col = captured_piece.position
                            captured_positions.append((captured_row, captured_col))

                            if captured_piece.state == 1 and self.__count_prisoner:
                                self.__prisoners_p2 += 1
                            elif captured_piece.state == 2 and self.__count_prisoner:
                                self.__prisoners_p1 += 1

                            self.board[captured_row][captured_col].change_state(0)

        return captured_positions

    def count_prisoners(self):
        """Count the number of prisoners for each player"""
        return self.__prisoners_p1, self.__prisoners_p2

    def count_territory(self):
        """Count the territory for each player"""
        territory_p1 = 0
        territory_p2 = 0
        visited = set()

        if sum([sum([p.state for p in row]) for row in self.board]) < 3 and self.__game_state == 1:
            return 0, 0

        for row in range(self.__top):
            for col in range(self.__top):
                piece = deepcopy(self.board[row][col])
                if piece.state == 0 and (row, col) not in visited:
                    territory, owner = self.flood_fill_territory(row, col, visited)
                    if owner == 1:
                        territory_p1 += territory
                    elif owner == 2:
                        territory_p2 += territory

        self.__territory_p1 = territory_p1
        self.__territory_p2 = territory_p2

        return territory_p1, territory_p2

    def flood_fill_territory(self, row, col, visited):
        """Flood fill algorithm to count territory"""
        territory = 0
        owner = None
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            territory += 1
            for dir_row, dir_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = r + dir_row, c + dir_col
                if self.existing_position(new_row, new_col):
                    neighbor_piece = self.board[new_row][new_col]
                    if neighbor_piece.state == 0:
                        stack.append((new_row, new_col))
                    elif neighbor_piece.state != 0 and owner is None:
                        owner = neighbor_piece.state
                    elif neighbor_piece.state != 0 and owner != neighbor_piece.state:
                        owner = 0  # Mixed territory

        return territory, owner

    def territory_scoring(self):
        """
        Counting point based on the Japanese go's rules (territory scoring)
        """

        self.__score_p1 = self.__territory_p1 - self.__prisoners_p2 + self.__komi_p1
        self.__score_p2 = self.__territory_p2 - self.__prisoners_p1 + self.__komi_p2

        return self.__score_p1, self.__score_p2

    def area_scoring(self):
        """
        Scocring based on the Chinese rules (area scoring)
        """

        self.__score_p1 = self.__territory_p1 + self.__komi_p1
        self.__score_p2 = self.__territory_p2 + self.__komi_p2

        for row in self.board:
            for piece in row:
                if piece.state == 1:
                    self.__score_p1 += 1
                elif piece.state == 2:
                    self.__score_p2 += 1

        return self.__score_p1, self.__score_p2

    def end_game(self):
        """
        Implementation of the end game before territory scoring
        """
        self.__game_state = 2
        self.__count_prisoner = True

        if self.__final_board:
            for row in range(self.__top):
                for col in range(self.__top):
                    final_state = self.__final_board[row][col].state
                    actual_piece = self.board[row][col]
                    if actual_piece.state != final_state:
                        actual_piece.change_state(final_state)

        message_box = QMessageBox()
        message_box.setWindowTitle("Ending game mode")
        message_box.setText(
            "Starting the ending game mode, select the dead piece to remove."
        )
        message_box.exec()

    def remove_dead_pieces_box(
        self, player_turn, selected_pieces: list[tuple[int, int]]
    ):
        """
        Function to remove dead pieces
        """

        selected_piece = Piece(3 - player_turn)

        msg_txt = f"{selected_piece.name} player, do you concede that the selected pieces are dead?"  # maybe permit the name of the player if ther is one

        message_box = QMessageBox()
        message_box.setWindowTitle("Concede Pieces")
        message_box.setText(msg_txt)
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        response = message_box.exec()

        if response == QMessageBox.StandardButton.Yes:
            for captured_row, captured_col in selected_pieces:

                if player_turn == 1:
                    self.__prisoners_p1 += 1
                elif player_turn == 2:
                    self.__prisoners_p2 += 1

                self.board[captured_row][captured_col].change_state(0)

            return selected_pieces

        elif response == QMessageBox.StandardButton.No:
            return

    def select_neighboor_piece(self, piece: Piece, visited_positions=None, visit=None):
        """
        Return a list of all the neighboor piece of the same state
        """

        if visited_positions == None:
            visited_positions = set()

        if visit == None:
            visit = set()

        visited_positions.add(piece.position)

        row, col = piece.position

        for dir_row, dir_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dir_row, col + dir_col
            if self.existing_position(new_row, new_col):
                neighbor_piece = deepcopy(self.board[new_row][new_col])
                if (
                    neighbor_piece.state == piece.state
                    and neighbor_piece.position not in visited_positions
                ):
                    visit.add(neighbor_piece)

        if len(visit) > 0:
            neighbor_piece = visit.pop()
            return self.select_neighboor_piece(neighbor_piece, visited_positions, visit)

        return [pos for pos in visited_positions]

    def dead_pieces_debate(self):
        self.__game_state = 1
        self.__final_board = deepcopy(self.board)
        self.__count_prisoner = False

        message_box = QMessageBox()
        message_box.setWindowTitle("Dispute mode")
        message_box.setText("Starting the dispute mode.")
        message_box.exec()
