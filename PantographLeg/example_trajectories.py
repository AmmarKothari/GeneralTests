import pantograph_internet_formula as pf
import numpy as np
import matplotlib.pyplot as plt

L1 = 1
L2 = 2
L4 = 1
L3 = 2

L5 = 1.0
theta_m = 0.0
config = pf.PantographConfig(theta_m, L5, L1, L2, L4, L3)
panto = pf.Pantograph(config)
panto.set_body_pos(0.0, 0.0)


def plot_trajectory(xs, ys):
    f, axs = plt.subplots(3, 1)
    qs = []
    solved_xys = []
    for x, y in zip(xs, ys):
        qs.append(panto.inverse(x, y))
        solved_xys.append(panto.forward(qs[-1]))
    solved_xs = [p[0] for p in solved_xys]
    solved_ys = [p[1] for p in solved_xys]
    import pdb; pdb.set_trace()
    axs[0].set_title('Position')
    axs[0].plot(solved_xs, solved_ys, 'ks')
    axs[0].plot(xs, ys, 'rx')
    axs[0].set_xlim([-2, 2])
    axs[1].set_title('q0')
    axs[1].plot([q[0] for q in qs], 'bo-')
    axs[2].set_title('q1')
    axs[2].plot([q[1] for q in qs], 'bo-')
    f, axs = plt.subplots(1, 1)
    plt.ion()
    for q, xy in zip(qs, solved_xys):
        panto.plot_pose(q)
        plt.plot(xy[0], xy[1], 'ks')
        plt.pause(0.1)
    plt.axis('equal')
    plt.show(block=True)


# ----------------------
# Forward Trajectories
# ----------------------
# theta_1s = np.linspace(np.pi, 3 * np.pi / 4, 10)
# theta_2s = np.linspace(np.pi / 4, np.pi / 2, 10)
# for theta_1 in theta_1s:
#     for theta_2 in theta_2s:
#         panto.plot_pose([theta_1, theta_2])
# plt.show()

# ----------------------
# Inverse Trajectories
# ----------------------
# Horizontal line
# xs = np.linspace(-1, 1, 20)
# ys = np.linspace(2, 2, 20)

# Vertical line
xs = np.linspace(0, 0, 20)
ys = np.linspace(1.5, 2.5, 20)

# Circle
# theta = np.linspace(0, 2 * np.pi)
# xs = np.cos(theta)
# ys = np.sin(theta)*0.5 + 1.5

# Sin
# xs = np.linspace(-np.pi, np.pi) * 0.5
# ys = np.sin(2 * xs)*0.5 + 1.5

plot_trajectory(xs, ys)