"""
With this command, the forecast data can be downloaded and is conerted to combined NetCDF files."""

from django.core.management.base import BaseCommand
import xarray as xr
import numpy as np
import dask.array as da
import os
from datetime import datetime
from monica.utils.get_weather_forecast import automated_thredds_download

class Command(BaseCommand):
    help = 'Download forecast data and convert to a combined NetCDF'

    def handle(self, *args, **kwargs):
        automated_thredds_download()

        self.stdout.write(self.style.SUCCESS('Successfully downloaded forecast data'))