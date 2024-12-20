from rest_framework import serializers
from monica.models import *


class MonicaProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonicaProject
        fields = ('id', 'name', 'description', 'monica_model_setup', 'created_at')


class ModelSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelSetup
        fields = ('id', 'user_crop_parameters', 'user_environment_parameters', 'user_soil_moisture_parameters',
                'user_soil_transport_parameters',  'user_soil_organic_parameters', 'user_soil_temperature_parameters',
                'simulation_parameters')
        
class MonicaSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonicaSite
        fields = ('id', 'name', 'description', 'latitude', 'longitude', 'altitude', 'slope', 'n_deposition', 'created_at')

class MonicaCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonicaCalculation
        fields = ('id', 'name', 'description', 'monica_project', 'start_date', 'end_date', 
                  'created_at', 'forecast_start_date')
        
