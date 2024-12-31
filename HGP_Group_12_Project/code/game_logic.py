class GameLogic:
    print("Game Logic Object Created")
    # TODO add code here to manage the logic of your game

    def capture_pieces(self, row, col):
        captured = []
        to_visit = [(row, col)]
        visited = set()
        liberties = 0

        while to_visit:
            r, c = to_visit.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            piece = self.boardArray[r][c]
            if piece.state == 0:
                liberties += 1
            else:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.boardHeight and 0 <= nc < self.boardWidth:
                        if (nr, nc) not in visited:
                            to_visit.append((nr, nc))

        if liberties == 0:
            for r, c in visited:
                if self.boardArray[r][c].state != 0:
                    captured.append((r, c))

        return captured

    def is_game_over(self):
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                if self.boardArray[row][col].state == 0:
                    return False
        return True

    def count_score(self):
        black_score = 0
        white_score = 0
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                piece = self.boardArray[row][col]
                if piece.state == 1:
                    white_score += 1
                elif piece.state == 2:
                    black_score += 1
        return black_score, white_score