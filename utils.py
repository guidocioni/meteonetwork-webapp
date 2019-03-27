# Common libraries for meteonetwork/meteoindiretta plotting routines
import requests
from lxml import etree
import numpy as np
import pandas as pd
import matplotlib.colors as mplcolors
import matplotlib.cm as mplcm
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib._png import read_png
from matplotlib import patheffects
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import importlib

import credentials

api_key = credentials.api_key
user = credentials.user

rest_url="http://api.meteonetwork.it/xml_rpc/public/rest"

def download_coordinates_stations(filename='stazioni_coordinate.csv'):
    ''' Update the text file containing the coordinates of the 
    stations. Since stations do not change quite often it's not necessary
    to do this update every time.'''
    method="getStationsInfo"
    url = (rest_url+"?method=%s&username=%s&token=%s" % (method, user, api_key))
    response = requests.get(url)
    root=etree.fromstring(response.content)

    station_ids = get_field_root(root, field="code", type="string")
    lons = get_field_root(root, field="longitude", type="float")
    lats = get_field_root(root, field="latitude", type="float")

    # Save coordinates to csv for later use
    df = pd.DataFrame(data={'station_id': station_ids,
                    'longitude': lons, 'latitude': lats})
    df.to_csv(filename)

def get_field_root(root, field="temperature", type="float"):
    '''Iterate through a element tree XML root got from a 
    response content.  '''
    variable=[]
    for temp in root.iter(field):
        variable.append(temp.text)

    if type != "string":
        return(np.array(variable).astype(type))
    else:
        return(variable)

def get_daily_values(date_download='2018-10-03'):
    '''Get daily station values using the getDailyStationsSingleDate method.
    Returns a dataframe with all the data.'''
    method="getDailyStationsSingleDate"
    url = (rest_url+"?method=%s&username=%s&token=%s&data=%s" % 
        (method, user, api_key, date_download))
    response = requests.get(url)
    root=etree.fromstring(response.content)

    station_ids = get_field_root(root, field="station_code", type="string")
    datetime = get_field_root(root, field="observation_date", type="string")
    t_min = get_field_root(root, field="t_min", type="float")
    t_med = get_field_root(root, field="t_med", type="float")
    t_max = get_field_root(root, field="t_max", type="float")
    rh_min = get_field_root(root, field="rh_min", type="float")
    rh_med = get_field_root(root, field="rh_med", type="float")
    rh_max = get_field_root(root, field="rh_max", type="float")
    rain = get_field_root(root, field="rain", type="float")
    w_med = get_field_root(root, field="w_med", type="float")
    w_max = get_field_root(root, field="w_max", type="float")
    w_dir = get_field_root(root, field="w_max", type="string")
    slpres = get_field_root(root, field="slpres", type="float")
    rad_med = get_field_root(root, field="rad_med", type="float")
    rad_max = get_field_root(root, field="rad_max", type="float")
    uv_med = get_field_root(root, field="uv_med", type="float")
    uv_max = get_field_root(root, field="uv_max", type="float")

    df = pd.DataFrame(data={'station_id': station_ids,'date': datetime,
        'temp min': t_min, 'temp max': t_max, 'temp med': t_med,
        'hum min': rh_min, 'hum max': rh_max, 'hum med': rh_med,
        'wind dir': w_dir, 'wind max': w_max, 'wind med': w_med,
        'pres': slpres, 'rad med': rad_med, 'rad max': rad_max,
        'uv med': uv_med, 'uv max': uv_max, 'rain': rain })

    return(df)

def get_realtime_values():
    '''Get realtime values from the REST api and returns a dataframe.'''
    method="getRealtimeStationsLastData"
    url = (rest_url+"?method=%s&username=%s&token=%s" % 
    (method, user, api_key))
    response = requests.get(url)
    root = etree.fromstring(response.content)
    # Elementi 
    fields = ['station_id','datetime','datetime_utc','temperature','smlp',
                'rh', 'wind_speed', 'wind_direction', 'wind_gust','rain_rate',
                'daily_rain','dew_point','rad','uv']

    datetime = get_field_root(root, field="datetime", type="string")
    station_ids = get_field_root(root, field="station_id", type="string")
    temperature = get_field_root(root, field="temperature", type="float")
    rh = get_field_root(root, field="rh", type="float")
    smlp = get_field_root(root, field="smlp", type="float")
    wind_speed = get_field_root(root, field="wind_speed", type="float")
    wind_direction = get_field_root(root, field="wind_direction", type="float")
    wind_gust = get_field_root(root, field="wind_gust", type="float")
    rain_rate = get_field_root(root, field="rain_rate", type="float")
    daily_rain = get_field_root(root, field="daily_rain", type="float")
    dew_point = get_field_root(root, field="dew_point", type="float")
    rad = get_field_root(root, field="rad", type="float")
    uv = get_field_root(root, field="uv", type="float")

    df = pd.DataFrame(data={'station_id': station_ids,'date': datetime,
        'temperature': temperature, 'humidity': rh, 'pressure': smlp,
        'wind_speed': wind_speed, 'wind_gust': wind_gust, 'wind_direction':wind_direction,
        'rain_rate': rain_rate, 'daily_rain': daily_rain,'dew_point': dew_point,
        'radiation': rad, 'uv radiation': uv})

    return(df)

