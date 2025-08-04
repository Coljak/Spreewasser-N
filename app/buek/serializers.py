from rest_framework import serializers
from . import models



class MapSoilCLCSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MapSoilCLC
        fields = ['polygon_id', 'tkle_nr', 'clc_code', 
                  'soilprofile', 'clc_code', 'bias_21_soilprofile', 
                  'bias_21_clc_code', 'bias_23_soilprofile', 'bias_23_clc_code',
                  'bias_31_soilprofile', 'bias_31_clc_code',]
        
class SoilProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SoilProfile
        fields = '__all__'
        depth = 1
class Ka5TextureClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ka5TextureClass
        fields = ['ka5_soiltype', 'clay', 'silt', 'sand']

class HumusClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HumusClass
        fields = ['corg']

class PHClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PHClass
        fields = ['ph_lower_value', 'ph_upper_value']

class BulkDensityClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BulkDensityClass
        fields = ['raw_density_g_per_cm3']

class SoilProfileHorizonSerializer(serializers.ModelSerializer):
    ka5_texture_class = Ka5TextureClassSerializer(read_only=True)
    humus_class = HumusClassSerializer(read_only=True)
    ph_class = PHClassSerializer(read_only=True)
    bulk_density_class = BulkDensityClassSerializer(read_only=True)

    ptf1_fc = serializers.SerializerMethodField()
    ptf1_wp = serializers.SerializerMethodField()

    class Meta:
        model = models.SoilProfileHorizon
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



