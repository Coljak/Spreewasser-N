# Generated by Django 4.1.2 on 2023-04-05 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0008_alter_soilprofileall_polygon_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='soilprofileall',
            old_name='polygon_id',
            new_name='polygon',
        ),
    ]