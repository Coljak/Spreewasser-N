"""
With this command, the forecast data can be downloaded and is conerted to combined NetCDF files.
"""

from django.core.management.base import BaseCommand
from monica.utils.get_weather_hindcasts import download_all_hindcast_data
from monica.services.climate_store import reload_all

"""
!!!!!!!!!!!!!! DOES NOT WORK FROM ZALF GUEST NETWORK !!!!!!!!!!!!!!!
"""
class Command(BaseCommand):
    help = 'Download hindcast data'

    def handle(self, *args, **kwargs):
        download_all_hindcast_data()
        reload_all()
        self.stdout.write(self.style.SUCCESS('Successfully downloaded all hindcast data'))