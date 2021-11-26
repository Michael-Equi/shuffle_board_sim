import matplotlib.pyplot as plt
import numpy as np
import time
import scipy.integrate

GRAVITY = 9.8
KINETIC_FRICTION = 0.1

called = False


class ShuffleBoardSim:
    def __init__(self):
        # board dimensions (meters)
        self.length = 2
        self.width = 0.5

        # mass in kg
        self.m = 0.345
        # radius in m
        self.r = 0.02936875

    def simulate(self, x0, end_time):

        # for friction models see http://www.mate.tue.nl/mate/pdfs/11194.pdf
        def closed_loop(t, x):
            global called
            # x1 = x[0:2]
            # x2 = x[2:4]
            # x1_dot = x[4:6]
            # x2_dot = x[6:8]

            x_dot = np.zeros(x.shape)
            # x_dot[:2] = x[2:]
            x_dot[0:2] = np.where(abs(x[4:6]) < 1e-2, 0, x[4:6])
            x_dot[2:4] = np.where(abs(x[6:8]) < 1e-2, 0, x[6:8])

            # x_dot[0:2] = np.where(abs(x_dot[0:2]) < 1e-2, 0, x_dot[0:2])
            # x_dot[2:4] = np.where(abs(x_dot[2:4]) < 1e-2, 0, x_dot[2:4])

            def get_friction(v, m):
                friction = m * GRAVITY * KINETIC_FRICTION
                if np.linalg.norm(v) > 0:
                    f = - friction * v / np.linalg.norm(v)
                    return f
                return np.zeros_like(v)

            # friction of puck 1
            f1 = get_friction(x_dot[0:2], self.m)
            x_dot[4:6] = f1

            # friction of puck 2
            f2 = get_friction(x_dot[2:4], self.m)
            x_dot[6:8] = f2

            # Collision physics
            p = x[0:2] - x[2:4]
            distance_btw_pucks = np.linalg.norm(p)
            distance_btw_pucks_after_step = np.linalg.norm((x[0:2] + x_dot[0:2]*0.05) - (x[2:4] + x_dot[2:4]*0.05))
            if distance_btw_pucks < 2 * self.r and (distance_btw_pucks - distance_btw_pucks_after_step) >  0:
                # if not called:
                v_p2 = p @ x_dot[0:2] / (p @ p) * p
                v_p1 = x_dot[0:2] - v_p2
                # x_dot[0:2] = 0
                # x_dot[2:4] = 0, 3
                # x_dot[4:] = 0
                x_dot[4:6] = (v_p1 - x_dot[0:2])/0.05
                x_dot[6:8] = (v_p2 - x_dot[2:4])/0.05
                    # called = True

                # import sys
                # sys.exit()
                # print(x_dot)

            # a = 1e2
            # x_dot[2:] = f * np.abs(((np.e ** (a * x[2:]) - np.e ** -(a * x[2:])) / (np.e ** (a * x[2:]) + np.e ** -(a * x[2:]))))
            # x_dot[2:] = friction * np.sign(x[2:]) * np.abs(x[2:])
            # x_dot[2:] = -friction * np.sign(x[2:])
            # x_dot[2:] = np.where(x[2:] < 1e-4, 0, f)
            # print(x_dot[2:])
            return x_dot



        dt = 0.05
        xs = [x0]
        last_xdot = np.zeros_like(xs)
        for _ in range(int(end_time / dt)):
            x_dot = closed_loop(0, xs[-1])
            xs.append(xs[-1] + x_dot * dt)
            if np.linalg.norm(last_xdot - x_dot) < 1e-3:
                return np.array(xs)
        return np.array(xs)

        # t = np.arange(0.0, end_time, 0.001)
        # return scipy.integrate.solve_ivp(
        #     closed_loop,
        #     (0, end_time),
        #     x0,
        #     t_eval=t,
        #     max_step=1e-4,
        #     atol=1e10,
        #     rtol=1e10)
        # return scipy.integrate.odeint(closed_loop, x0, t, hmax=1e-4)
        # return scipy.integrate.quad(closed_loop, x0, t)



if __name__ == '__main__':
    board = ShuffleBoardSim()
    start = time.time()
    # x1, y1, x2, y2, x1_dot, y1_dot, x2_dot, y2_dot
    # x = board.simulate(np.array([0.5, 0.1, 0.5, 1, 0.3, 1.0, 0.3, 0.3]), 5)
    now = time.time()
    x = board.simulate(np.array([0.5, 0.1, 0.48, 1, 0, 1.0, 0, 0]), 100)
    print(time.time() - now)

    # x = board.simulate(np.array([0.5, 0.1, 0.5, 1, 0, 1.0, 0, 0]), 5).y.T
    # x = board.simulate(np.array([0.5, 0.1, 0.3, 1.0]), 5)
    # print(time.time() - start)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x[:, 0], x[:, 1])
    ax.plot(x[:, 2], x[:, 3])
    ax.add_artist(plt.Circle((x[-1, 0], x[-1, 1]), 0.02936875))
    ax.add_artist(plt.Circle((x[-1, 2], x[-1, 3]), 0.02936875, color='red'))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.axis('square')
    plt.xlim([0, 1])
    plt.ylim([0, 2])
    plt.show()
