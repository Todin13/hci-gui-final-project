from piece import Piece

class GameLogic:
    print("Game Logic Object Created")
    # TODO add code here to manage the logic of your game

    def __init__(self, board: list(list(Piece))):
        self.board = board # saving the pointing to the board
        self.score = 0 # init the score

    def check_piece_placement(self, new_piece: Piece):
        """
        Function that will check the validity of a movement
        """
        pass

    def ko(self):
        """
        Implementation of the ko rule
        """
        pass

    def suicide(self):
        """
        Implementation of the suicide rule
        """
        pass

    def encirclement_one_piece(self):
        """
        Delete encircled piece
        """
        pass

    def encirclement_multiple_pieces(self):
        """
        Delete multipled encircled pieces
        """
        pass
