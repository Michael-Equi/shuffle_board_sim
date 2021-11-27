import matplotlib.pyplot as plt
import numpy as np
import time
from random import uniform

import sim
import players

class ShuffleBoardGame:
    length = 2
    width = 1

    def __init__(self):
        self.sim = sim.ShuffleBoardSim(ShuffleBoardGame.length, ShuffleBoardGame.width)
        self.board = [] # Pucks stored as an array of (x, y) tuples
        self.turn_time = 5

    def take_turn(self, team, x_pos, y_pos, x_vel, y_vel):
        puck_x, puck_y = self.sim_turn(x_pos, y_pos, x_vel, y_vel)
        self.board.append((puck_x, puck_y, team))

    def sim_turn(self, x_pos, y_pos, x_vel, y_vel): # Similar to take turn but doesn't update board state
        puck_trajectory = self.sim.simulate(np.array([x_pos, y_pos, x_vel, y_vel]), self.turn_time)
        puck_x_final = puck_trajectory[-1,0]
        puck_y_final = puck_trajectory[-1,1]
        return puck_x_final, puck_y_final

    def score_board(self):
        scores = [0,0]
        for puck in self.board:
            if puck[0] > 0 and puck[0] < ShuffleBoardGame.width:
                if puck[1] <= ShuffleBoardGame.length:
                    if puck[1] >= 1.75:
                        scores[puck[2]] += 4
                    elif puck[1] >= 1.5:
                        scores[puck[2]] += 3
                    elif puck[1] >= 1.25:
                        scores[puck[2]] += 2
                    elif puck[1] >= 1.0:
                        scores[puck[2]] += 1
        return scores

    def display_board(self):
        fig, ax = plt.subplots(figsize=(6, 6))
        for puck in self.board:
            if puck[2] == 0:
                ax.plot(puck[0], puck[1], 'bo')
            if puck[2] == 1:
                ax.plot(puck[0], puck[1], 'ro')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.axis('square')
        plt.xlim([0, ShuffleBoardGame.width])
        plt.ylim([0, ShuffleBoardGame.length])
        plt.show()


if __name__ == '__main__':
    num_pucks = 3 # Num pucks per team
    game = ShuffleBoardGame()
    p1 = players.RandomPlayer()
    p2 = players.RandomPlayer()
    for _ in range(num_pucks):
        game.take_turn(0, *p1.calc_move(game.board))
        game.take_turn(1, *p2.calc_move(game.board))
    print(game.score_board())
    game.display_board()
    