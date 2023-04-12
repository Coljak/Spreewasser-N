# Generated by Django 4.2 on 2023-04-05 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('swn', '0003_rename_poly_buekdata_geom_remove_buekdata_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='soil_profile_all',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_id_in_polygon', models.IntegerField()),
                ('range_percentage_of_area', models.CharField()),
                ('avg_range_percentage_of_area', models.IntegerField()),
                ('horizon_id', models.IntegerField()),
                ('layer_depth', models.IntegerField()),
                ('bulk_density', models.IntegerField()),
                ('raw_density', models.IntegerField()),
                ('soil_organic_carbon', models.FloatField()),
                ('soil_organic_matter', models.IntegerField()),
                ('ph', models.IntegerField()),
                ('KA5_texture_class', models.CharField()),
                ('sand', models.IntegerField()),
                ('clay', models.IntegerField()),
                ('silt', models.IntegerField()),
                ('permanent_wilting_point', models.IntegerField()),
                ('field_capacity', models.IntegerField()),
                ('saturation', models.IntegerField()),
                ('soil_water_conductivity_coefficient', models.IntegerField()),
                ('sceleton', models.IntegerField()),
                ('soil_ammonium', models.IntegerField()),
                ('soil_nitrate', models.IntegerField()),
                ('c_n', models.IntegerField()),
                ('initial_soil_moisture', models.IntegerField()),
                ('layer_description', models.CharField()),
                ('is_in_groundwater', models.IntegerField()),
                ('is_impenetrabl', models.IntegerField()),
                ('polygon_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='swn.buekdata')),
            ],
        ),
    ]
