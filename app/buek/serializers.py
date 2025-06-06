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
class Ka5TextureClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ka5TextureClass
        fields = ['ka5_soiltype', 'clay', 'silt', 'sand']

class HumusClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = HumusClass
        fields = ['corg']

class PHClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = PHClass
        fields = ['ph_lower_value', 'ph_upper_value']

class BulkDensityClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkDensityClass
        fields = ['raw_density_g_per_cm3']

class SoilProfileHorizonSerializer(serializers.ModelSerializer):
    ka5_texture_class = Ka5TextureClassSerializer(read_only=True)
    humus_class = HumusClassSerializer(read_only=True)
    ph_class = PHClassSerializer(read_only=True)
    bulk_density_class = BulkDensityClassSerializer(read_only=True)

    ptf1_fc = serializers.SerializerMethodField()
    ptf1_wp = serializers.SerializerMethodField()

    class Meta:
        model = SoilProfileHorizon
        fields = [
            'id',
            'soilprofile',
            'horizont_nr',
            'symbol',
            'obergrenze_m',
            'untergrenze_m',
            'ka5_texture_class',
            'humus_class',
            'ph_class',
            'bulk_density_class',
            'ptf1_fc',
            'ptf1_wp',
        ]

    def get_ptf1_fc(self, obj):
        return obj.get_ptf1_fc()

    def get_ptf1_wp(self, obj):
        return obj.get_ptf1_wp()



