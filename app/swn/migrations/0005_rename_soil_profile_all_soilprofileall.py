# Generated by Django 4.2 on 2023-04-05 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0004_soil_profile_all'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='soil_profile_all',
            new_name='SoilProfileAll',
        ),
    ]