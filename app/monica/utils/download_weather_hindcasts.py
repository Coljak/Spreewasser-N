"""
This module automates the download of the hindcasts from ???
"""

from ftplib import FTP_TLS
import os
import xarray as xr
from django.core.cache import cache
from monica.utils import monica_constants
from django.conf import settings
from datetime import datetime

# TODO add a timeout if the download does not work/ continue7



def download_from_ftps(host, username, password, remote_file_path, local_file_path):
    print('download_from_ftps')
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
    


def correct_hindcast_chunking(filename):
    print('correct_hindcast_chunking: ', filename)
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
    # path = f'monica/climate_netcdf/{filename}'
    path = f'{settings.MONICA_NETCDF_HINDCAST_DIR}/{filename}'
    tmp_path = f'{path}.tmp'

    ds = xr.open_dataset(path, chunks=None)
    ds.to_netcdf(tmp_path, encoding=encoding)
    ds.close()
    os.replace(tmp_path, path)



def correct_dataset_units(local_file_path):
    """
    The values for rsds is scaled by 100 in the hindcast data. 
    The unit is wrongly stated as W m-2 instead of Wh m-2. 
    This function corrects the values and updates the units attribute in the NetCDF file.
    """
    print('correct_dataset_units: ', local_file_path)
    ds = xr.open_dataset(local_file_path)
    ds['rsds'] = ds['rsds'] * .01
    ds['rsds'].attrs['units'] = 'Wh m-2'
    ds.to_netcdf(local_file_path)
    


def process_year(year):
    print(f"Processing year: {year}")
    dwd_host = os.environ["DWD_HOST"]
    dwd_username = os.environ["DWD_USERNAME"]
    dwd_password = os.environ["DWD_PASSWORD"]
    dwd_port = int(os.environ["DWD_PORT"])
    for var in monica_constants.VARIABLES_LOWER:
        try:
            filename = f'zalf_{var}_amber_{year}_v1-0.nc'
            remote_file_path = f'/DWD_SpreeWasser_N/{filename}'
            # TODO replace
            local_file_path = f'monica/climate_netcdf/{filename}'
            locale_fp = f'{settings.MONICA_NETCDF_HINDCAST_DIR}/{filename}'

            download_from_ftps(
                dwd_host,
                dwd_username,
                dwd_password,
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
    
    last_valid_date = cache.get('last_valid_hindcast_date', None)
    current_year = datetime.now().year
    last_valid_year = last_valid_date.year if last_valid_date else None
    if last_valid_date is not None and current_year > last_valid_year:
        if not (last_valid_date.month == 12 and last_valid_date.day == 31):
            process_year(last_valid_year)
    if last_valid_date is None or current_year > last_valid_year:
        process_year(current_year)




def download_all_hindcast_data():

    year_now = datetime.now().year

    for year in range(monica_constants.START_YEAR, (year_now + 1)):
                       
        process_year(year)

    print('Done downloading hindcast data.')
    print('Rewrite chunking of netcdf files...')

    nc_files = [nc for nc in os.listdir('monica/climate_netcdf/') if nc.endswith('.nc')]
    for filename in nc_files:
        correct_hindcast_chunking(filename)

    print('Done rewriting chunking of netcdf files.')


