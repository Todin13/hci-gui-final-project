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

    def check_piece_placement(self, new_piece: Piece):
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
        if is_in_ko or self.ko_state:
            self.ko_state = not self.ko_state

        return True

    def ko(self, new_piece: Piece):
        """
        Implementation of the ko rule
        """
        pass

    def suicide(self, new_piece: Piece):
        """
        Check if the movement is suicidal
        """

        # check if piece or territory is encircled
        if self.is_encircled(new_piece):
            row, col = new_piece.position

            game_board = deepcopy(self.board)  # do not work coz copy pointer ?
            game_board[row][col] = new_piece

            # if encircled place hipothecally the piece to check if it encircled at least one opposite piece that encirle it now
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
                        if self.is_encircled(oposite_piece, game_board=game_board):
                            return False

            # if not encircling at least one piec on the with the new piece then suicidal move
            return True

        else:
            return False

    def is_encircled(self, piece: Piece, visited=None, visit=None, game_board=None):
        """
        Say if a piece or a group of piece is encircled, may return the encircled pieced to delete them
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
                    return False
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
            return True
        else:
            if not visit == set():
                neighbor_piece = visit.pop()
                game_board[row][col] = piece
                return self.is_encircled(neighbor_piece, visited, visit, game_board)
            else:
                return True

    def existing_position(self, row, col):
        """
        Function that check if the given position exist on the board
        """
        if 0 <= col < self.top and 0 <= row < self.top:
            return True
        else:
            return False
