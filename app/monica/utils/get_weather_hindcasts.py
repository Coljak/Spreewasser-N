"""
This module automates the download of the hindcasts from ???
"""

from ftplib import FTP_TLS
import os
from datetime import datetime, date, timedelta
import xarray as xr
import numpy as np
from .dwd_server import settings
from django.core.cache import cache
from monica.utils import monica_constants
from app import settings


# TODO add a timeout if the download does not work/ continue7



def download_from_ftps(host, username, password, remote_file_path, local_file_path):
    """
    Download a file from an FTPS server.
    
    :param host: FTPS server address
    :param username: FTPS username
    :param password: FTPS password
    :param remote_file_path: Path to the file on the FTPS server
    :param local_file_path: Path to save the file locally
    """

    try:
        # Connect to FTPS server
        ftps = FTP_TLS(host)
        ftps.login(user=username, passwd=password)
        ftps.prot_p()  # Secure the data connection (uses explicit FTPS)

        # Ensure the directory for the local file exists
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Download the file
        with open(local_file_path, 'wb') as f:
            ftps.retrbinary(f"RETR {remote_file_path}", f.write)

        print(f"Download complete: {local_file_path}")
        ftps.quit()
    
    except Exception as e:
        print(f"Error: {e}")
    

        


def get_last_valid_date():
    """
    Gets the last valid date from the NetCDF file for the given year.
    It is used to get the latest date, for wich hindcast data is available. 
    returns the last valid date as a datetime object.
    """
    year = datetime.now().year
    try:
        nc_path = f'monica/climate_netcdf/zalf_hurs_amber_{year}_v1-0.nc'
    except Exception as e:
        try:
            nc_path = f'monica/climate_netcdf/zalf_hurs_amber_{year-1}_v1-0.nc'
        except Exception as e:
            print(f"Error: {e}")
            return None

    ds = xr.open_dataset(nc_path)
    hurs = ds.hurs[:, 200, 200].values
    valid_indices = np.where(~np.isnan(hurs))[0]
    if valid_indices.size > 0:
        last_valid_index = valid_indices[-1] 
        last_valid_date = ds.time.values[last_valid_index] 
    else:
        last_valid_date = None
    return last_valid_date.astype('datetime64[D]').astype(datetime)


def get_last_valid_date_cached():
    """
    This sets the cached 'last_valid_date' to the last valid date from the NetCDF file.
    """
    last_valid_date = cache.get('last_valid_date')
    yesterday = datetime.now() - timedelta(days=1)
    if last_valid_date is None or last_valid_date < yesterday:
        last_valid_date = get_last_valid_date()
    year = datetime.now().year
    if last_valid_date is None:
        last_valid_date = get_last_valid_date(year)
        cache.set('last_valid_date', last_valid_date, timeout=129600)  # Cache for 36 hours
    

    return last_valid_date

def correct_hindcast_chunking(filename):
    vari = filename.split('_')[1]
    if vari == 'sfcwind':
        vari = 'sfcWind'
    encoding = {
        vari: {
            'chunksizes': (61, 145, 109), 
            'zlib': True, 
            'complevel': 4 
        }}
    # TODO - replace
    path = f'monica/climate_netcdf/{filename}'
    locale_fp = f'{settings.MONICA_NETCDF_HINDCAST_DIR}/{filename}'
    ds = xr.open_dataset(path, chunks=None)
    ds.to_netcdf(path, encoding=encoding)

def correct_dataset_units(local_file_path):
    ds = xr.open_dataset(local_file_path)
    ds['rsds'] = ds['rsds'] * .01
    ds.to_netcdf(local_file_path)
    


def process_year(year):
    for var in monica_constants.VARIABLES_LOWER:
        try:
            filename = f'zalf_{var}_amber_{year}_v1-0.nc'
            remote_file_path = f'/DWD_SpreeWasser_N/{filename}'
            # TODO replace
            local_file_path = f'monica/climate_netcdf/{filename}'
            locale_fp = f'{settings.MONICA_NETCDF_HINDCAST_DIR}/{filename}'

            download_from_ftps(
                settings['host'],
                settings['username'],
                settings['password'],
                remote_file_path,
                local_file_path
            )

            if var == 'rsds':
                correct_dataset_units(local_file_path)
            correct_hindcast_chunking(filename)

        except Exception as e:
            # This error should only occur if the last available date is dec 31st of the current year
            print(f"Error: {e}")



def update_hindcast_data():
    year = datetime.now().year
    last_valid_date = cache.get('last_valid_date')
    # if last valid date is the last day of the year, the hindcast can be in the previous year
    if last_valid_date is not None and last_valid_date.month == 12 and last_valid_date.day == 31:
        year -= 1
    process_year(year)



def download_all_hindcast_data():
    start_year = 2007
    year_now = datetime.now().year

    for year in range(start_year, (year_now + 1)):
                       
        for var in monica_constants.VARIABLES_LOWER:
            remote_file_path = f'/DWD_SpreeWasser_N/zalf_{var}_amber_{year}_v1-0.nc'
            local_file_path = f'monica/climate_netcdf/zalf_{var}_amber_{year}_v1-0.nc'
            download_from_ftps(settings['host'], settings['username'], settings['password'], remote_file_path, local_file_path)

    
        try:
            year += 1
            remote_file_path = f'/DWD_SpreeWasser_N/zalf_{var}_amber_{year}_v1-0.nc'
            local_file_path = f'monica/climate_netcdf/zalf_{var}_amber_{year}_v1-0.nc'
            download_from_ftps(settings['host'], settings['username'], settings['password'], remote_file_path, local_file_path)
            
        except Exception as e:
            # This error should only occur if the last available date is dec 31st of the current year
            print(f"Error: {e}")

    print('Done downloading hindcast data.')
    print('Rewrite chunking of netcdf files...')

    nc_files = [nc for nc in os.listdir('monica/climate_netcdf/') if nc.endswith('.nc')]
    for filename in nc_files:
        correct_hindcast_chunking(filename)

    print('Done rewriting chunking of netcdf files.')
