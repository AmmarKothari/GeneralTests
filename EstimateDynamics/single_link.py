import pdb

import matplotlib.pyplot as plt
import numpy as np

from integration_methods import rk4

G = -9.8 # m/s^2

class SingleLink(object):
    def __init__(self):
        self.q = [0, 0] # theta, theta_dot
        self.l = 1
        self.torque_lims = [-1, 1] # this is the js torque
        # can this mass also be one or does it need to be scaled by torques?
        self.m = 1
        self.I = 1/3 * self.m * self.l**2
        self.b = 1.0 # damping


    def dynamics(self, t, q, u):
        q_dot = np.zeros(2)
        q_dot[0] = q[1]
        # I * qdd + b*qd + m*g*l*sin(theta) = u
        q_dot[1] = self.I**-1 - self.b*q[1] + self.m * G * self.l * np.sin(q[0]) + u
        return q_dot

class SingleLinkVis(SingleLink):
    def __init__(self):
        super(SingleLink, self).__init__()

    # def plot(self):

if __name__ == '__main__':
    sl = SingleLink()
    dt = 1e-3
    t_end = 5
    q0 = [np.pi/2, 0.0]
    q = np.array(q0)
    t_current = 0
    qs = []
    qs.append(q0)
    u = 0.1
    while t_current < t_end:
        t_current, q = rk4(t_current, q, u, dt, sl.dynamics)

        qs.append(q)
    pdb.set_trace()