def filter_values(var, lats, lons, max_density=1.5, num_bins=61):
    '''Attempts to remove overlapping points by binning the results and 
    removing stations within a box with a certain density. For now the algorithm
    just randomly choose one of the station in the box.
    Returns the new array of the input array.'''

    var_sparse=np.copy(var)
    # First compute density of stations
    lon_bins = np.linspace(lons.min(), lons.max(), num_bins) 
    lat_bins = np.linspace(lats.min(), lats.max(), num_bins) #
    density, xedges, yedges= np.histogram2d(lats, lons, [lat_bins, lon_bins])

    # Then loop throught the boxes in the histogram and put np.NaN 
    # in all but one of the stations that pertain to that box 
    for i,j in zip(np.where(density > max_density)[0],np.where(density > max_density)[1]):
        indices=np.where((lons<=yedges[j+1]) & (lons>=yedges[j]) & (xedges[i]<=lats) & (lats<=xedges[i+1]))[0]
        #Select all points but one to be masked 
        var_sparse[indices[np.arange(len(indices))!=1]]=np.nan

    return(var_sparse)

def filter_max_values(var, lats, lons, max_density=1.5, num_bins=61):
    '''Attempts to remove overlapping points by binning the results and 
    removing stations within a box with a certain density. Differently
    from what is done in filter_values, here the maximum value is 
    preserved within a cell.
    Returns the new array of the input array.'''

    var_sparse=np.copy(var)
    # First compute density of stations
    lon_bins = np.linspace(lons.min(), lons.max(), num_bins) 
    lat_bins = np.linspace(lats.min(), lats.max(), num_bins) #
    density, xedges, yedges= np.histogram2d(lats, lons, [lat_bins, lon_bins])

    # Then loop throught the boxes in the histogram and put np.NaN 
    # in all but one of the stations that pertain to that box 
    for i,j in zip(np.where(density > max_density)[0],np.where(density > max_density)[1]):
        indices=np.where((lons<=yedges[j+1]) & (lons>=yedges[j]) & (xedges[i]<=lats) & (lats<=xedges[i+1]))[0]
        #Select all points but one to be masked
        # check before if the slice is all NaNs
        if not np.isnan(var_sparse[indices]).sum() == len(var_sparse[indices]):
            var_sparse[indices[np.arange(len(indices))!= np.nanargmax(var_sparse[indices])]] = np.nan

    return(var_sparse)

def filter_min_values(var, lats, lons, max_density=1.5, num_bins=61):
    '''Attempts to remove overlapping points by binning the results and 
    removing stations within a box with a certain density. Differently
    from what is done in filter_values, here the minimum value is 
    preserved within a cell.
    Returns the new array of the input array.'''

    var_sparse=np.copy(var)
    # First compute density of stations
    lon_bins = np.linspace(lons.min(), lons.max(), num_bins) 
    lat_bins = np.linspace(lats.min(), lats.max(), num_bins) #
    density, xedges, yedges= np.histogram2d(lats, lons, [lat_bins, lon_bins])

    # Then loop throught the boxes in the histogram and put np.NaN 
    # in all but one of the stations that pertain to that box 
    for i, j in zip(np.where(density > max_density)[0],np.where(density > max_density)[1]):
        indices=np.where((lons<=yedges[j+1]) & (lons>=yedges[j]) & (xedges[i]<=lats) & (lats<=xedges[i+1]))[0]
        #Select all points but one to be masked
        # check before if the slice is all NaNs
        if not np.isnan(var_sparse[indices]).sum() == len(var_sparse[indices]):
            var_sparse[indices[np.arange(len(indices))!= np.nanargmin(var_sparse[indices])]] = np.nan

    return(var_sparse)

