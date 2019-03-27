import utils
import pandas as pd
import numpy as np

update_database=False

def main(plot_type='synoptic', plot_filename='output.png', projection='italy'):
	if plot_filename:
		import matplotlib
		matplotlib.use("cairo")

	# First get coordinates
	if update_database:
	    utils.download_coordinate_stations()

	df = utils.get_realtime_values()

	# Read the coordinates
	coords = pd.read_csv('stazioni_coordinate.csv', index_col=0)

	# Now merge the two dataset. This automatically takes care 
	# of finding the common stations using station_id
	#
	data=pd.merge(left=coords, left_on='station_id', right=df,
	                 right_on='station_id', suffixes=('',''))

	lats = data['latitude'].values
	lons = data['longitude'].values

	# Filter stations to remove overlapping points
	# Modify max_density and num_bins to act on the filtering
	
	if plot_type == 'temperature':
		temperature = data['temperature'].values
		temperature_sparse = utils.filter_values(temperature, lats, lons)
		plot_temperature(projection, temperature_sparse, temperature, lons, lats, data['date'], plot_filename)
	elif plot_type == 'rain':
		precipitation = data['daily_rain'].values
		precipitation_sparse = utils.filter_values(precipitation, lats, lons, max_density=1)
		plot_rain(projection, precipitation_sparse, precipitation, lons, lats, data['date'], plot_filename)
	elif plot_type == 'humidity':
		humidity = data['humidity'].values
		humidity_sparse = utils.filter_values(humidity, lats, lons)
		plot_humidity(projection, humidity_sparse, humidity, lons, lats, data['date'], plot_filename)
	elif plot_type == 'gust':
		gust = data['wind_gust'].values
		u, v = utils.wind_components(data['wind_speed'].values, data['wind_direction'].values)
		u_sparse = utils.filter_values(u, lats, lons, max_density=1)
		v_sparse = utils.filter_values(v, lats, lons, max_density=1)
		gust_sparse = utils.filter_values(gust, lats, lons, max_density=1)
		plot_gust(projection, gust_sparse, gust, u_sparse, v_sparse,
					 lons, lats, data['date'], plot_filename)
	elif plot_type == 'synoptic':
		u, v = utils.wind_components(data['wind_speed'].values, data['wind_direction'].values)
		u_sparse = utils.filter_values(u, lats, lons, max_density=1, num_bins=30)
		v_sparse = utils.filter_values(v, lats, lons, max_density=1, num_bins=30)
		mslp = data['pressure'].values
		mslp_sparse = utils.filter_values(mslp, lats, lons, max_density=1, num_bins=30)
		mslp_sparse[mslp_sparse==0] = np.nan
		plot_synoptic(projection, u_sparse, v_sparse, mslp_sparse,
					 lons, lats, data['date'], plot_filename)
	else:
		print('Error, variable %s not found' % plot_type)

def plot_temperature(projection, temp_sparse, temp,
					 lons, lats, date, plot_filename='output.png'):
	import matplotlib.pyplot as plt
	'''Plot temperature on the map'''
	fig = plt.figure(1, figsize=(10,10))

	ax = utils.get_projection(plt, projection, regions=False)

	utils.add_vals_on_map(ax=ax, projection=projection, var=temp_sparse, lons=lons, lats=lats)

	plt.title('Temperature live | Ultimo aggiornamento %s' % date[0])

	utils.add_logo_on_map(ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
	utils.add_logo_on_map(ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
	utils.add_hist_on_map(ax=ax, var=temp, label='Temperatura [C]')

	plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
	plt.clf()

def plot_humidity(projection, hum_sparse, hum,
					 lons, lats, date, plot_filename='output.png'):
	import matplotlib.pyplot as plt

	fig = plt.figure(1, figsize=(10,10))
	ax = utils.get_projection(plt, projection, regions=False)

	utils.add_vals_on_map(ax=ax, var=hum_sparse, projection=projection,
	 lons=lons, lats=lats, minval=0, maxval=100, cmap='jet_r')

	plt.title('Umidita live | Ultimo aggiornamento %s' % date[0])

	utils.add_logo_on_map(ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
	utils.add_logo_on_map(ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
	utils.add_hist_on_map(ax=ax, var=hum, label='Umidita [%]')

	plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
	plt.clf()

def plot_rain(projection, rain_sparse, rain,
					 lons, lats, date, plot_filename='output.png'):
	import matplotlib.pyplot as plt

	fig = plt.figure(1, figsize=(10,10))
	ax = utils.get_projection(plt, projection, regions=False)

	utils.add_vals_on_map(ax=ax, var=rain_sparse, projection=projection,
	 lons=lons, lats=lats, minval=0, maxval=150, cmap='gist_stern_r')

	plt.title('Precipitazioni live | Ultimo aggiornamento %s' % date[0])

	utils.add_logo_on_map(ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
	utils.add_logo_on_map(ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
	utils.add_hist_on_map(ax=ax, var=rain, label='Pioggia giornaliera [mm]')

	plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
	plt.clf()

def plot_gust(projection, gust_sparse, gust, u, v,
					 lons, lats, date, plot_filename='output.png'):
	import matplotlib.pyplot as plt

	fig = plt.figure(1, figsize=(10,10))
	ax = utils.get_projection(plt, projection, regions=False)

	utils.add_vals_on_map(ax=ax, var=gust_sparse, projection=projection,
	 lons=lons, lats=lats, minval=0, maxval=150, cmap='gist_stern_r', fontsize=10)

	utils.add_barbs_on_map(ax=ax,  projection=projection, u=u, v=v,
	     lons=lons, lats=lats)

	plt.title('Raffiche live | Ultimo aggiornamento %s' % date[0])

	utils.add_logo_on_map(ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
	utils.add_logo_on_map(ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
	utils.add_hist_on_map(ax=ax, var=gust, label='Raffica [km/h]')

	plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
	plt.clf()

def plot_synoptic(projection, u, v, mslp,
					 lons, lats, date, plot_filename='output.png'):
	import matplotlib.pyplot as plt

	fig = plt.figure(1, figsize=(10,10))
	ax = utils.get_projection(plt, projection, regions=False)

	utils.add_vals_on_map(ax=ax, var=mslp, projection=projection,
	 lons=lons, lats=lats, minval=960, maxval=1050, colors=False, fontsize=8)

	utils.add_barbs_on_map(ax=ax,  projection=projection, u=u, v=v,
	     lons=lons, lats=lats, magnitude=True)

	plt.title('Pressione e venti  | Ultimo aggiornamento %s' % date[0])

	utils.add_logo_on_map(ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
	utils.add_logo_on_map(ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))

	plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
	plt.clf()

if __name__ == "__main__":
    main()