import os
from datetime import datetime, timedelta
from ftplib import FTP
import paramiko
import stat
import logging
from django.core.management.base import BaseCommand
from klim4cast.management.commands.klim4cast_server_settings import sftp_server, sftp_user, sft_port, sftp_password
from klim4cast.tif_processing import process_tifs


logging.basicConfig(
    filename='ftp_download.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def download_directory(sftp, remote_dir, local_dir):
    """
    The data on the ftp server is organized in directories in the /data folder.
    The directories are named with the iso dates. This function takes as input the sftp connection, 
    the remote directory (e.g. 'data/2024-06-30') and the local path where the data should be downloaded to ('./../../data/chech_globe_data/<ISO-date>).
    """

    print(f"Recursion: Downloading {remote_dir} to {local_dir}")
    for entry in sftp.listdir_attr(remote_dir):
        remote_path = f"{remote_dir}/{entry.filename}"
        local_path = os.path.join(local_dir, entry.filename)
        if stat.S_ISDIR(entry.st_mode):
            os.makedirs(local_path, exist_ok=True)
            download_directory(sftp, remote_path, local_path)
        else:
            sftp.get(remote_path, local_path)


def is_iso_date(filename):
    """
    Checks if a string is a valid ISO 8601 date
    """
    try:
        datetime.fromisoformat(filename)
        return True
    except ValueError:
        return False
    

def list_dates(sftp):
    """
    List all the dates in the 'data' directory on the sftp server
    """    
    file_paths = []
    dates = []
    sftp_list = sftp.listdir_attr('data')
    for file in sftp_list:
        if stat.S_ISDIR(file.st_mode) and is_iso_date(file.filename):
            dates.append(file.filename)
            
    latest_date = sorted(dates)[-1]

    return dates, latest_date

class Command(BaseCommand):
    help = "Connect to the CheckGlobe FTP server and download the latest data. Creation of NetCDF file from downloaded tif files."

    def handle(self, *args, **kwargs):
        try:
            transport = paramiko.Transport((sftp_server, sft_port))
            transport.connect(username=sftp_user, password=sftp_password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            self.stdout.write("Connection successfully established ...")

            dates, latest_date = list_dates(sftp)
            self.stdout.write(f"Latest date on CheckGlobe FTP: {latest_date}\nDates: {dates}")

            file_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            local_dir = os.path.join(file_dir, 'data', 'chech_globe_data')
            netcdf_dir = os.path.join(file_dir, 'data', 'netcdf')
            local_dates = os.listdir(local_dir)
            self.stdout.write(f"Local dates: {local_dates}")

            if not local_dates or local_dates[-1] < latest_date:
                try:
                    self.stdout.write("Trying to download data from CheckGlobe FTP ...")
                    remote_dir = f"data/{latest_date}"
                    local_dir = os.path.join(local_dir, latest_date)
                    download_directory(sftp, remote_dir, local_dir)
                    self.stdout.write("Data downloaded from CheckGlobe FTP ...")
                    data_dir = os.path.join(local_dir, 'Data')
                    # netcdf_dir = '/app/thredds_data/data/Klim4Cast'
                    process_tifs(data_dir, netcdf_dir)
                    self.stdout.write("NetCDF file created ...")
                except Exception as e:
                    self.stdout.write(f"Download from CheckGlobe FTP failed after connection was established: {e}")
                    os.rmdir(local_dir)
            else:
                self.stdout.write("No new data on CheckGlobe FTP ...")

            sftp.close()
            transport.close()
            self.stdout.write("CheckGlobe FTP Connection closed ...")
        except Exception as e:
            self.stdout.write(f"Connection to CheckGlobe FTP failed: {e}")

# def main():
#     """
#     Connect to the CheckGlobe FTP server and download the latest data.
#     Creation of NetCDF file from downloaded tif files.
#     """

#     try:
#         transport = paramiko.Transport((sftp_server, sft_port))
#         transport.connect(username=sftp_user, password=sftp_password)
#         sftp = paramiko.SFTPClient.from_transport(transport)
#         print("Connection successfully established ...")

#         dates, latest_date = list_dates(sftp)
#         print(f"Latest date on CheckGlobe FTP: {latest_date}\nDates: {dates}")

#         # local_dirs = os.listdir('./../../data/chech_globe_data')
#         file_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#         print("file_dir", file_dir)
#         local_dir = os.path.join(file_dir, 'data', 'chech_globe_data')
#         netcdf_dir = os.path.join(file_dir, 'data', 'netcdf')
#         print("local_dir", local_dir)
#         local_dates = os.listdir(local_dir)
#         print("local_dates", local_dates)

#         if not local_dates or local_dates[-1] < latest_date:
#             try:
#                 print("Trying to download data from CheckGlobe FTP ...")
#                 remote_dir = f"data/{latest_date}"
#                 local_dir = os.path.join(local_dir, latest_date)
#                 download_directory(sftp, remote_dir, local_dir)
#                 print("Data downloaded from CheckGlobe FTP ...")
#                 data_dir = os.path.join(local_dir, 'Data')
#                 output_dir = '/thredds_data/data/Klim4Cast'
#                 process_tifs(data_dir, output_dir)
#                 print("NetCDF file created ...")
#             except Exception as e:
#                 print(e)
#                 print("Download from CheckGlobe FTP failed after connection was established...")
#                 os.rmdir(local_dir)
                
#         else:
#             print("No new data on CheckGlobe FTP ...")

#         sftp.close()
#         transport.close()
#         print("CheckGlobe FTP Connection closed ...")
#     except Exception as e:
#         print(e)
#         print("Connection to CheckGlobe FTP failed ...")

    
        
                


