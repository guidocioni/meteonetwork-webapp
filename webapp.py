from flask import Flask, send_file, request
from werkzeug import secure_filename
from datetime import datetime, timedelta

import plot_live
import plot_daily

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Meteonetwork Data</title>
    </head>
    <body>
        <h1>Meteonetwork-Meteoindiretta maps generator</h1>
        For live maps use the first input, for daily values use the second input. Not both at the same time!
        The resulting picture will open in the same window
        <h2>Live maps</h2>
        <form class="mapSelection" method="POST" action="/live">  
           <select class="mapForm" id="DropdownSelector" type="text" name="Dropdown" placeholder="Select A Map">
                <option disabled selected>Select a map</option>
                <option id="temperature" value="temperature">Temperature [C]</option>
                <option id="rain" value="rain">Daily Precipitation [mm]</option>
                <option id="humidity" value="humidity">Humidity [%]</option>
                <option id="gust" value="gust">Wind gusts [km/h]</option>
                <option id="synoptic" value="synoptic">MSLP [hPa] and winds direction</option>
           </select>
           <input class="btn" type="submit" value="submit">
        </form>
        <h2>Daily maps</h2>
        <form class="dailyMapSelection" method="POST" action="/daily">  
           <select class="dailyMapForm" id="DropdownSelector" type="text" name="DropdownDaily" placeholder="Select A Map">
                <option disabled selected>Select a Map</option>
                <option id="temperature_max" value="temperature_max">Maximum Temperature [C]</option>
                <option id="temperature_min" value="temperature_min">Minimum Temperature [C]</option>
                <option id="rain" value="rain">Daily precipitation [mm]</option>
                <option id="gust" value="gust">Maximum gust [km/h]</option>
           </select>
           <input name="date" placeholder="YYYY-MM-DD">
           <input class="btn" type="submit" value="submit">
        </form>
    </body>
    </html>
    """


@app.route('/live', methods = ['POST'])
def live():
    map_type = request.form.get("Dropdown")
    if map_type is None:
        map_type = 'temperature'

    plot_filename = 'output.png'
    plot_live.main(plot_type=map_type, plot_filename=plot_filename, projection='italy')
    
    return send_file(plot_filename, mimetype='image/png')

@app.route('/daily', methods = ['POST'])
def daily():
    map_type = request.form.get("DropdownDaily")
    if map_type is None:
        map_type = 'temperature_max'
    date = request.form.get("date")
    if date == '':
        date = (datetime.now()-timedelta(1)).strftime(format='%Y-%m-%d')

    plot_filename = 'output.png'
    plot_daily.main(plot_type=map_type, date_download=date,
             plot_filename=plot_filename, projection='italy')
    
    return send_file(plot_filename)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host='0.0.0.0')
