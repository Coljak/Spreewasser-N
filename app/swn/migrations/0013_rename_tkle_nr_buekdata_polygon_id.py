# Generated by Django 4.1.2 on 2023-04-05 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0012_alter_soilprofileall_avg_range_percentage_of_area_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buekdata',
            old_name='tkle_nr',
            new_name='polygon_id',
        ),
    ]
