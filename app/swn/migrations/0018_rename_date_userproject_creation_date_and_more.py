# Generated by Django 4.2 on 2023-06-08 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0017_geodata'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userproject',
            old_name='date',
            new_name='creation_date',
        ),
        migrations.RenameField(
            model_name='userproject',
            old_name='field',
            new_name='user_field',
        ),
        migrations.AddField(
            model_name='userproject',
            name='calculation_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userproject',
            name='calculation_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
