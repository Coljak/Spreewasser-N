# Generated by Django 4.1.2 on 2023-04-05 14:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0014_remove_buekdata_id_alter_buekdata_polygon_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='soilprofileall',
            name='polygon',
        ),
    ]