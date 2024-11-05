from rest_framework import serializers
from .models import *



class MapSoilCLCSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapSoilCLC
        fields = ['polygon_id', 'tkle_nr', 'clc_code', 
                  'soilprofile', 'clc_code', 'bias_21_soilprofile', 
                  'bias_21_clc_code', 'bias_23_soilprofile', 'bias_23_clc_code',
                  'bias_31_soilprofile', 'bias_31_clc_code',]
        
class SoilProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilProfile
        fields = '__all__'
        depth = 1

class SoilProfileHorizonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilProfileHorizon
        fields = '__all__'