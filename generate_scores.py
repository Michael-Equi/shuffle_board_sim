import csv
import numpy as np
import multiprocessing as mp
import time

import sim
import game
import players

def run_game():
    num_pucks = 6 # Num pucks total
    game_inst = game.ShuffleBoardGame()
    state = sim.State(num_pucks)
    p1 = players.QSimPlayer()
    p2 = players.QSimPlayer()
    teams = {} # This should only be used for visualization
    
    for i in range(num_pucks):
        if i % 2 == 0:
            teams[i] = 0
            state, _ = game_inst.sim_turn(state, i, *p1.calc_move(0, game_inst, state, i))
        else:
            teams[i] = 1
            state, _ = game_inst.sim_turn(state, i, *p2.calc_move(1, game_inst, state, i))

    scores = []
    score = game_inst.score_board(state, [0,1], teams)
    score_diff = score[0] - score[1]
    for i in range(num_pucks):
        scores.extend(state.get_x(i))
    scores.append(score_diff)

    return scores


if __name__ == '__main__':
    filename = 'scores2.csv'
    num_games = 10000
    scores = []

    with mp.Pool(processes=12) as pool:
        results = []
        for _ in range(num_games):
            results.append(pool.apply_async(run_game))
        pool.close()
        for r in results:
            scores.append(r.get())
        pool.join()

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(scores)
    