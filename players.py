import math
import copy
import time
from random import uniform

import numpy as np
import multiprocessing as mp

import sim

class Player:
    def __init__(self, game):
        self.game = game
        self.player_sim = sim.ShuffleBoardSim(0.01)
        self.start_x = game.width/2
        self.start_y = 0.1

    def calc_move(self, player, state, puck, use_mp=True):
        raise NotImplementedError("Player should be subclassed")

class RandomPlayer(Player):
    def calc_move(self, player, state, puck, use_mp=True):
        return self.start_x, self.start_y, uniform(-0.25, 0.25), uniform(1.0, 1.1)

class SimPlayer(Player):
    def calc_move(self, player, state, puck, use_mp=True):
        start = time.time()
    
        shots = []
        for x_pos in [self.game.width/4, self.game.width/2, 3*self.game.width/4]:
            for x_vel in np.arange(-0.15, 0.15, .01):
                for y_vel in np.arange(1.0, 1.3, .02):
                    shots.append((x_pos, x_vel, y_vel))

        shot_scores = np.empty(len(shots))
        result_shots = np.empty(len(shots), dtype='f,f,f')
        with mp.Pool(processes=12) as pool:
            results = []
            for shot in shots:
                copied_state = copy.deepcopy(state)
                copied_state.set_all(puck, np.array([shot[0], self.start_y, shot[1], shot[2]]))
                results.append((pool.apply_async(self.player_sim.simulate, args=(copied_state, self.game)), shot))

            pool.close()
            
            for idx, r in enumerate(results):
                xf = r[0].get()[0]
                score = self.game.score_board(xf)
                shot_scores[idx] = score[0] - score[1]
                result_shots[idx] = r[1]

            np.random.seed(1)
            if player == 1:
                shot_scores = -shot_scores
            best_shot = result_shots[np.random.choice(np.flatnonzero(shot_scores == shot_scores.max()))]

            pool.join()


        print("Shot Time: " + str(time.time() - start))
        # print("Predicted Score: " + str(shot_scores.max()))
        # print("Velocity: " + str(best_vel))

        return best_shot[0], self.start_y, best_shot[1], best_shot[2]

# class QSimPlayer(Player):
#     def calc_move(self, player, game, state, puck, use_mp=True):
#         start = time.time()
#         model = load_model('q_model')
    
#         vels = []
#         for x_vel in np.arange(-0.25, 0.25, .05):
#             for y_vel in np.arange(0.4, 1.2, .05):
#                 vels.append((x_vel, y_vel))

#         player_sim = sim.ShuffleBoardSim(0.01)

#         if use_mp:
#             with mp.Pool(processes=12) as pool:
#                 results = []
#                 for vel in vels:
#                     copied_state = copy.deepcopy(state)
#                     copied_state.set_all(puck, np.array([0.5, 0.1, vel[0], vel[1]]))
#                     results.append((pool.apply_async(player_sim.simulate, args=(copied_state,)), vel)) # Result and vel tuple

#                 pool.close()

#                 all_new_locations = []
#                 result_vels = []
#                 for r in results:
#                     xf = r[0].get()[0]
                    
#                     new_locations = []
#                     for i in range(6):
#                         new_locations.extend(xf.get_x(i))
#                     all_new_locations.append(new_locations)
#                     result_vels.append(r[1])

#                 shot_scores = model.predict(all_new_locations).flatten()
#                 if player == 1:
#                     shot_scores = -shot_scores
#                 best_vel = result_vels[shot_scores.argmax()]

#                 pool.join()
#         else:
#             all_new_locations = []
#             for vel in vels:
#                 copied_state = copy.deepcopy(state)
#                 copied_state.set_all(puck, np.array([0.5, 0.1, vel[0], vel[1]]))

#                 xf, _ = player_sim.simulate(copied_state)
#                 new_locations = []
#                 for i in range(6):
#                     new_locations.extend(xf.get_x(i))
#                 all_new_locations.append(new_locations)

#             shot_scores = model.predict(all_new_locations).flatten()
#             if player == 1:
#                 shot_scores = -shot_scores
#             best_vel = vels[shot_scores.argmax()]


#         # print("Shot Time: " + str(time.time() - start))
#         # print("Predicted Score: " + str(shot_scores.max()))
#         # print("Velocity: " + str(best_vel))

#         return 0.5, 0.1, best_vel[0], best_vel[1]