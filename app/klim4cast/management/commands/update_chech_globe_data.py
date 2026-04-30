import os

from ftplib import FTP
import paramiko
import shutil

import logging
from django.core.management.base import BaseCommand

from django.conf import settings
from .klim4cast_server_settings import sftp_server, sftp_user, sft_port, sftp_password
import os
from klim4cast.utils.tif_processing import process_tifs
from klim4cast.utils.tif_download import download_directory, list_dates

logging.basicConfig(
    filename='ftp_download.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


class Command(BaseCommand):
    help = "Connect to the CzechGlobe FTP server and download the latest data. Creation of NetCDF file from downloaded tif files."

    def handle(self, *args, **kwargs):
        try:
            sftp_server = settings.CLIM4CAST_FTP_SERVER
            sftp_user = settings.CLIM4CAST_SFTP_USER
            sft_port = settings.CLIM4CAST_SFTP_PORT
            sftp_password = settings.CLIM4CAST_SFTP_PASSWORD
            transport = paramiko.Transport((sftp_server, sft_port))
            transport.connect(username=sftp_user, password=sftp_password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            self.stdout.write("Connection successfully established ...")

            dates, latest_date = list_dates(sftp)
            self.stdout.write(f"Latest date on CheckGlobe FTP: {latest_date}\nDates: {dates}")

            # file_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            local_dir = settings.CLIM4CAST_DATA
            netcdf_dir = settings.CLIM4CAST_NETCDF_DIR
            downloaded_dates = os.listdir(local_dir)
            if downloaded_dates == []:
                self.stdout.write("No data downloaded yet ...")
                local_dates = None
            else:
                self.stdout.write(f"Already downloaded dates: {downloaded_dates}")
                local_dates = sorted(downloaded_dates)
            self.stdout.write(f"Local dates: {local_dates}")

            if not local_dates or local_dates[-1] < latest_date:
                local_dir = os.path.join(local_dir, latest_date)
                try:
                    self.stdout.write("Trying to download data from ChechGlobe FTP ...")
                    remote_dir = f"data/{latest_date}"
                    
                    download_directory(sftp, remote_dir, local_dir)
                    self.stdout.write("Data downloaded from ChechGlobe FTP ...")

                    data_dir = os.path.join(local_dir, 'Data')
                    
                except Exception as e:
                    self.stdout.write(f"Download from ChechGlobe FTP failed after connection was established: {e}")
                    shutil.rmtree(local_dir)

                try:
                    process_tifs(data_dir, netcdf_dir)
                    self.stdout.write("NetCDF file created ...")
                    shutil.rmtree(local_dir)
                except Exception as e:
                    self.stdout.write(f"Creation of NetCDF file failed: {e}")

            else:
                self.stdout.write("No new data on ChechGlobe FTP ...")

            sftp.close()
            transport.close()
            self.stdout.write("CheckGlobe FTP Connection closed ...")


        except Exception as e:
            self.stdout.write(f"Connection to CheckGlobe FTP failed: {e}")

                


