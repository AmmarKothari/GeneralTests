import pydy
from sympy import symbols
import sympy.physics.mechanics as me
import pdb
# --------------------------------------------
# This is for two links in 2 dimensions
# Can only rotate round z-axis

# ------------------
# Create Model
# ------------------


n = 2

# Generalized Coordinates
thetax = me.dynamicsymbols('thetax:{}'.format(n)) # x
thetay = me.dynamicsymbols('thetay:{}'.format(n)) # y
thetaz = me.dynamicsymbols('thetaz:{}'.format(n)) # z


# Generalized Speeds
omegax = me.dynamicsymbols('omegax:{}'.format(n))
omegay = me.dynamicsymbols('omegay:{}'.format(n))
omegaz = me.dynamicsymbols('omegaz:{}'.format(n))

# Each link is a cylinder rotating about its end
l = symbols('l:{}'.format(n))
m_link = symbols('M:{}'.format(n))
Ixx = symbols('Ixx:{}'.format(n))
Iyy = symbols('Iyy:{}'.format(n))
Izz = symbols('Izz:{}'.format(n))

# Gravity
g = symbols('g')

# Applied Torques
t = symbols('t:{}'.format(n))

# Inertial frame of base link
# assume can't track or slide
I = me.ReferenceFrame('I')

# Reference frame for each link
# pdb.set_trace()
A = me.ReferenceFrame('A')
A.orient(I, 'Space', [thetaz[0], 0, 0], 'ZXY')
B = me.ReferenceFrame('B')
B.orient(I, 'Space', [thetaz[1], 0, 0], 'ZXY')

# define the kinematic differential equations
# speeds equal the time derivatives of the generalized coords
# What does that mean?
kinematic_differentials = []
# for each link
# the speed and the derivative of position should be equal -- makes sense
for i in range(n):
    kinematic_differentials.append(omegaz[i] - thetaz[i].diff())


# Angular velocities
A.set_ang_vel(I, omegaz[0] * I.z)
B.set_ang_vel(I, omegaz[0] * I.z)

# Set base point as not moving
O = me.Point('O')
O.set_vel(I, 0)

# set the location of the joints
P1 = O.locatenew('P1', -l[0]*A.y)
P2 = P1.locatenew('P1', -l[1]*B.y)

# calculate the velocity of the points
# Velocity relative to base point in the global frame
P1.v2pt_theory(O, I, A)
P2.v2pt_theory(O, I, B)
points = [P1, P2]

# locate the center of mass
P_link1 = O.locatenew('P_link1', -l[0]/2 * A.y)
P_link2 = O.locatenew('P_link2', -l[1]/2 * B.y)

# define the linear velocities
P_link1.v2pt_theory(O, I, A)
P_link2.v2pt_theory(O, I, B)

points_rigid_body = [P_link1, P_link2]

# define inertias
inertia_link1 = (me.inertia(A, Ixx[0], Iyy[0], Izz[0]), P_link1)
inertia_link2 = (me.inertia(B, Ixx[1], Iyy[1], Izz[1]), P_link2)

# create rigid bodies
link1 = me.RigidBody('link1', P_link1, A, m_link[0], inertia_link1)
link2 = me.RigidBody('link2', P_link2, B, m_link[1], inertia_link2)

links = [link1, link2]

# add all the acting forces
# Need to add a force for the joint torques
forces = []
for link in links:
    mass = link.mass
    point = link.masscenter
    forces.append((point, -mass*g*I.y))

total_system = links

# all generalized coords and speeds
q = thetaz
u = omegaz

print("Generating equations of motion.")
kane = me.KanesMethod(I, q_ind=q, u_ind=u, kd_eqs=kinematic_differentials)
fr, frstar = kane.kanes_equations(forces, total_system)
print('Fr: {}'.format(fr))
print('Fr_Star: {}'.format(frstar))


# ------------------
# Simulate
# ------------------
# external
from numpy import radians, linspace, hstack, zeros, ones
from scipy.integrate import odeint
from pydy.codegen.ode_function_generators import generate_ode_function

param_syms = []
for par_seq in [l, m_link, Ixx, Iyy, Izz, (g,)]:
    param_syms += list(par_seq)

link_length = 10.0  # meters
link_mass = 10.0  # kg
link_radius = 0.5  # meters
link_ixx = 1.0 / 12.0 * link_mass * (3.0 * link_radius**2 + link_length**2)
link_iyy = link_mass * link_radius**2
link_izz = link_ixx

param_vals = [link_length for x in l] + \
             [link_mass for x in m_link] + \
             [link_ixx for x in list(Ixx)] + \
             [link_iyy for x in list(Iyy)] + \
             [link_izz for x in list(Izz)] + \
             [9.8]

print("Generating numeric right hand side.")
right_hand_side = generate_ode_function(kane.forcing_full, q, u, param_syms,
                                        mass_matrix=kane.mass_matrix_full,
                                        generator='cython')


t = linspace(0.0, 60.0, num=600)
x0 = hstack((ones(2*n) * radians(10.0), zeros(2*n)))

print("Integrating equations of motion.")
pdb.set_trace()
state_trajectories = odeint(right_hand_side, x0, t, args=(dict(zip(param_syms,param_vals)),))
print("Integration done.")

# ------------------
# Visualize
# ------------------



