"""
This is all about loading the hindcast and forecast, cashing it and retrieving it.
"""

import xarray as xr
from datetime import datetime
from monica.utils import monica_constants
from monica import models
from pathlib import Path
from django.core.cache import cache
import numpy as np
import glob
from django.conf import settings

# Create a cached mapping of hindcast to forecast indices and vice versa. Forecasts map to a set of hindcasts.

HINDCAST_TO_FORECAST_INDEX = None
FORECAST_TO_HINDCASTS_INDEX = None

def get_hindcast_forecast_index_mappings():
    global HINDCAST_TO_FORECAST_INDEX, FORECAST_TO_HINDCASTS_INDEX
    if HINDCAST_TO_FORECAST_INDEX is None:
        HINDCAST_TO_FORECAST_INDEX, FORECAST_TO_HINDCASTS_INDEX = models.DWDGridToPointIndices.build_index_mappings_as_array()

    return HINDCAST_TO_FORECAST_INDEX, FORECAST_TO_HINDCASTS_INDEX

# Caching hindcast and forecast
FORECAST = None
FORECAST_START_DATE = None
FORECAST_END_DATE = None
HINDCAST = None
HINDCAST_LAST_DATE = None

def load_hindcast():
    climate_data_path = settings.MONICA_NETCDF_HINDCAST_DIR

    this_year = datetime.now().year


    path_list = []
    for _, value in monica_constants.CLIMATE_VARIABLES.items():

        for year in range(monica_constants.START_YEAR, this_year + 1):
            file_path = f"{climate_data_path}/zalf_{value.lower()}_amber_{year}_v1-0.nc"
            path_list.append(file_path)


    hindcast = xr.open_mfdataset(
            path_list,
            combine='by_coords',
            chunks={'time': 61},
            parallel=False
        )
    return hindcast


def load_forecast(scenario):
    """
    Initializes a lazily-loaded xarray dataset for reuse across requests.
    This function loads the NetCDF files for each forecast scenario.
    This is done to avoid opening and closing the files for each request.
    """
    climate_data_path = settings.MONICA_NETCDF_FORECAST_DIR
    print(' climate_data_path: ', type(climate_data_path), climate_data_path)
    # TODO - deal with multiple scenarios!!

    files = glob.glob(f"{climate_data_path}/forecast_{scenario}_*.nc")
    print(f"Found forecast files: {files}")

    file_path = files[0] # get the latest scenario if multiple exist
    
    forecast = xr.open_dataset(
            file_path,
            chunks={'time': 61},
        )

    return forecast

def get_forecast(scenario):
    global FORECAST
    if FORECAST is None:
        FORECAST = load_forecast(scenario)
    return FORECAST

def get_hindcast():
    """
    scenario: str, one of the scenarios defined in monica_constants.SCENARIOS
    """
    global HINDCAST
    if HINDCAST is None:
        HINDCAST = load_hindcast()
        # set the last valid date for the hindcast data, which is needed to determine if new data needs to be downloaded
        set_hindcast_last_valid_date(HINDCAST)

    return HINDCAST

def reload_all():
    global FORECAST, HINDCAST
    FORECAST = None
    HINDCAST = None

def set_hindcast_last_valid_date(hindcast):
    hindcast = hindcast
    hurs = hindcast.hurs.isel(time=slice(-365, None), lat=200, lon=200)
    vals = hurs.values
    valid_indices = np.where(~np.isnan(vals))[0]
    if valid_indices.size > 0:
        last_valid_index = valid_indices[-1] 
        last_valid_date = hindcast.time.values[last_valid_index] 
        last_valid_date = last_valid_date.astype('datetime64[D]').astype(datetime)
        cache.set('last_valid_hindcast_date', last_valid_date, timeout=129600)
        return last_valid_date


def get_last_valid_hindcast_dates():
    last_valid_date = cache.get('last_valid_hindcast_date', None)
    if last_valid_date is None: 
       hindcast = get_hindcast()      
       last_valid_date = set_hindcast_last_valid_date(hindcast)
    return last_valid_date

