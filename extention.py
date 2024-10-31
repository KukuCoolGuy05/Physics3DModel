import numpy as np
from flask import Flask, render_template, jsonify, request
import plotly.graph_objects as go
import plotly.io as pio

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

def gaussian_electric_field(surface_type, r_point, q, X, Y, Z):
    #distance vectors for x, y, z (reusing your existing pattern)
    Rx = X - r_point[0]
    Ry = Y - r_point[1]
    Rz = Z - r_point[2]
    R = np.sqrt(Rx**2 + Ry**2 + Rz**2)
    R[R < 1e-10] = 1e-10
    
    #calculate electric field for each surface
    if surface_type == "sphere":
        Ex = k_e * q * Rx / R**3
        Ey = k_e * q * Ry / R**3
        Ez = k_e * q * Rz / R**3
        
    elif surface_type == "cylinder":
        Rxy = np.sqrt(Rx**2 + Ry**2)
        Rxy[Rxy < 1e-10] = 1e-10
        
        # Only radial component in xy-plane
        Ex = k_e * q * Rx / (Rxy * R**2)
        Ey = k_e * q * Ry / (Rxy * R**2)
        Ez = np.zeros_like(Z)
        
    elif surface_type == "plane":
        Ex = np.zeros_like(X)
        Ey = np.zeros_like(Y)
        Ez = np.sign(Rz) * k_e * q / R**2
        
    return Ex, Ey, Ez

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

    #add proton or electron if the toggle is on 
    if show_proton:
        figure.add_trace(go.Scatter3d(x=[proton_position[0]], y=[proton_position[1]], z=[proton_position[2]], mode="markers", marker=dict(size=10, color="red"), name="Proton", showlegend=True))
    else:
        #add an invisible proton trace to maintain consistent trace indices
        figure.add_trace(go.Scatter3d(x=[proton_position[0]], y=[proton_position[1]], z=[proton_position[2]], mode="markers", marker=dict(size=0, color="red", opacity=0), name="Proton", showlegend=False, hoverinfo='skip', visible=False))
    if show_electron:
        figure.add_trace(go.Scatter3d(x=[electron_position[0]], y=[electron_position[1]], z=[electron_position[2]], mode="markers", marker=dict(size=10, color="green"), name="Electron", showlegend=True))
    else:
        #add an invisible electron trace to maintain consistent trace indices
        figure.add_trace(go.Scatter3d(x=[electron_position[0]], y=[electron_position[1]], z=[electron_position[2]], mode="markers", marker=dict(size=0, color="green", opacity=0), name="Electron", showlegend=False, hoverinfo='skip', visible=False))

    #create and update the layout of the figure
    scene_dict = dict(xaxis=dict(range=[-75, 75]), yaxis=dict(range=[-75, 75]), zaxis=dict(range=[-75, 75], backgroundcolor="rgba(222, 226, 230, 1)"))
    figure.update_layout(scene=scene_dict, width=1000, height=1000, paper_bgcolor='rgba(222, 226, 230, 1)', plot_bgcolor='rgba(222, 226, 230, 1)', uirevision=True, transition_duration=0)

    #if post is called, send plot data as JSON instead of HTML
    if request.method == 'POST':
        return figure.to_json()
    
    #return the figure we created
    return pio.to_html(
        figure,
        full_html=False,
        include_plotlyjs='cdn',
        config={
            'displayModeBar': True,
            'responsive': True,
            'scrollZoom': True
        }
    )

#create a new figure that will display the gaussian surface and its electric field
def plot_gaussian_surface(surface_type='sphere', radius=25, charge=q_proton):    
    # Calculate electric field
    r_point = [0, 0, 0]  # Center point for field calculation
    Ex, Ey, Ez = gaussian_electric_field(surface_type, r_point, charge, X, Y, Z)
    
    #scale vectors using your existing function
    Ex_norm, Ey_norm, Ez_norm, relative_magnitudes = scale_vectors(Ex, Ey, Ez)
    
    #create figure
    figure = go.Figure()
    
    #add electric field arrows
    for i in range(len(X.flatten())):
        x_start = X.flatten()[i]
        y_start = Y.flatten()[i]
        z_start = Z.flatten()[i]
        
        x_end = x_start + Ex_norm.flatten()[i]
        y_end = y_start + Ey_norm.flatten()[i]
        z_end = z_start + Ez_norm.flatten()[i]
        
        magnitude = relative_magnitudes.flatten()[i]
        if magnitude > 0.1:
            figure.add_trace(go.Scatter3d(x=[x_start, x_end], y=[y_start, y_end], z=[z_start, z_end], mode="lines+markers", line=dict(color="blue", width=2.5), marker=dict(size=[0, 4]), showlegend=False))
    
    #add Gaussian surface visualization
    theta = np.linspace(0, 2*np.pi, 50)
    phi = np.linspace(0, np.pi, 50)
    theta, phi = np.meshgrid(theta, phi)
    
    if surface_type == "sphere":
        x_surf = radius * np.sin(phi) * np.cos(theta)
        y_surf = radius * np.sin(phi) * np.sin(theta)
        z_surf = radius * np.cos(phi)
        
    elif surface_type == "cylinder":
        h = np.linspace(-50, 50, 50)
        theta, h = np.meshgrid(theta, h)
        x_surf = radius * np.cos(theta)
        y_surf = radius * np.sin(theta)
        z_surf = h
        
    elif surface_type == "plane":
        x_surf = np.linspace(-50, 50, 50)
        y_surf = np.linspace(-50, 50, 50)
        x_surf, y_surf = np.meshgrid(x_surf, y_surf)
        z_surf = np.full_like(x_surf, radius)
    
    figure.add_trace(go.Surface(
        x=x_surf, y=y_surf, z=z_surf,
        opacity=0.3,
        showscale=False,
        name=f"{surface_type.title()} Gaussian Surface"
    ))
    
    # Use your existing layout setup
    scene_dict = dict(
        xaxis=dict(range=[-75, 75]),
        yaxis=dict(range=[-75, 75]),
        zaxis=dict(range=[-75, 75]),
        bgcolor="rgba(222, 226, 230, 1)"
    )
    
    figure.update_layout(
        scene=scene_dict,
        width=1000,
        height=1000,
        paper_bgcolor='rgba(222, 226, 230, 1)',
        plot_bgcolor='rgba(222, 226, 230, 1)',
        uirevision=True,
        transition_duration=0
    )
    
    return figure