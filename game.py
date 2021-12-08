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

    def sim_turn(self, state, puck, x_pos, y_pos, x_vel, y_vel):
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
                y_pos[i%2].append(pos[1])
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

    def board_heuristics(self, state):
        num_pucks = [0,0]
        alt_score = [0,0]

        width = ShuffleBoardGame.width
        length = ShuffleBoardGame.length
        sl_3 = length * (15/16)
        sl_2 = length * (14/16)
        sl_1 = length * (10/16)
        
        for i in range(state.num_pucks):
            pos = state.get_x(i)
            if pos[0] >= 0 and pos[0] <= width and pos[1] <= length and pos[1] > 0:
                num_pucks[i%2] += 1
                if pos[1] > sl_3:
                    alt_score[i%2] += 3
                elif pos[1] > sl_2:
                    alt_score[i%2] += 2
                elif pos[1] > sl_1:
                    alt_score[i%2] += 1

        return num_pucks, alt_score

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

    def run_sim_game(self):
        num_pucks = 8 # Num pucks total
        state = sim.State(num_pucks)
        p1 = players.SimPlayer(self)
        p2 = players.SimPlayer(self)
        # seed(42)
        # p2 = players.RandomPlayer()
        teams = {} # This should only be used for visualization
        for i in range(num_pucks):
            if i % 2 == 0:
                teams[i] = 'red'
                # state, xs = game.sim_turn(state, i, game.width/2,0.1,0.0,1.15)
                state, xs = self.sim_turn(state, i, *p1.calc_move(0, state, i))
            else:
                teams[i] = 'blue'
                # state, xs = game.sim_turn(state, i, 0,0,0,0)
                state, xs = self.sim_turn(state, i, *p2.calc_move(1, state, i))
            sim.animate(xs, self.dt, self.length, self.width, teams)
        
        print(self.score_board(state))
        print(self.board_heuristics(state))

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
        plt.xlim([0, self.width])
        plt.ylim([0, self.length])
        plt.axhline(y=self.length * (15/16))
        plt.axhline(y=self.length * (14/16))
        plt.axhline(y=self.length * (10/16))
        plt.show()

    def run_real_game(self):
        num_pucks = 8 # Num pucks total
        state = sim.State(num_pucks)
        ai = players.SimPlayer(self)

        teams = {}
        for i in range(num_pucks):
            if i % 2 == 0:
                teams[i] = 'red'
                input("Press enter once human shot is complete")
            else:
                teams[i] = 'blue'
                robo_shot = ai.calc_move(1, state, i)
                perform_shot(robo_shot) # TODO: Create perform_shot to make robot shoot based on input
            state = get_real_board_state() # TODO: Create get_real_board_state to return a state based on irl board
        
        score = self.score_board(state)
        print("Human Score: " + str(score[0]))
        print("Robot Score: " + str(score[1]))

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
        plt.xlim([0, self.width])
        plt.ylim([0, self.length])
        plt.axhline(y=self.length * (15/16))
        plt.axhline(y=self.length * (14/16))
        plt.axhline(y=self.length * (10/16))
        plt.show()

if __name__ == '__main__':
    game = ShuffleBoardGame()
    # game.run_real_game()
    game.run_sim_game()
    