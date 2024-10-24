import numpy as np
from flask import Flask, render_template
import plotly.graph_objects as go
import plotly.io as pio

#create flask for calling the graph on a website
app = Flask(__name__)

#variables holding all of the constants that is required for this project
k_e = 8.99e9 #Coulomb constant
q_proton = 1.602e-19 #charge of a proton
q_electron = -1.602e-19 #charge of an electron

proton_position = [1, 0, 0]
electron_position = [-1, 0 , 0]

#define a grid of points in 3D space
x = np.linspace(-2, 2, 10).astype(float)
y = np.linspace(-2, 2, 10).astype(float)
z = np.linspace(-2, 2, 10).astype(float)
X, Y, Z = np.meshgrid(x, y, z) #final grid we want to graph on 

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
    #electric field due to the proton and electron, call it using the constants we have defined above
    Ex_proton, Ey_proton, Ez_proton = electric_field(q_proton, proton_position, X, Y, Z)
    Ex_electron, Ey_electron, Ez_electron = electric_field(q_electron, electron_position, X, Y, Z)
    
    #the final electric field should be the sum of both proton's and electron's electric field
    Ex = Ex_proton + Ex_electron
    Ey = Ey_proton + Ey_electron
    Ez = Ez_proton + Ez_electron

    #create the figure and add the arrows/proton/electron
    figure = go.Figure()
    figure.add_trace(go.Cone(x=X.flatten(), y=Y.flatten(), z=Z.flatten(), u=Ex.flatten(), v=Ey.flatten(), w=Ez.flatten(), sizemode="scaled", sizeref=0.6, anchor="tail", opacity=1, colorscale="Blues", showscale=False))
    figure.add_trace(go.Scatter3d(x=[proton_position[0]], y=[proton_position[1]], z=[proton_position[2]], mode="markers", marker=dict(size=15, color="red"), name="Proton"))
    figure.add_trace(go.Scatter3d(x=[electron_position[0]], y=[electron_position[1]], z=[electron_position[2]], mode="markers", marker=dict(size=15, color="green"), name="Electron"))

    #create and update the layout of the figure
    scene_dict = dict(xaxis=dict(nticks=10, range=[-2, 2]), yaxis=dict(nticks=10, range=[-2, 2]), zaxis=dict(nticks=10, range=[-1, 1]))
    figure.update_layout(scene=scene_dict, title="Electric Field of a proton and an electron", width=1300, height=1300)

    #return the figure we created using pio.to_html
    return pio.to_html(figure, full_html=False)

@app.route('/')
def index():
    plot_html = plot_3D()
    return render_template("index.html", plot=plot_html)

if __name__ == "__main__":
    app.run(debug=True)