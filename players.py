import copy
import time
from random import uniform

import numpy as np
import multiprocessing as mp
from scipy.ndimage import gaussian_filter

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
    
        poss_x_pos = np.array([self.game.width/4, self.game.width/2, 3*self.game.width/4])
        poss_x_vel = np.arange(-0.15, 0.15, .01)
        poss_y_vel = np.arange(1.0, 1.3, .02)

        shots = []
        for x_pos in poss_x_pos:
            for x_vel in poss_x_vel:
                for y_vel in poss_y_vel:
                    shots.append((x_pos, x_vel, y_vel))

        shot_scores = np.empty((len(poss_x_pos), len(poss_x_vel), len(poss_y_vel)))
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
                x_pos_loc = np.searchsorted(poss_x_pos, r[1][0])
                x_vel_loc = np.searchsorted(poss_x_vel, r[1][1])
                y_vel_loc = np.searchsorted(poss_y_vel, r[1][2])
                shot_scores[x_pos_loc,x_vel_loc,y_vel_loc] = score[0] - score[1]
                # result_shots[idx] = r[1]

            np.random.seed(1)
            if player == 1:
                shot_scores = -shot_scores

            shot_scores = gaussian_filter(shot_scores, sigma=1, mode='nearest')

            max_shot_val = np.max(shot_scores)
            max_shot_choices = (shot_scores == max_shot_val).nonzero()
            choice = np.random.randint(len(max_shot_choices[0]))
            chosen_x_pos = poss_x_pos[max_shot_choices[0][choice]]
            chosen_x_vel = poss_x_vel[max_shot_choices[1][choice]]
            chosen_y_vel = poss_y_vel[max_shot_choices[2][choice]]
            best_shot = (chosen_x_pos, chosen_x_vel, chosen_y_vel)

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