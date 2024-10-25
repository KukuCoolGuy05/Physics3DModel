import numpy as np
from flask import Flask, render_template, jsonify, request
import plotly.graph_objects as go
import plotly.io as pio

#create flask for calling the graph on a website
app = Flask(__name__)

#variables holding all of the constants that is required for this project
k_e = 8.99e9 #Coulomb constant
q_proton = 1.602e-19 #charge of a proton
q_electron = -1.602e-19 #charge of an electron

proton_position = [25, 0, 0]
electron_position = [-25, 0 , 0]

#define a grid of points in 3D space
x = np.linspace(-100, 100, 10)
y = np.linspace(-100, 100, 10)
z = np.linspace(-100, 100, 10)
X, Y, Z = np.meshgrid(x, y, z) #final grid we want to graph on 

#function to calculate electric field
def electric_field(q, r_charge, X, Y, Z):
    #distance vectors for x, y, z
    Rx = X - r_charge[0]
    Ry = Y - r_charge[1]
    Rz = Z - r_charge[2]
    R = np.sqrt(Rx**2 + Ry**2 + Rz**2)
    R[R < 1e-10] = 1e-10
    
    #electric field components
    Ex = k_e * q * Rx / R**3
    Ey = k_e * q * Ry / R**3
    Ez = k_e * q * Rz / R**3
    return Ex, Ey, Ez

#scale the arrows so they decrease in length as electric field decreases
def scale_vectors(Ex, Ey, Ez):
    #calculate magnitudes and find the max magnitude 
    magnitudes = np.sqrt(Ex**2 + Ey**2 + Ez**2)
    max_magnitude = np.max(magnitudes[magnitudes != np.inf])
    
    #normalize magnitudes
    relative_magnitudes = magnitudes / max_magnitude
    
    #scale factor for arrow length
    max_arrow_length = 15
    
    #scale the vectors based on their magnitude
    scale = max_arrow_length * relative_magnitudes
    
    #normalize direction vectors and apply scaling
    Ex_scaled = np.where(magnitudes != 0, Ex * scale / magnitudes, 0)
    Ey_scaled = np.where(magnitudes != 0, Ey * scale / magnitudes, 0)
    Ez_scaled = np.where(magnitudes != 0, Ez * scale / magnitudes, 0)
    
    return Ex_scaled, Ey_scaled, Ez_scaled, relative_magnitudes

def plot_3D(show_proton=True, show_electron=True):
    #electric field components initialized to zero
    Ex = np.zeros_like(X)
    Ey = np.zeros_like(Y)
    Ez = np.zeros_like(Z)
    
    #add proton's electric field if it is shown on the figure, and do the same with electron
    if show_proton:
        Ex_proton, Ey_proton, Ez_proton = electric_field(q_proton, proton_position, X, Y, Z)
        Ex += Ex_proton
        Ey += Ey_proton
        Ez += Ez_proton
    if show_electron:
        Ex_electron, Ey_electron, Ez_electron = electric_field(q_electron, electron_position, X, Y, Z)
        Ex += Ex_electron
        Ey += Ey_electron
        Ez += Ez_electron

    Ex_norm, Ey_norm, Ez_norm, relative_magnitudes = scale_vectors(Ex, Ey, Ez)
    #create the figure and add the arrows/proton/electron
    figure = go.Figure()
    for i in range(len(X.flatten())):
        #get the position for each arrow
        x_start = X.flatten()[i]
        y_start = Y.flatten()[i]
        z_start = Z.flatten()[i]
        
        #calculate the end point of the arrow
        x_end = x_start + Ex_norm.flatten()[i]
        y_end = y_start + Ey_norm.flatten()[i]
        z_end = z_start + Ez_norm.flatten()[i]

        #print(f"Arrow {i}: Start({x_start}, {y_start}, {z_start}) End({x_end}, {y_end}, {z_end})")
        magnitude = relative_magnitudes.flatten()[i]
        #add the arrow to the figure
        if magnitude > 0.1:
            figure.add_trace(go.Scatter3d(x=[x_start, x_end], y=[y_start, y_end], z=[z_start, z_end], mode="lines+markers", line=dict(color="blue", width=2.5), marker=dict(size=[0, 4],), showlegend=False))

    figure.add_trace(go.Scatter3d(x=[proton_position[0]], y=[proton_position[1]], z=[proton_position[2]], mode="markers", marker=dict(size=10, color="red"), name="Proton"))
    figure.add_trace(go.Scatter3d(x=[electron_position[0]], y=[electron_position[1]], z=[electron_position[2]], mode="markers", marker=dict(size=10, color="green"), name="Electron"))

    #create and update the layout of the figure
    scene_dict = dict(xaxis=dict(range=[-100, 100]), yaxis=dict(range=[-100, 100]), zaxis=dict(range=[-100, 100], backgroundcolor="rgba(222, 226, 230, 1)"))
    figure.update_layout(scene=scene_dict, width=1000, height=1000, paper_bgcolor='rgba(222, 226, 230, 1)', plot_bgcolor='rgba(222, 226, 230, 1)')

    #return the figure we created using pio.to_html
    return pio.to_html(figure, full_html=False)

@app.route("/")
def index():
    show_proton = request.args.get('proton', 'true').lower() == 'true'
    show_electron = request.args.get('electron', 'true').lower() == 'true'
    plot_html = plot_3D(show_proton, show_electron)
    return render_template("index.html", plot=plot_html)

@app.route("/gaussian_surfaces")
def gaussian_surfaces():
    return render_template("GaussianSurfaces.html")

@app.route("/wires")
def wires():
    return render_template("Wires.html")

if __name__ == "__main__":
    app.run(debug=True)