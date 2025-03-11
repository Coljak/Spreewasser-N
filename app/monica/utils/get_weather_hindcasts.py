"""
This module automates the download of the hindcasts from ???
"""

from ftplib import FTP_TLS
import os
from datetime import datetime, date
import xarray as xr
import numpy as np
from .dwd_server import settings
from django.core.cache import cache

VARS = ['hurs', 'pr', 'rsds', 'sfcwind','tas', 'tasmax', 'tasmin']

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
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Always close the connection
        ftps.quit()


def get_last_valid_date(year):
    nc_path = f'monica/climate_netcdf/zalf_hurs_amber_{year}_v1-0.nc'
    ds = xr.open_dataset(nc_path)
    hurs = ds.hurs[:, 200, 200].values
    valid_indices = np.where(~np.isnan(hurs))[0]
    if valid_indices.size > 0:
        last_valid_index = valid_indices[-1] 
        last_valid_date = ds.time.values[last_valid_index] 
    else:
        last_valid_date = None
    return last_valid_date.astype('datetime64[D]').astype(datetime)


def get_last_valid_date_cached(update=False, next_year=False):
    last_valid_date = cache.get('last_valid_date')
    year = datetime.now().year
    if last_valid_date is None and update == False:
        last_valid_date = get_last_valid_date(year)
        cache.set('last_valid_date', last_valid_date, timeout=129600)  # Cache for 36 hours
    elif update == True:
        
        if next_year == True:
            year += 1
        last_valid_date = get_last_valid_date(year)
        cache.set('last_valid_date', last_valid_date, timeout=129600)

    return last_valid_date


def update_hindcast_data():
    year = datetime.now().year
    for var in VARS:
        remote_file_path = f'/DWD_SpreeWasser_N/zalf_{var}_amber_{year}_v1-0.nc'
        local_file_path = f'monica/climate_netcdf/zalf_{var}_amber_{year}_v1-0.nc'
        download_from_ftps(settings['host'], settings['username'], settings['password'], remote_file_path, local_file_path)

    last_valid_date = get_last_valid_date_cached(update=True)
    # if last valid date is the last day of the year, the forecast can be in the next year
    if last_valid_date is not None and last_valid_date.month == 12 and last_valid_date.day == 31:
        try:
            year += 1
            for var in VARS:
                remote_file_path = f'/DWD_SpreeWasser_N/zalf_{var}_amber_{year}_v1-0.nc'
                local_file_path = f'monica/climate_netcdf/zalf_{var}_amber_{year}_v1-0.nc'
                download_from_ftps(settings['host'], settings['username'], settings['password'], remote_file_path, local_file_path)
            
            get_last_valid_date_cached(update=True, next_year=True)
        except Exception as e:
            # This error should only occur if the last available date is dec 31st of the current year
            print(f"Error: {e}")

