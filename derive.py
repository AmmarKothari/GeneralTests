#!/usr/bin/env python
import pdb

from sympy import symbols
import sympy.physics.mechanics as me

print("Defining the problem.")

# The system will have n links
n = 2

# Each link's orientation is described by two spaced fixed angles: alpha and
# beta.

# Generalized coordinates
alpha = me.dynamicsymbols('alpha:{}'.format(n))
# beta = me.dynamicsymbols('beta:{}'.format(n))

# Generalized speeds
omega = me.dynamicsymbols('omega:{}'.format(n))
# delta = me.dynamicsymbols('delta:{}'.format(n))

# Generalized Forces
torque = me.dynamicsymbols('torque:{}'.format(n))

# Each link is modeled as a cylinder so it will have a length, mass, and a
# symmetric inertia tensor.
l = symbols('l:{}'.format(n))
m_link = symbols('M:{}'.format(n))
Ixx = symbols('Ixx:{}'.format(n))
Iyy = symbols('Iyy:{}'.format(n))
Izz = symbols('Izz:{}'.format(n))

# Acceleration due to gravity will be used when prescribing the forces
# acting on the links and bobs.
g = symbols('g')

# Now defining an inertial reference frame for the system to live in. The Y
# axis of the frame will be aligned with, but opposite to, the gravity
# vector.

I = me.ReferenceFrame('I')

# Three reference frames will track the orientation of the three links.

ref_frames = []
for i in range(n):
    if i == 0:
        prev_frame = I
    ref_frames.append(me.ReferenceFrame('F{}'.format(i)))
    # ref_frames[-1].orient(I, 'Space', [alpha[i], beta[i], 0], 'ZXY')
    prev_frames = ref_frames[-1]
# First link rotates around the x axis
ref_frames[0].orient(I, 'Space', [0, alpha[0], 0], 'ZXY')
ref_frames[1].orient(I, 'Space', [alpha[1], 0, 0], 'ZXY')

# Define the kinematical differential equations such that the generalized
# speeds equal the time derivative of the generalized coordinates.
kinematic_differentials = []
for i in range(n):
    kinematic_differentials.append(omega[i] - alpha[i].diff())
    # kinematic_differentials.append(delta[i] - beta[i].diff())

# The angular velocities of the three frames can then be set.
ref_frames[0].set_ang_vel(I, omega[0] * I.x)
ref_frames[1].set_ang_vel(I, omega[1] * I.z)
# for i in range(n):
#     ref_frames[i].set_ang_vel(I, omega[i] * I.z)
    # ref_frames[i].set_ang_vel(I, omega[i] * I.z + delta[i] * I.x)

# The base of the pendulum will be located at a point O which is stationary
# in the inertial reference frame.
O = me.Point('O')
O.set_vel(I, 0)


# The location of the bobs (at the joints between the links) are created by
# specifiying the vectors between the points.
p_joints = []
for i in range(n):
    if i == 0:
        prev_point = O
    else:
        prev_point = p_joints[-1]
    p_joints.append(prev_point.locatenew('P{}'.format(i + 1), -l[i] * ref_frames[i].y))

# The velocities of the points can be computed by taking advantage that
# pairs of points are fixed on the referene frames.
points = []
for i, point in enumerate(p_joints):
    if i == 0:
        prev_point = O
    point.v2pt_theory(prev_point, I, ref_frames[i])
    points.append(point)
    prev_point = point

# The mass centers of each link need to be specified and, assuming a
# constant density cylinder, it is equidistance from each joint.
p_links = []
for i in range(n):
    if i == 0:
        prev_point = O
    else:
        prev_point = points[i-1]
    p_links.append(prev_point.locatenew('P_link{}'.format(i + 1), -l[i] / 2 * ref_frames[i].y))
    p_links[-1].v2pt_theory(prev_point, I, ref_frames[i])

points_rigid_body = p_links

# The inertia tensors for the links are defined with respect to the mass
# center of the link and the link's reference frame.
inertia_links = []
links = []
for frame, link in zip(ref_frames, p_links):
    inertia_links.append( (me.inertia(ref_frames[i], Ixx[i], Iyy[i], Izz[i]), link) )
    # Now rigid bodies can be created for each link.
    rbody = me.RigidBody('link{}'.format(i), link, frame, m_link[i], inertia_links[-1])
    links.append(rbody)


# The only contributing forces to the system is the force due to gravity
# acting on each particle and body.
forces = []

for link in links:
    mass = link.mass
    point = link.masscenter
    forces.append((point, -mass * g * I.y))

forces.append((p_joints[0], torque[0]/l[0] * I.x))
forces.append((p_joints[1], torque[1]/l[1] * I.z))

# Make a list of all the particles and bodies in the system.
total_system = links

# Lists of all generalized coordinates and speeds.
# q = alpha + beta
# u = omega + delta
q = alpha
u = omega

# Now the equations of motion of the system can be formed.
print("Generating equations of motion.")
kane = me.KanesMethod(I, q_ind=q, u_ind=u, kd_eqs=kinematic_differentials)
fr, frstar = kane.kanes_equations(total_system, forces)
print("Derivation complete.")

print("Generating kinematics equations")





pdb.set_trace()
