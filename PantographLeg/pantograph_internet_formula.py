import math
import numpy as np
import pdb
import matplotlib.pyplot as plt
from unittest import mock
import sympy


def _linear_offset(p_start, theta, l):
    x = p_start[0] + l * math.cos(theta)
    y = p_start[1] + l * math.sin(theta)
    return [x, y]


class PantographConfig:
    def __init__(self, theta_m, la_b, la_1, la_2, lb_1, lb_2):
        self.theta_m = theta_m
        self.la_b = la_b
        self.la_1 = la_1
        self.la_2 = la_2
        self.lb_1 = lb_1
        self.lb_2 = lb_2


class Pantograph:
    def __init__(self, config, is_symbolic=False):
        self.config = config
        self.is_symbolic = is_symbolic
        self.p1 = None

    def set_body_pos(self, x, y):
        self.p1 = [x, y]

    @property
    def p5(self):
        return _linear_offset(self.p1, self.config.theta_m, self.config.la_b)

    def forward(self, q):
        # Calculation taken from here: http://hades.mech.northwestern.edu/index.php/Design_and_Control_of_a_Pantograph_Robot
        theta_1 = q[0]
        theta_4 = q[1]
        p2, p4 = self._mid_joints(theta_1, theta_4)
        p3 = self._get_end_point(p2, p4)
        l3_solved_length = math.sqrt((p4[0] - p3[0]) ** 2 + (p4[1] - p3[1]) ** 2)
        if not self.is_symbolic and not np.isclose(l3_solved_length, self.config.lb_2):
            print('Solution is not consistent for [{:.3f}, {:.3f}]. L3 error: {:.3f}'.format(theta_1, theta_4,
                                                                                             l3_solved_length - self.config.lb_2))
        return p3

    def _get_end_point(self, p2, p4):
        l2_4 = math.sqrt((p2[0] - p4[0]) ** 2 + (p2[1] - p4[1]) ** 2)
        if not self.is_symbolic and np.isclose(l2_4, 0.0):
            raise Exception('Not a valid configuration')
        l2_h = 0.5 * l2_4 + (self.config.la_2 ** 2 - self.config.lb_2 ** 2) / (2 * l2_4)
        ratio_dist = l2_h / l2_4
        ph = [p2[0] + ratio_dist * (p4[0] - p2[0]),
              p2[1] + ratio_dist * (p4[1] - p2[1])]
        l3_h = math.sqrt(self.config.la_2 ** 2 - l2_h ** 2)
        # TODO: Add a check here to ensure that the angle is never greater than pi
        p3 = [ph[0] - (l3_h / l2_4) * (p4[1] - p2[1]),
              ph[1] + (l3_h / l2_4) * (p4[0] - p2[0])]
        return p3

    def _mid_joints(self, theta_1, theta_4):
        p2 = _linear_offset(self.p1, theta_1, self.config.la_1)
        p4 = _linear_offset(self.p5, theta_4, self.config.lb_1)
        return p2, p4

    def inverse(self, x, y):
        l13 = math.hypot(self.p1[0] - x, self.p1[1] - y)
        l53 = math.hypot(self.p5[0] - x, self.p5[1] - y)
        try:
            beta_a = math.acos(
                (self.config.la_1 ** 2 + l13 ** 2 - self.config.la_2 ** 2) / (2 * self.config.la_1 * l13))
        except ValueError:
            pdb.set_trace()
            raise Exception('B_a outside of operating range: [{:.3f}, {:.3f}]'.format(x, y))
        alpha_a = math.atan2(y - self.p1[1], (x - self.p1[0]))
        try:
            beta_b = math.acos(
                (self.config.lb_1 ** 2 + l53 ** 2 - self.config.lb_2 ** 2) / (2 * self.config.lb_1 * l53))
        except ValueError:
            pdb.set_trace()
            raise Exception('B_b outside of operating range: [{:.3f}, {:.3f}'.format(x, y))
        alpha_b = math.atan2(y - self.p5[1], -(x - self.p5[0]))
        q1 = alpha_a + beta_a
        q2 = math.pi - (alpha_b + beta_b)
        return [q1, q2]

    def plot_pose(self, q):
        end_pos = self.forward(q)
        p2, p4 = self._mid_joints(q[0], q[1])
        plt.plot(*self.p1, 'ro')
        plt.plot(*self.p5, 'ko')
        _plot_link(self.p1, p2)
        _plot_link(self.p5, p4)
        _plot_link(p2, end_pos)
        _plot_link(p4, end_pos)
        plt.plot(end_pos[0], end_pos[1], 'gx')


