# Generated by Django 4.1.2 on 2023-03-26 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crop',
            name='winter_summer_crop',
        ),
    ]
