import matplotlib.pyplot as plt
import numpy as np
import time
from random import seed

import sim
import players

class ShuffleBoardGame:
    length = 2.4384
    width = 0.4064

    def __init__(self):
        self.dt = 0.01
        self.sim = sim.ShuffleBoardSim(self.dt)

    def sim_turn(self, state, puck, x_pos, y_pos, x_vel, y_vel): # Similar to take turn but doesn't update board state   
        original_x = state.get_all(puck)
        state.set_all(puck, np.array([x_pos, y_pos, x_vel, y_vel]))
        xf, xs = self.sim.simulate(state, self)
        state.set_all(puck, original_x)
        return xf, xs

    def score_board(self, state):
        width = ShuffleBoardGame.width
        length = ShuffleBoardGame.length
        sl_3 = length * (15/16)
        sl_2 = length * (14/16)
        sl_1 = length * (10/16)
        scores = [0,0]
        y_pos = [[sl_1],[sl_1]]

        for i in range(state.num_pucks):
            pos = state.get_x(i)
            if pos[0] >= 0 and pos[0] <= width and pos[1] <= length and pos[1] > sl_1:
                if i % 2 == 0:
                    y_pos[0].append(pos[1])
                else:
                    y_pos[1].append(pos[1])
        if max(y_pos[0]) > max(y_pos[1]):
            winner = 0
        else:
            winner = 1
        all_winning_y_pos = [pos for pos in y_pos[winner] if pos > max(y_pos[1 - winner])]
        for winning_y_pos in all_winning_y_pos:
            if winning_y_pos > sl_3:
                scores[winner] += 3
            elif winning_y_pos > sl_2:
                scores[winner] += 2
            else:
                scores[winner] += 1
        return scores

    def display_board(self):
        fig, ax = plt.subplots(figsize=(3, 6))
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
    num_pucks = 8 # Num pucks total
    game = ShuffleBoardGame()
    state = sim.State(num_pucks)
    p1 = players.SimPlayer(game)
    p2 = players.SimPlayer(game)
    seed(42)
    # p2 = players.RandomPlayer()
    teams = {} # This should only be used for visualization
    for i in range(num_pucks):
        if i % 2 == 0:
            teams[i] = 'red'
            # state, xs = game.sim_turn(state, i, game.width/2,0.12,0.15,1)
            state, xs = game.sim_turn(state, i, *p1.calc_move(0, state, i))
        else:
            teams[i] = 'blue'
            # state, xs = game.sim_turn(state, i, 0,0,0,0)
            state, xs = game.sim_turn(state, i, *p2.calc_move(1, state, i))
        sim.animate(xs, game.dt, game.length, game.width, teams)
    
    print(game.score_board(state))

    plt.close('all')
    r = 0.02936875
    fig, ax = plt.subplots(figsize=(3, 6))
    for puck in range(state.num_pucks):
        pos = state.get_x(puck)
        if puck in teams.keys():
            ax.add_artist(plt.Circle(pos, r, color=teams[puck]))
        else:
            ax.add_artist(plt.Circle(pos, r, color="pink"))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.axis('square')
    plt.xlim([0, game.width])
    plt.ylim([0, game.length])
    length = ShuffleBoardGame.length
    plt.axhline(y=length * (15/16))
    plt.axhline(y=length * (14/16))
    plt.axhline(y=length * (10/16))
    plt.show()
    