class EEFixedPantograph(Pantograph):
    def __init__(self, config):
        super(EEFixedPantograph, self).__init__(config)
        self.p1 = [0.0, 0.0]
        self.ee = None

    def set_foot_pos(self, x, y):
        self.ee = [x, y]

    def forward(self, q):
        """Returns the body position, not the end point position."""
        self.p1 = [0.0, 0.0]  # TODO: Just pass in p1 to plotting function
        p3 = super(EEFixedPantograph, self).forward(q)
        # Because the cosys of for this model is 180 from the normal panto so need to rotate.
        p3[0] *= -1
        p3[1] *= -1
        self.p1 = [self.ee[0] - p3[0], self.ee[1] - p3[1]]
        return self.p1

    def inverse(self, x, y):
        self.p1 = [0.0, 0.0]
        # Foot position to put body in the desired pose
        # Relative position and then rotating 180 around body position
        x_foot_effective = -(self.ee[0] - x)
        y_foot_effective = -(self.ee[1] - y)
        q = super(EEFixedPantograph, self).inverse(x_foot_effective, y_foot_effective)
        return q

    def plot_pose(self, q):
        body_pos = self.forward(q)
        p2, p4 = self._mid_joints(q[0] + math.pi, q[1] + math.pi)
        _plot_link(self.p1, p2)
        _plot_link(self.p5, p4)
        _plot_link(p2, self.ee)
        _plot_link(p4, self.ee)
        plt.plot(*self.p1, 'ro', alpha=0.1)
        plt.plot(*self.p5, 'ko', alpha=0.1)
        plt.plot([self.p1[0], self.p5[0]], [self.p1[1], self.p5[1]], 'k', alpha=0.5)
        plt.plot(self.ee[0], self.ee[1], 'gx')


class SymbolicPantograph(Pantograph):
    """The coordinate system is pi rotated from parent class."""

    def __init__(self, config):
        with mock.patch('math.cos', sympy.cos), mock.patch('math.sin', sympy.sin):
            super(SymbolicPantograph, self).__init__(config, is_symbolic=True)

    def forward(self, q):
        self.q = q
        for i, angle in enumerate(self.q):
            if not (-math.pi < angle <= math.pi):
                raise Exception("q_{} out of range".format(i))
        with mock.patch('math.cos', sympy.cos), mock.patch('math.sin', sympy.sin), mock.patch('math.sqrt', sympy.sqrt):
            self.forward_eq = super(SymbolicPantograph, self).forward(q)
            return self.forward_eq

    def get_jacobian(self, q):
        with mock.patch('math.cos', sympy.cos), mock.patch('math.sin', sympy.sin), mock.patch('math.sqrt', sympy.sqrt):
            self.jacobian = sympy.Matrix(self.forward_eq).jacobian(q)
            return self.jacobian


def _plot_link(p_start, p_end, style='b-'):
    plt.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]], style, alpha=0.1)
    plt.plot(p_end[0], p_end[1], 'bo', alpha=0.2)

# symbolic solving
# p1x, p1y, theta_m, la_b, la_1, la_2, lb_1, lb_2 = sympy.symbols('p1x p1y theta_m la_b la_1 la_2 lb_1 lb_2')
# config = PantographConfig([p1x, p1y], theta_m, la_b, la_1, la_2, lb_1, lb_2)
# panto = SymbolicPantograph(config)
# q1, q2 = sympy.symbols('q1 q2')
# forward_eq = panto.forward([q1, q2])
# pdb.set_trace()


# L1 = 1
# L2 = 2
# L4 = 1
# L3 = 2
#
# L5 = 1.0
# theta_m = 0.0
# p1 = [0.0, 0.0]
# config = PantographConfig(p1, theta_m, L5, L1, L2, L4, L3)
# panto = Pantograph(config)

# Forward kinematics plot
# plt.ion()
# for q1 in np.linspace(math.pi / 2, 3 * math.pi / 4, 5):
#     for q2 in np.linspace(math.pi / 2, 3 * math.pi / 4, 5):
#         panto.plot_pose([q1, q2])
#         plt.draw()
#         plt.pause(0.2)
# plt.show(block=True)


# Inverse kinematics plot
# plt.ion()
# for x in np.linspace(-1, 1, 5):
#     for y in np.linspace(2, 3, 5):
#         try:
#             q = panto.inverse(x, y)
#         except:
#             continue
#         print('xy: [{:.3f}, {:.3f}] q:({:.3f}, {:.3f})'.format(x, y, q[0], q[1]))
#         panto.plot_pose(q)
#         plt.plot(x, y, 'rs')
#         plt.draw()
#         plt.pause(0.2)
# plt.show(block=True)
