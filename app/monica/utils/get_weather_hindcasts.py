"""
This module automates the download of the hindcasts from ???
"""

from ftplib import FTP_TLS
import os
from datetime import datetime
from dwd_server import settings

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

def update_hindcast_data():
    new_files = [ ]
    year = datetime.now().year
    for var in VARS:
        remote_file_path = f'/DWD_SpreeWasser_N/zalf_{var}_amber_{year}_v1-0.nc'
        local_file_path = f'climate_netcdf/zalf_{var}_amber_{year}_v1-0.nc'
        download_from_ftps(settings['host'], settings['username'], settings['password'], remote_file_path, local_file_path)