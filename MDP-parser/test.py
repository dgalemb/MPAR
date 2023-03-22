import numpy as np

R1 = np.zeros((8, 3))
R1[3][2] = 1
R2 = np.ones((8, 3))
Q = np.zeros((8, 3))

print(Q)
print(R1)
print(R2)


Q = R1/(R1 + R2)

print(Q)