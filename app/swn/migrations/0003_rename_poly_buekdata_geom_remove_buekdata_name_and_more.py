# Generated by Django 4.2 on 2023-04-05 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0002_buekdata'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buekdata',
            old_name='poly',
            new_name='geom',
        ),
        migrations.RemoveField(
            model_name='buekdata',
            name='name',
        ),
        migrations.AddField(
            model_name='buekdata',
            name='bgl',
            field=models.CharField(max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='buekdata',
            name='hinweis',
            field=models.CharField(max_length=86, null=True),
        ),
        migrations.AddField(
            model_name='buekdata',
            name='legende',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='buekdata',
            name='nrkart',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='buekdata',
            name='shape_area',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='buekdata',
            name='shape_leng',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='buekdata',
            name='symbol',
            field=models.CharField(max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='buekdata',
            name='tkle_nr',
            field=models.BigIntegerField(null=True),
        ),
    ]
