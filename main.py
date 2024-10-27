import numpy as np
from flask import Flask, render_template, jsonify, request
import plotly.graph_objects as go
import plotly.io as pio
import extention

#create flask for calling the graph on a website
app = Flask(__name__)

#route the main page with get and post methods
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            data = request.get_json()
            show_proton = data.get('proton', True)
            show_electron = data.get('electron', True)
            plot_html = extention.plot_3D(show_proton, show_electron)
            return jsonify({'plot': plot_html, 'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        #initial load
        plot_html = extention.plot_3D(True, True)
        return render_template("index.html", plot=plot_html)

@app.route("/gaussian_surfaces", methods=['GET', 'POST'])
def gaussian_surfaces():
    if request.method == 'POST':
        try:
            data = request.get_json()
            #extract and validate parameters
            surface_type = data.get('surface_type', 'sphere')
            if surface_type not in ['sphere', 'cylinder', 'plane']:
                raise ValueError(f"Invalid surface type: {surface_type}")
                
            radius = float(data.get('radius', 25))
            if not (1 <= radius <= 50):
                raise ValueError(f"Radius must be between 1 and 50, got {radius}")
                
            charge = float(data.get('charge', 1))
            if not (-10 <= charge <= 10):
                raise ValueError(f"Charge must be between -10 and 10, got {charge}")
            
            #generate the plot
            figure = extention.plot_gaussian_surface(surface_type, radius, charge)
            plot_html = pio.to_html(
                figure,
                full_html=False,
                include_plotlyjs='cdn',
                config={
                    'displayModeBar': True,
                    'responsive': True,
                    'scrollZoom': True
                }
            )
            
            return jsonify({'plot': plot_html, 'status': 'success'})
            
        except Exception as e:
            return jsonify({'error': str(e), 'status': 'error'}), 500
    else:
        #initial plot for GET request
        figure = extention.plot_gaussian_surface()
        plot_html = pio.to_html(
            figure,
            full_html=False,
            include_plotlyjs='cdn',
            config={
                'displayModeBar': True,
                'responsive': True,
                'scrollZoom': True
            }
        )
        return render_template("GaussianSurfaces.html", plot=plot_html)

@app.route("/wires")
def wires():
    return render_template("Wires.html")

if __name__ == "__main__":
    app.run(debug=True)