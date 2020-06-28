# meteonetwork webapp
Few scripts and utilities to download and process data from Meteonetwork weather stations (http://www.meteonetwork.it/rete/). The code contained here is used to deploy a simple web application built upon `Dask` which allows to create some simple plot/maps with daily data or live data from the weather stations network. It can be accessed here https://meteonetwork.herokuapp.com/

![Sample plotting output](https://i.imgur.com/ZxP4C6j.png)

Note that you need an account and an api-key to perform the api query (see https://www.meteonetwork.it/supporto/meteonetwork-api/). These need to be defined as environmental variable, `MNW_MAIL`, `MNW_TOKEN` and `MNW_BULK_TOKEN`. Otherwise the script will try to generate a new token using your email/username defined as `MNW_MAIL`, `MNW_USER`. 

The `utils.py` file contains most of the routines needed to filter and plot the values. 
The `api.py` file contains the `MNWApi` class needed to download the data from meteonetwork REST server. 




