"""
With this code, the klimertrag seed and harvest data can be imported from the csv files into the swn database.
The command can be executed with the following command:
python manage.py import_seed_harvest_data(csv_file=<path_to_csv_file>, cultivar_name=<cultivar_name>)
"""

import csv
import django.core.management.base import BaseCommand
from monica.models import SeedHarvestData, SeedHarvestWinterWheat, CultivarParameters
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = 'Import seed and harvest data from klimertrtag csv files'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                climate_station = int(row['climate.station'])
                lat = float(row['lat'])
                lon = float(row['long'])
                crop_txt = row['crop']
                cultivar_parameters_id = CultivarParameters.objects.get(species_name=kwargs['cultivar_name']).id
                avg_sowing_doy = int(row['avg.sowing.doy'])
                sowing_values = int(row['X..values.sowing'])
                avg_harvest_doy = int(row['avg.harvest.doy'])
                harvest_values = int(row['X..values.harvest'])
                earliest_sowing_doy = int(row['earliest.sowing.doy'])
                latest_sowing_doy = int(row['latest.sowing.doy'])
                earliest_harvest_doy = int(row['earliest.harvest.doy'])
                latest_harvest_doy = int(row['latest.harvest.doy'])
                
                

                seed_harvest_data = SeedHarvestData.objects.create(
                    climate_station=climate_station,
                    lat=lat,
                    lon=lon,
                    crop_txt=crop_txt,
                    avg_sowing_doy=avg_sowing_doy,
                    sowing_values=sowing_values,
                    avg_harvest_doy=avg_harvest_doy,
                    harvest_values=harvest_values,
                    earliest_sowing_doy=earliest_sowing_doy,
                    latest_sowing_doy=latest_sowing_doy,
                    earliest_harvest_doy=earliest_harvest_doy,
                    latest_harvest_doy=latest_harvest_doy,
                    geom= Point(lon, lat)
                )
                SeedHarvestWinterWheat.objects.create(seedharvestdates_ptr=seed_harvest_data)

        self.stdout.write(self.style.SUCCESS('Successfully imported data'))