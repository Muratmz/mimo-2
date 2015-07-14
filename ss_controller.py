
###########################################################################
## ECE: 3111 Final Project                                               ##
## Amadeusz Nasuta                                                       ##
## Christian Ratliff                                                     ##
## Michael Williams                                                      ##
## Erica Wisniewski                                                      ##
###########################################################################

## ss_controller.py

import numpy as np 
import control
import control.matlab as matlab
from matplotlib import pyplot as plt
from matplotlib import rc
rc('text', usetex=True)

## State space representation
A = np.array([
    [0, 1, 0, 0], 
    [62.0139, -44.5897, 0, -2123.32],
    [0, 0, 0, 1],
    [6.09908, -10.1911, 0, -485.289]
    ])
B = np.array([[0], [-90.0275], [0], [-20.5759]])
C = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])
D = np.array([[0], [0]])

## Controllability matrix
C_m = control.ctrb(A, B)
rank = np.linalg.matrix_rank(C_m)

## State space controller
t = np.linspace(0, 5, 1e3) # Time steps
Q = np.matrix.transpose(C) * np.matrix(C) # compute Q-matrix
Q[0, 0] = 100 # index controls position
Q[2, 2] = 1500 # index controls angle
print("Q shape")
print(np.shape(Q))
R = 1
(K, S, E) = matlab.lqr(A, B, Q, R) # Linear quadratic regulation
Ac = np.matrix(A - (B * K)) 
Bc = np.matrix(B)
Cc = np.matrix(C)
Dc = np.matrix(D)
sys_cl = control.ss(Ac, Bc, Cc, Dc)
r = 0.2 * np.ones(len(t)) # Input at each time T
[y, t_out, x] = matlab.lsim(sys_cl, U=r, T=t) # simulate close-loop system

# Plot results
fig, ax1 = plt.subplots()
plt.title(r'State Space Controller')
ax1.plot(t_out, y[:,1], color='g') # position 
ax1.set_ylabel(r'position (m)', color='g')
for t1 in ax1.get_yticklabels():
    t1.set_color('g')
ax2 = ax1.twinx()
ax2.plot(t_out, y[:,0], color='b') # angle
ax2.set_ylabel(r'angle (rad)', color='b')
for t1 in ax2.get_yticklabels():
    t1.set_color('b')
ax1.set_xlabel(r'time (s)')
plt.grid()
plt.tight_layout()
#plt.savefig("ss_controller.pdf")
plt.show()

print("LQR CONTROLLER")
print()
print("R = ", R)
print()
print("Q matrix:")
print(Q)
print()
print("Gain matrix: K")
print(K)
print()
print("System matrix for closed-loop system: A - (B * K)")
print(Ac)
