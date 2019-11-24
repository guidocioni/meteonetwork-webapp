import utils
import pandas as pd
from datetime import datetime, timedelta

update_database = False


def main(plot_type='temperature_max', date_download=(datetime.now() - timedelta(1)).strftime(format='%Y-%m-%d'),
         plot_filename='output.png', projection='italy'):
    if plot_filename:
        import matplotlib
        matplotlib.use("agg")

    # First get coordinates
    if update_database:
        utils.download_coordinate_stations()

    df = utils.get_daily_values(date_download)

    # Read the coordinates
    coords = pd.read_csv('stazioni_coordinate.csv', index_col=0)

    # Now merge the two dataset. This automatically takes care
    # of finding the common stations using station_id
    #
    data = pd.merge(left=coords, left_on='station_id', right=df,
                    right_on='station_id', suffixes=('', ''))

    lats = data['latitude'].values
    lons = data['longitude'].values

    if plot_type == 'temperature_max':
        temp_max = data['temp max'].values
        temp_max_sparse = utils.filter_max_values(temp_max, lats, lons)
        plot_temperature_max(projection, plot_type, temp_max_sparse, temp_max, lons, lats,
                             date_download, plot_filename)
    elif plot_type == 'temperature_min':
        temp_min = data['temp min'].values
        temp_min_sparse = utils.filter_min_values(temp_min, lats, lons)
        plot_temperature_min(projection, plot_type, temp_min_sparse, temp_min, lons, lats,
                             date_download, plot_filename)
    elif plot_type == 'rain':
        rain = data['rain'].values
        rain_sparse = utils.filter_max_values(rain, lats, lons)
        plot_rain(projection, rain_sparse, rain, lons,
                  lats, date_download, plot_filename)
    elif plot_type == 'gust':
        gust = data['wind max'].values
        gust_sparse = utils.filter_max_values(gust, lats, lons)
        plot_gust(projection, gust_sparse, gust, lons,
                  lats, date_download, plot_filename)
    else:
        print('Error, variable %s not found' % plot_type)


def plot_temperature_max(projection, plot_type, temp_sparse, temp,
                         lons, lats, date, plot_filename='output.png'):
    import matplotlib.pyplot as plt
    '''Plot temperature on the map'''
    fig = plt.figure(1, figsize=(10, 10))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=temp_sparse,
                          projection=projection, lons=lons, lats=lats)

    plt.title('Temperature massime %s' % date)

    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(plt.gca(), temp, label='Temperatura [C]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_temperature_min(projection, plot_type, temp_sparse, temp,
                         lons, lats, date, plot_filename='output.png'):
    import matplotlib.pyplot as plt
    '''Plot temperature on the map'''
    fig = plt.figure(1, figsize=(10, 10))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=temp_sparse,
                          projection=projection, lons=lons, lats=lats)

    plt.title('Temperature minime %s' % date)

    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(plt.gca(), temp, label='Temperatura [C]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_rain(projection, rain_sparse, rain,
              lons, lats, date, plot_filename='output.png'):
    import matplotlib.pyplot as plt
    fig = plt.figure(1, figsize=(10, 10))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=rain_sparse, projection=projection, lons=lons, lats=lats,
                          minval=0, maxval=150, cmap='gist_stern_r')

    plt.title('Pioggia giornaliera %s' % date)

    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(plt.gca(), rain, label='Pioggia giornaliera [mm]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_gust(projection, gust_sparse, gust,
              lons, lats, date, plot_filename='output.png'):
    import matplotlib.pyplot as plt
    fig = plt.figure(1, figsize=(10, 10))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=gust_sparse, projection=projection, lons=lons, lats=lats,
                          minval=0, maxval=150, cmap='gist_stern_r')

    plt.title('Raffica massima giornaliera %s' % date)

    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(plt.gca(), gust, label='Raffica [kmh/h]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


if __name__ == "__main__":
    main()
