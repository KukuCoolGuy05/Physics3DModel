import extention
from flask import Flask, render_template, jsonify, request

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
            surface_type = data.get('surface_type', 'sphere')
            radius = float(data.get('radius', 25))
            charge = float(data.get('charge', q_proton))
            plot_html = extention.plot_gaussian_surface(surface_type, radius, charge)
            return jsonify({'plot': plot_html, 'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        plot_html = extention.plot_gaussian_surface()
        return render_template("GaussianSurfaces.html", plot=plot_html)

@app.route("/wires")
def wires():
    return render_template("Wires.html")

if __name__ == "__main__":
    app.run(debug=True)