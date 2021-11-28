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
        self.dt = 0.01
        self.sim = sim.ShuffleBoardSim(self.dt)

    def sim_turn(self, state, puck, x_pos, y_pos, x_vel, y_vel): # Similar to take turn but doesn't update board state   
        original_x = state.get_all(puck)
        state.set_all(puck, np.array([x_pos, y_pos, x_vel, y_vel]))
        xf, xs = self.sim.simulate(state)
        state.set_all(puck, original_x)
        return xf, xs

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
    num_pucks = 6 # Num pucks total
    game = ShuffleBoardGame()
    state = sim.State(num_pucks)
    p1 = players.RandomPlayer()
    p2 = players.RandomPlayer()
    teams = {} # This should only be used for visualization
    for i in range(num_pucks):
        if i % 2 == 0:
            teams[i] = 'red'
            state, xs = game.sim_turn(state, i, *p1.calc_move(state))
        else:
            teams[i] = 'blue'
            state, xs = game.sim_turn(state, i, *p2.calc_move(state))
        print(state)
    sim.animate(xs, game.dt, teams)
    # print(game.score_board())
    # game.display_board()
    