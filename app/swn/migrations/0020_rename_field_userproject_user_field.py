# Generated by Django 4.2 on 2023-06-08 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0019_rename_user_field_userproject_field'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userproject',
            old_name='field',
            new_name='user_field',
        ),
    ]
