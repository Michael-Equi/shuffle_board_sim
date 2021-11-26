import itertools
import time

import matplotlib.pyplot as plt
import numpy as np

GRAVITY = 9.8
KINETIC_FRICTION = 0.1


class State:

    @classmethod
    def from_vec(cls, v):
        s = cls(len(v) // 4)
        s._state = v
        return s

    def __init__(self, num_pucks):
        self.num_pucks = num_pucks
        self._state = np.zeros(self.num_pucks * 4)

    def __mul__(self, other):
        return State.from_vec(self._state * other)

    def __add__(self, other):
        assert self.num_pucks == other.num_pucks
        return State.from_vec(self._state + other.get_state())

    def __sub__(self, other):
        assert self.num_pucks == other.num_pucks
        return State.from_vec(self._state - other.get_state())

    def __str__(self):
        s = ""
        for puck in range(self.num_pucks):
            x = self.get_x(puck)
            dx = self.get_x_dot(puck)
            s += f"puck #{puck}\n   x: {x[0]}\n   y: {x[1]}\n  dx: {dx[0]}\n  dy: {dx[1]}\n"
        return s

    def __array__(self):
        return self._state

    def get_x(self, puck):
        return self._state[puck * 2:puck * 2 + 2]

    def get_x_dot(self, puck):
        return self._state[self.num_pucks * 2 + puck * 2:self.num_pucks * 2 + puck * 2 + 2]

    def set_x(self, puck, value):
        self._state[puck * 2:puck * 2 + 2] = value

    def set_x_dot(self, puck, value):
        self._state[self.num_pucks * 2 + puck * 2:self.num_pucks * 2 + puck * 2 + 2] = value

    def get_state(self):
        return np.copy(self._state)


class ShuffleBoardSim:
    def __init__(self, dt, min_velocity=1e-2):
        # board dimensions (meters)
        self.length = 2
        self.width = 0.5

        # mass in kg
        self.m = 0.345
        # radius in m
        self.r = 0.02936875

        self.dt = dt
        self.min_velocity = min_velocity

    def simulate(self, initial_state: State, tol=1e-5):

        # for friction models see http://www.mate.tue.nl/mate/pdfs/11194.pdf
        def closed_loop(x: State):
            x_dot = State(x.num_pucks)

            def get_friction(v, m):
                friction = m * GRAVITY * KINETIC_FRICTION
                if np.linalg.norm(v) > 0:
                    f = - friction * v / np.linalg.norm(v)
                    return f
                return np.zeros_like(v)

            for puck in range(x.num_pucks):
                x_dot.set_x(puck, x.get_x_dot(puck))
                x_dot.set_x(puck, np.where(abs(x_dot.get_x(puck)) < self.min_velocity, 0, x_dot.get_x(puck)))
                x_dot.set_x_dot(puck, get_friction(x_dot.get_x(puck), self.m))

            for pair in itertools.combinations(range(x.num_pucks), 2):
                # Collision physics
                p = x.get_x(pair[0]) - x.get_x(pair[1])
                distance_btw_pucks = np.linalg.norm(p)
                distance_btw_pucks_after_step = np.linalg.norm((x.get_x(pair[0]) + x_dot.get_x(pair[0]) * self.dt) - (
                        x.get_x(pair[1]) + x_dot.get_x(pair[1]) * self.dt))
                if distance_btw_pucks < 2 * self.r and (distance_btw_pucks - distance_btw_pucks_after_step) > 0:
                    v_p2 = p @ x_dot.get_x(pair[0]) / (p @ p) * p
                    v_p1 = x_dot.get_x(pair[0]) - v_p2
                    x_dot.set_x_dot(pair[0], (v_p1 - x_dot.get_x(pair[0])) / self.dt)
                    x_dot.set_x_dot(pair[1], (v_p2 - x_dot.get_x(pair[1])) / self.dt)

            return x_dot

        xs = [initial_state]
        while True:
            x_dot = closed_loop(xs[-1])
            xs.append(xs[-1] + x_dot * self.dt)
            if np.linalg.norm(xs[-1] - xs[-2]) < tol:
                return xs[-1], xs


def visualize(state, fig, ax, teams={}, r=0.02936875):
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


def animate(states, dt, teams={}, r=0.02936875):
    fig, ax = plt.subplots(figsize=(12, 6))
    for state in states:
        visualize(state, fig, ax, teams, r)
        plt.pause(dt)
        ax.clear()


def visualize_traj(states, fig, ax, teams={}, r=0.02936875):
    states_arr = np.array([np.array(state) for state in states])
    for puck in range(states[0].num_pucks):
        ax.plot(states_arr[:, puck * 2], states_arr[:, puck * 2 + 1])
        pos = states[-1].get_x(puck)
        if puck in teams.keys():
            ax.add_artist(plt.Circle(pos, r, color=teams[puck]))
        else:
            ax.add_artist(plt.Circle(pos, r, color="pink"))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.axis('square')
    plt.xlim([0, 1])
    plt.ylim([0, 2])


if __name__ == '__main__':
    dt = 0.01
    board = ShuffleBoardSim(dt)
    initial_state = State(6)

    teams = {
        0: 'red',
        1: 'blue',
        2: 'red',
        3: 'blue',
        4: 'red',
        5: 'blue',
    }

    initial_state.set_x(0, np.array([0.48, 0.1]))
    initial_state.set_x_dot(0, np.array([0, 1.03]))
    initial_state.set_x(1, np.array([0.5, 1]))
    initial_state.set_x_dot(1, np.array([0, 0]))
    initial_state.set_x(2, np.array([0.6, 1.2]))
    initial_state.set_x_dot(2, np.array([0, 0]))
    initial_state.set_x(3, np.array([0.73, 1.4]))
    initial_state.set_x_dot(3, np.array([0, 0]))
    initial_state.set_x(4, np.array([0.5, 1.6]))
    initial_state.set_x_dot(4, np.array([0, 0]))
    initial_state.set_x(5, np.array([0.5, 1.8]))
    initial_state.set_x_dot(5, np.array([0, 0]))

    start = time.time()
    xf, xs = board.simulate(initial_state)
    print("Solve time:", time.time() - start)

    print(xf)
    # fig, ax = plt.subplots(figsize=(12, 6))
    # visualize_traj(xs, fig, ax, teams)
    # plt.show()
    animate(xs, dt, teams)
