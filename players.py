import math
import copy
import time
from random import uniform

import numpy as np
import multiprocessing as mp
from keras.models import load_model

import sim

class Player:
    def calc_move(self, player, game, state, puck):
        raise NotImplementedError("Player should be subclassed")

class RandomPlayer(Player):
    def calc_move(self, player, game, state, puck):
        return 0.5, 0.1, uniform(-0.25, 0.25), uniform(0.4, 1.2)

class QSimPlayer(Player):
    def calc_move(self, player, game, state, puck):
        start = time.time()
        model = load_model('q_model')
    
        vels = []
        for x_vel in np.arange(-0.25, 0.25, .05):
            for y_vel in np.arange(0.4, 1.2, .05):
                vels.append((x_vel, y_vel))

        player_sim = sim.ShuffleBoardSim(0.01)

        with mp.Pool(processes=12) as pool:
            results = []
            for vel in vels:
                copied_state = copy.deepcopy(state)
                copied_state.set_all(puck, np.array([0.5, 0.1, vel[0], vel[1]]))
                results.append((pool.apply_async(player_sim.simulate, args=(copied_state,)), vel)) # Result and vel tuple

            pool.close()

            all_new_locations = []
            result_vels = []
            for r in results:
                xf = r[0].get()[0]
                
                new_locations = []
                for i in range(6):
                    new_locations.extend(xf.get_x(i))
                all_new_locations.append(new_locations)
                result_vels.append(r[1])

            shot_scores = model.predict(all_new_locations).flatten()
            if player == 1:
                shot_scores = -shot_scores
            best_vel = result_vels[shot_scores.argmax()]

            pool.join()

        print("Shot Time: " + str(time.time() - start))
        print("Predicted Score: " + str(shot_scores.max()))
        print("Velocity: " + str(best_vel))

        return 0.5, 0.1, best_vel[0], best_vel[1]