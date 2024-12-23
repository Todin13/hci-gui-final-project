class Piece(object):
    """
    Piece implementation
    No piece state = 0
    White piece state = 1
    Black piece state = 2
    
    """

    def __init__(self, state: int, row: int | None = None, col: int | None = None):
        self.state = state
        self.position = (row, col)
        self.__allPieces = {0: "No", 1: "White", 2: "Black"}
        self.name = self.__allPieces[self.state]

    def change_state(self, new_state: int):
        if new_state != self.state:
            self.state = new_state
            self.name = self.__allPieces[self.state] 
        else:
            raise ValueError(f"Cannot change {self.name} piece in position {self.position} to {self.__allPieces[new_state]} piece as it's the same.")

    def __str__(self):
        if self.position != (None, None):
            return f"{self.name} Piece at position {self.position}"
        else:
            return f"{self.name} Piece "
    
