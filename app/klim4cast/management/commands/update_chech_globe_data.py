import os

from ftplib import FTP
import paramiko
import shutil

import logging
from django.core.management.base import BaseCommand
from .klim4cast_server_settings import sftp_server, sftp_user, sft_port, sftp_password
from klim4cast.utils.tif_processing import process_tifs
from klim4cast.utils.tif_download import download_directory, list_dates

logging.basicConfig(
    filename='ftp_download.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


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
            local_dates = sorted(os.listdir(local_dir))
            self.stdout.write(f"Local dates: {local_dates}")

            if not local_dates or local_dates[-1] < latest_date:
                local_dir = os.path.join(local_dir, latest_date)
                try:
                    self.stdout.write("Trying to download data from CheckGlobe FTP ...")
                    remote_dir = f"data/{latest_date}"
                    
                    download_directory(sftp, remote_dir, local_dir)
                    self.stdout.write("Data downloaded from CheckGlobe FTP ...")

                    data_dir = os.path.join(local_dir, 'Data')
                    
                except Exception as e:
                    self.stdout.write(f"Download from CheckGlobe FTP failed after connection was established: {e}")
                    shutil.rmtree(local_dir)

                try:
                    process_tifs(data_dir, netcdf_dir)
                    self.stdout.write("NetCDF file created ...")
                    shutil.rmtree(local_dir)
                except Exception as e:
                    self.stdout.write(f"Creation of NetCDF file failed: {e}")

            else:
                self.stdout.write("No new data on CheckGlobe FTP ...")

            sftp.close()
            transport.close()
            self.stdout.write("CheckGlobe FTP Connection closed ...")


        except Exception as e:
            self.stdout.write(f"Connection to CheckGlobe FTP failed: {e}")

                


