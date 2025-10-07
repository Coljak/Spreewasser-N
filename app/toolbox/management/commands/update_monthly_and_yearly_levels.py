"""
With this command, monthly and yearly averages are produced or updated from the data saved in TimeseriesDailyWaterlevel."""
from django.core.management.base import BaseCommand
from django.db.models import Avg
from django.db.models.functions import TruncMonth, TruncYear
from toolbox import models

def aggregate_monthly(station_ids=None):
    qs = models.TimeseriesDailyWaterlevel.objects.all()
    if station_ids:
        qs = qs.filter(station_id__in=station_ids)

    monthly_qs = (
        qs
        .values('station')
        .annotate(date=TruncMonth('date'))
        .annotate(level_avg=Avg('level'))
    )

    for row in monthly_qs:
        models.TimeseriesMonthlyWaterlevel.objects.update_or_create(
            station_id=row['station'],
            month=row['date'],
            defaults={'level': row['level_avg']}
        )

def aggregate_yearly(station_ids=None):
    qs = models.TimeseriesDailyWaterlevel.objects.all()
    if station_ids:
        qs = qs.filter(station_id__in=station_ids)

    yearly_qs = (
        qs
        .values('station')
        .annotate(date=TruncYear('date'))
        .annotate(level_avg=Avg('level'))
    )

    for row in yearly_qs:
        models.TimeseriesYearlyWaterlevel.objects.update_or_create(
            station_id=row['station'],
            year=row['date'].year,
            defaults={'level': row['level_avg']}
        )

class Command(BaseCommand):
    help = 'Monthly and yearly averages are produced or updated for waterlevel timeseries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['monthly', 'yearly', 'both'],
            default='both',
            help="Choose which aggregation to run"
        )
        parser.add_argument(
            '--station',
            nargs='+',
            type=int,
            help="Station ID(s) to aggregate (space-separated). Default: all stations"
        )

    def handle(self, *args, **options):
        agg_type = options['type']
        station_ids = options.get('station')

        if agg_type in ('monthly', 'both'):
            aggregate_monthly(station_ids)
            self.stdout.write(self.style.SUCCESS('✅ Monthly aggregation done'))

        if agg_type in ('yearly', 'both'):
            aggregate_yearly(station_ids)
            self.stdout.write(self.style.SUCCESS('✅ Yearly aggregation done'))
