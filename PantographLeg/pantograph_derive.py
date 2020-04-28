import sympy
import pdb


# Angles that we can control
theta_1, theta_5 = sympy.symbols('theta_1 theta_5')

theta_2, theta_4 = sympy.symbols('theta_2 theta_4')

theta_f = sympy.symbols('theta_f')

l1, l2, l3, l4, l5 = sympy.symbols('l1 l2 l3 l4 l5')

# Side A of the pantograph
p1 = [0, 0]
p2 = [p1[0] + l1*sympy.cos(theta_1), p1[1] + l1*sympy.sin(theta_1)]

p3_A = [p2[0] + l2*sympy.cos(theta_1 + theta_2), p2[1] + l2*sympy.sin(theta_1 + theta_2)]

# Side B of the pantograph
p5 = [p1[0] + l5 * sympy.cos(theta_f), p1[1] + l5 * sympy.sin(theta_f)]
p4 = [p5[0] + l4 * sympy.cos(theta_5), p5[0] + l4 * sympy.cos(theta_5)]

p3_B = [p4[0] + l3 * sympy.cos(theta_5 + theta_4), p4[1] + l3 * sympy.sin(theta_5 + theta_4)]

# Solve the equations
x_eq = p3_B[0] - p3_A[0]
y_eq = p3_B[1] - p3_A[1]
theta_2_sol = sympy.solvers.solve(x_eq, theta_2)[0]

# Replace theta_2 into the y equation
y_eq_with_sub = y_eq.replace(theta_2, theta_2_sol)
theta_4_sol = sympy.solvers.solve(y_eq_with_sub, theta_4)[0]
 # IDK THIS DIDN"T WORK



