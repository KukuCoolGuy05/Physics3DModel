import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#variables holding all of the constants that is required for this project
k_e = 8.99e9 #Coulomb constant
q_proton = 1.602e-19 #charge of a proton
q_electron = -1.602e-19 #charge of an electron

proton_position = np.array([1, 0, 0])
electron_position = np.array([-1, 0, 0])

# Define a grid of points in 3D space
x = np.linspace(-2, 2, 20)
y = np.linspace(-2, 2, 20)
z = np.linspace(-2, 2, 20)
X, Y, Z = np.meshgrid(x, y, z)

# Function to calculate electric field
def electric_field(q, r_charge, X, Y, Z):
    # Distance vectors
    Rx = X - r_charge[0]
    Ry = Y - r_charge[1]
    Rz = Z - r_charge[2]
    R = np.sqrt(Rx**2 + Ry**2 + Rz**2)
    
    # Avoid division by zero at the charge location
    R[R == 0] = np.inf
    
    # Electric field components
    Ex = k_e * q * Rx / R**3
    Ey = k_e * q * Ry / R**3
    Ez = k_e * q * Rz / R**3
    return Ex, Ey, Ez

# Electric field due to the proton and electron
Ex_proton, Ey_proton, Ez_proton = electric_field(q_proton, proton_position, X, Y, Z)
Ex_electron, Ey_electron, Ez_electron = electric_field(q_electron, electron_position, X, Y, Z)

# Total electric field
Ex = Ex_proton + Ex_electron
Ey = Ey_proton + Ey_electron
Ez = Ez_proton + Ez_electron

# Create a 3D plot for the electric field
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Plotting quiver (vector field)
ax.quiver(X, Y, Z, Ex, Ey, Ez, length=0.05, normalize=True, color='blue')

# Plot proton and electron positions
ax.scatter(*proton_position, color='red', s=100, label='Proton')
ax.scatter(*electron_position, color='green', s=100, label='Electron')

# Set plot limits
ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([-2, 2])

# Labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Electric Field of a Proton and Electron')

# Show legend
ax.legend()

# Show the plot
plt.show()