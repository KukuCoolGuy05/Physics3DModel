import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk

#variables holding all of the constants that is required for this project
k_e = 8.99e9 #Coulomb constant
q_proton = 1.602e-19 #charge of a proton
q_electron = -1.602e-19 #charge of an electron

proton_position = np.array([1, 0, 0])
electron_position = np.array([-1, 0, 0])
proton_visible = True
electron_visible = True

#define a grid of points in 3D space
x = np.linspace(-2, 2, 10)
y = np.linspace(-2, 2, 10)
z = np.linspace(-2, 2, 10)
X, Y, Z = np.meshgrid(x, y, z) #final grid we want to graph on 

#create a 3D plot for the electric field
fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(111, projection='3d')

#function to calculate electric field
def electric_field(q, r_charge, X, Y, Z):
    #distance vectors for x, y, z
    Rx = X - r_charge[0]
    Ry = Y - r_charge[1]
    Rz = Z - r_charge[2]
    R = np.sqrt(Rx**2 + Ry**2 + Rz**2)
    R[R == 0] = np.inf
    
    #electric field components
    Ex = k_e * q * Rx / R**3
    Ey = k_e * q * Ry / R**3
    Ez = k_e * q * Rz / R**3
    return Ex, Ey, Ez

def plot_3D():
    global proton_visible, electron_visible, fig, ax

    #clear the previous graph
    ax.clear()

    #electric field due to the proton and electron, call it using the constants we have defined above
    Ex_proton, Ey_proton, Ez_proton = 0, 0, 0
    Ex_electron, Ey_electron, Ez_electron = 0, 0, 0

    #check whether the proton or electon is visible on the grid and update accordingly
    if proton_visible:
        ax.scatter(*proton_position, color="red", s=100, label="Proton")
        Ex_proton, Ey_proton, Ez_proton = electric_field(q_proton, proton_position, X, Y, Z)
    if electron_visible:
        ax.scatter(*electron_position, color="green", s=100, label="Electron")
        Ex_electron, Ey_electron, Ez_electron = electric_field(q_electron, electron_position, X, Y, Z)

    #total electric field, add the electric feild of proton and electron
    Ex = Ex_proton + Ex_electron
    Ey = Ey_proton + Ey_electron
    Ez = Ez_proton + Ez_electron

    #plotting vector using quiver, and proton/electron on the grid as well
    ax.quiver(X, Y, Z, Ex, Ey, Ez, length=0.15, normalize=True, color='blue')

    #set plot limits
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])

    #set x, y, x labels and the title for the 3D graph
    ax.set_xlabel("x")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Electric Field of a Proton and Electron")

    #plot the graph with the legend
    ax.legend()
    plt.show() 

#toggle proton on and off, update the grid
def toggle_proton():
    global proton_visible
    proton_visible = not proton_visible
    plot_3D()

#toggle electron on and off,, update the grid
def toggle_electron():
    global electron_visible
    electron_visible = not electron_visible
    plot_3D() 

# Create the main Tkinter window
root = tk.Tk()
root.title("Electric Field Visualizer")

# Create buttons to toggle visibility
btn_toggle_proton = tk.Button(root, text="Toggle Proton", command=toggle_proton)
btn_toggle_proton.pack(pady=20)

btn_toggle_electron = tk.Button(root, text="Toggle Electron", command=toggle_electron)
btn_toggle_electron.pack(pady=20)

# Start plotting the field initially
plot_3D()

# Start the Tkinter event loop
root.mainloop()