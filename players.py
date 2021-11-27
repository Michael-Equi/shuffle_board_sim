from random import uniform

class Player:
    def calc_move(self, board):
        raise NotImplementedError("Player should be subclassed")

class RandomPlayer(Player):
    def calc_move(self, board):
        return 0.5, 0.1, uniform(-0.25, 0.25), uniform(0.4, 1.2)