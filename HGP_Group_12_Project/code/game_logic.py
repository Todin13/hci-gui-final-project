from piece import Piece
from copy import deepcopy

class GameLogic:
    print("Game Logic Object Created")
    # TODO add code here to manage the logic of your game

    def __init__(self, board: list[list[Piece]]):
        self.board = board  # saving the pointing to the board
        self.score = 0  # init the score
        self.top = len(board)  # getting the max index + 1
        self.ko_state = False  # ko state round before, init as false
        self.prisoners_p1 = 0  # Counter for Player 1's prisoners
        self.prisoners_p2 = 0  # Counter for Player 2's prisoners

    def check_piece_placement(self, new_piece: Piece, hover=False):
        """
        Function that will check a movement's validity
        """
        is_in_ko = self.ko(new_piece)  # check if the move create a ko or is in a ko

        # check if move is suicidal
        if self.suicide(new_piece):
            return False

        # check if the last move created a ko and if this move is in the ko
        if self.ko_state and is_in_ko:
            return False

        # if the move is ko or if  last move is ko changing ko state
        if (is_in_ko or self.ko_state) and not hover:
            self.ko_state = not self.ko_state

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
        if 0 <= col < self.top and 0 <= row < self.top:
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
                oposite_piece = self.board[new_row][new_col]
                if oposite_piece.state == 3 - new_piece.state:
                    res = self.is_encircled(oposite_piece)
                    if res[0]:
                        for captured_piece in res[1]:
                            captured_row, captured_col = captured_piece.position
                            captured_positions.append((captured_row, captured_col))

                            if captured_piece.state == 1:
                                print("capture un prisonnier blanc")
                                self.prisoners_p2 += 1
                            elif captured_piece.state == 2:
                                print("capture un prisonnier noir")
                                self.prisoners_p1 += 1

                            self.board[captured_row][captured_col].change_state(0)


        return captured_positions

    def count_prisoners(self):
        """Count the number of prisoners for each player"""
        return self.prisoners_p1, self.prisoners_p2

    def count_territory(self):
        """Count the territory for each player"""
        territory_p1 = 0
        territory_p2 = 0
        visited = set()

        for row in range(self.top):
            for col in range(self.top):
                piece = self.board[row][col]
                if piece.state == 0 and (row, col) not in visited:
                    territory, owner = self.flood_fill_territory(row, col, visited)
                    if owner == 1:
                        territory_p1 += territory
                    elif owner == 2:
                        territory_p2 += territory

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
