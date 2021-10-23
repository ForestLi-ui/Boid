from mpl_toolkits import mplot3d
import numpy as np
import math
import matplotlib.pyplot as plt

cm = plt.get_cmap("RdYlGn")
fig = plt.figure()
ax = plt.axes(projection='3d')

# fibonacci lattice
n = 100
goldenRatio = (1 + 5 ** 0.5) / 2
x_list = []
y_list = []
z_list = []
for i in range(n):
    theta = 2 * math.pi * i / goldenRatio
    phi = math.acos(1 - 2 * (i + 0.5) / n)
    x, y, z = math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi)
    x_list.append(x)
    y_list.append(y)
    z_list.append(z)
ax.scatter(x_list, y_list, z_list)
plt.show()
