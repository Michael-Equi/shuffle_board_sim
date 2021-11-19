import matplotlib.pyplot as plt
import numpy as np
import time
import scipy.integrate

GRAVITY = 9.8
KINETIC_FRICTION = 0.1


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
        def closed_loop(x, t):
            x_dot = np.zeros(x.shape)
            x_dot[:2] = x[2:]
            friction = self.m * GRAVITY * KINETIC_FRICTION

            f = - friction * x[2:] / np.linalg.norm(x[2:])

            # a = 1e2
            # x_dot[2:] = f * np.abs(((np.e ** (a * x[2:]) - np.e ** -(a * x[2:])) / (np.e ** (a * x[2:]) + np.e ** -(a * x[2:]))))
            # x_dot[2:] = friction * np.sign(x[2:]) * np.abs(x[2:])
            # x_dot[2:] = -friction * np.sign(x[2:])
            x_dot[2:] = np.where(x[2:] < 1e-4, 0, f)
            # print(x_dot[2:])
            return x_dot

        t = np.arange(0.0, end_time, 0.01)
        return scipy.integrate.odeint(closed_loop, x0, t)


if __name__ == '__main__':
    board = ShuffleBoardSim()
    start = time.time()
    x = board.simulate(np.array([0.5, 0.1, 0.3, 1.0]), 5)
    print(time.time() - start)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x[:, 0], x[:, 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.axis('square')
    plt.xlim([0, 1])
    plt.ylim([0, 2])
    plt.show()
