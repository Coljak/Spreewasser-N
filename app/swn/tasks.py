# TODO: Install and configure celery. 
from celery import shared_task
from .models import UserField


# the queries should be executed in trhe background.
@shared_task
def process_user_field(user_field_id):
    user_field = UserField.objects.get(pk=user_field_id)
    user_field.get_intersecting_soil_data()
    user_field.get_weather_data()
    user_field.save()