def get_projection(plt, projection='italy', regions=False):
    '''Retrieve the projection using cartopy'''
    # Fist check if we have cartopy, otherwise just plot on a background image,
    # which hopefully has the same extents...
    if (importlib.util.find_spec("cartopy") is not None):
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        
        ax = plt.axes(projection=ccrs.PlateCarree())

        if projection== 'italy':
            ax.set_extent([6, 19, 36, 48], ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='#64B6AC')
        ax.add_feature(cfeature.LAKES.with_scale('50m'), facecolor='#2081C3')
        ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='#2081C3')
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linestyle='-', alpha=.5,
                   edgecolor='white', linewidth=2.)

        if regions:
            states_provinces = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_1_states_provinces_lines',
                scale='10m',
                facecolor='none')
            ax.add_feature(states_provinces, edgecolor='white', alpha=.5)

        return(ax)
    else:
        return(add_background(plt, projection))

def add_background(plt, projection, image='background.png'):
    ''''Add a background image to the plot'''
    if projection == 'italy':
        extents = [6.000000000000001, 19.0, 36.0, 48.00000000000001]
    
    img = plt.imread(image)
    plt.axis('off')
    plt.imshow(img, zorder=0, extent=extents)

    return(plt.gca())

def add_vals_on_map(ax, projection, var, lons, lats, minval=None, maxval=None,
                     cmap='rainbow', border=True, shift_x=0., shift_y=0., fontsize=12, colors=True):
    '''Given an input projection, a variable containing the values and a plot put
    the values on a map exlcuing NaNs and taking care of not going
    outside of the map boundaries, which can happen.
    - minval, maxval set the extents for the colorscale cmap
    - border activates the border on the text labels
    - shift_x and shift_y apply a shifting offset to all text labels
    - colors indicate whether the colorscale cmap should be used to map the values of the array'''
    if not minval:
        minval = np.nanmin(var)
    if not maxval:
        maxval = np.nanmax(var)

    norm = mplcolors.Normalize(vmin=minval, vmax=maxval)
    m = mplcm.ScalarMappable(norm=norm, cmap=cmap)

    if (importlib.util.find_spec("cartopy") is not None):
        extents = ax.get_extent()
    else:
        if projection == 'italy':
            extents = [6.000000000000001, 19.0, 36.0, 48.00000000000001]
    
    lon_min, lon_max, lat_min, lat_max = extents

    texts=[]
    for i, txt in enumerate(var):
        if colors:
            if not(np.isnan(txt)) and (lon_min<=lons[i]<=lon_max) and (lat_min<=lats[i]<=lat_max):
                texts.append(ax.text(lons[i]+shift_x, lats[i]+shift_y, ('%d'%txt),
                 color=m.to_rgba(float(txt)), weight='bold', fontsize=fontsize))
        else:
            if not(np.isnan(txt)) and (lon_min<=lons[i]<=lon_max) and (lat_min<=lats[i]<=lat_max):
                texts.append(ax.text(lons[i]+shift_x, lats[i]+shift_y, ('%d'%txt),
                 color='black', weight='bold', fontsize=fontsize))            
    # Add border to the text
    if border: 
        [text.set_path_effects([patheffects.Stroke(linewidth=1, foreground='black'), patheffects.Normal()]) for text in texts]

def add_logo_on_map(ax, logo, zoom=0.15, pos=(0.92, 0.1)):
    '''Add a logo on the map given a pnd image, a zoom and a position
    relative to the axis ax.'''
    img_logo=OffsetImage(read_png(logo), zoom=zoom)
    logo_ann = AnnotationBbox(img_logo, pos, xycoords='axes fraction',frameon=False)
    ax.add_artist(logo_ann)

def add_hist_on_map(ax, var, width="30%", height="15%", loc=1, label='Temperatura [C]'):
    '''Add an histogram of the variable on the map, specifying the location.
    Unfortunately face color has to be hardcoded while I understand how can
    one retrieve the  color of the fillcontinents method from basemap.'''
    axin = inset_axes(ax, width=width, height=height, loc=loc)
    axin.hist(var[~np.isnan(var)], bins=50, normed=True, color='black', alpha=0.7)
    axin.yaxis.set_visible(False)
    axin.spines['right'].set_visible(False)
    axin.spines['left'].set_visible(False)
    axin.spines['top'].set_visible(False)
    axin.set_xlabel(label)
    # axin.set_facecolor('#64B6AC', alpha=0.1)
    axin.set_facecolor((0, 0, 0, 0))


