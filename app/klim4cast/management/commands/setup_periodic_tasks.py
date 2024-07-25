# app/klim4cast/management/commands/setup_periodic_tasks.py
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

class Command(BaseCommand):
    help = 'Setup periodic tasks'

    def handle(self, *args, **kwargs):
        # Define your crontab schedule (every 30 minutes from 12 PM to 12:30 PM)
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0,30',
            hour='12',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone='Europe/Berlin',
        )

        # Create the periodic task
        PeriodicTask.objects.create(
            crontab=schedule,
            name='Download latest TIF files',
            task='app.klim4cast.tasks.download_latest_tif',
        )