def set_forecast_valid_date(forecast):
    times = forecast.time[:].values
    last_valid_date = times[-1]
    last_valid_date = last_valid_date.astype('datetime64[D]').astype(datetime)
    first_valid_date = times[0]
    first_valid_date = first_valid_date.astype('datetime64[D]').astype(datetime)
    cache.set('first_valid_forecast_date', first_valid_date, timeout=129600)
    cache.set('last_valid_forecast_date', last_valid_date, timeout=129600)
    return first_valid_date, last_valid_date


def get_last_valid_forecast_date():
    first_valid_date = cache.get('first_valid_forecast_date', None)
    last_valid_date = cache.get('last_valid_forecast_date', None)
    if last_valid_date is None or first_valid_date is None: 
       forecast = get_forecast(monica_constants.SCENARIOS[0])      
       first_valid_date, last_valid_date = set_forecast_valid_date(forecast)
    return first_valid_date, last_valid_date



def get_hindcast_subset(hindcast_start_date, hindcast_end_date):
    """"
    hindcast_start_date: str, in the format 'YYYY-MM-DD'
    hindcast_end_date: str, in the format 'YYYY-MM-DD'
    scenario: str, one of the scenarios defined in monica_constants.SCENARIOS
    """
    hindcast = get_hindcast()
    hindcast_subset = hindcast.sel(time=slice(hindcast_start_date, hindcast_end_date))
    return hindcast_subset

def get_monica_forecast_subset(forecast_start_date, forecast_end_date, scenario):
    """
    forecast_start_date: str, in the format 'YYYY-MM-DD'
    forecast_end_date: str, in the format 'YYYY-MM-DD'
    scenario: str, one of the scenarios defined in monica_constants.SCENARIOS
    """
    forecast = get_forecast(scenario)
    forecast_subset = forecast.sel(time=slice(forecast_start_date, forecast_end_date))
    return forecast_subset


def get_monica_hindcast_json_per_point(hindcast_start_date, hindcast_end_date, lat_idx, lon_idx):
    """
    This is optimized for point calculations (user's location) and returns the climate data as a JSON object for the given time range and location.
    hindcast_start_date: str, in the format 'YYYY-MM-DD'
    hindcast_end_date: str, in the format 'YYYY-MM-DD'
    lat_idx: int, latitude index for the location of interest
    lon_idx: int, longitude index for the location of interest
    """
    hindcast = get_hindcast_subset(hindcast_start_date, hindcast_end_date)
    point = hindcast.isel(lat=lat_idx, lon=lon_idx).load()
    climate_json = {}
    for key, val in monica_constants.CLIMATE_VARIABLES.items():

        climate_json[key] = point[val][:].values.tolist() 
    return climate_json

def get_monica_forecast_json_per_point(forecast_start_date, forecast_end_date, lat_idx, lon_idx, scenario, hindcast_indices=True):
    """
    This is optimized for point calculations (user's location) and returns the climate data as a JSON object for the given time range and location.
    forecast_start_date: str, in the format 'YYYY-MM-DD'
    forecast_end_date: str, in the format 'YYYY-MM-DD'
    lat_idx: int, latitude index for the location of interest
    lon_idx: int, longitude index for the location of interest
    scenario: str, one of the scenarios defined in monica_constants.SCENARIOS
    hindcast_indices: bool, whether the lat/lon indices are based on the hindcast or forecast grid (default: True, because all other data is based on the hindcast grid)
    """
    forecast = get_monica_forecast_subset(forecast_start_date, forecast_end_date, scenario)
    print('indices before conversion: ', lat_idx, lon_idx)
    hincast_to_forecast_index, forecast_to_hindcast_index = get_hindcast_forecast_index_mappings()
    if hindcast_indices:
        lat_idx, lon_idx = hincast_to_forecast_index[lat_idx, lon_idx]

    print('indices after conversion: ', lat_idx, lon_idx)

    point = forecast.isel(lat=lat_idx, lon=lon_idx).load()
    climate_json = {}
    for key, val in monica_constants.CLIMATE_VARIABLES.items():

        climate_json[key] = point[val][:].values.tolist() 
    return climate_json




