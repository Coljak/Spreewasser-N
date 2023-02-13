# Generated by Django 4.1.2 on 2023-02-09 11:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0004_userfield_geom'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userproject',
            name='user',
        ),
        migrations.AddField(
            model_name='userfield',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
