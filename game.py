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

    def score_board(self, state, team_names, teams):
        width = ShuffleBoardGame.width
        length = ShuffleBoardGame.length
        scores = {}
        for team in team_names:
            scores[team] = 0
        for i in range(state.num_pucks):
            pos = state.get_x(i)
            if pos[0] > 0 and pos[0] < width:
                if pos[1] <= length:
                    if pos[1] >= length * (7/8):
                        scores[teams[i]] += 4
                    elif pos[1] >= length * (6/8):
                        scores[teams[i]] += 3
                    elif pos[1] >= length * (5/8):
                        scores[teams[i]] += 2
                    elif pos[1] >= length * (4/8):
                        scores[teams[i]] += 1
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
    p1 = players.QSimPlayer()
    p2 = players.RandomPlayer()
    teams = {} # This should only be used for visualization
    for i in range(num_pucks):
        if i % 2 == 0:
            teams[i] = 'red'
            state, xs = game.sim_turn(state, i, *p1.calc_move(0, game, state, i))
        else:
            teams[i] = 'blue'
            state, xs = game.sim_turn(state, i, *p2.calc_move(1, game, state, i))
        sim.animate(xs, game.dt, teams)
    
    print(game.score_board(state, ['red', 'blue'], teams))

    plt.close('all')
    r = 0.02936875
    fig, ax = plt.subplots(figsize=(12, 6))
    for puck in range(state.num_pucks):
        pos = state.get_x(puck)
        if puck in teams.keys():
            ax.add_artist(plt.Circle(pos, r, color=teams[puck]))
        else:
            ax.add_artist(plt.Circle(pos, r, color="pink"))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.axis('square')
    plt.xlim([0, 1])
    plt.ylim([0, 2])
    length = ShuffleBoardGame.length
    plt.axhline(y=length * (7/8))
    plt.axhline(y=length * (6/8))
    plt.axhline(y=length * (5/8))
    plt.axhline(y=length * (4/8))
    plt.show()
    