# Generated by Django 4.1.2 on 2023-04-05 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0009_rename_polygon_id_soilprofileall_polygon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='soilprofileall',
            old_name='KA5_texture_class',
            new_name='ka5_texture_class',
        ),
    ]