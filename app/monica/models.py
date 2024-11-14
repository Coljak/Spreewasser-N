from django.db import models
from django.contrib.gis.db import models as gis_models
from swn.models import User
from buek import models as buek_models
from django.contrib.postgres.fields import ArrayField
from typing import List, Tuple
import json
from django.contrib.gis.db.models import functions as gis_functions
from django.contrib.gis.geos import Point
# from django.contrib.gis.measure import Distance
from django.db.models import Q
from django.contrib.gis.db.models.functions import Distance
from datetime import datetime
import pandas as pd


class CropParametersExist(models.Model):
    species_name = models.CharField(max_length=100, blank=True)
    
    in_species = models.BooleanField(default=False)
    in_cultivar = models.BooleanField(default=False)
    in_residues = models.BooleanField(default=False)
    def __str__(self):
        return self.species_name

# this is the model for all jsons in monica-parammeters/crops/<crop-name>/.json
class CultivarParameters(models.Model):
    name = models.CharField(max_length=100)
    species_name = models.CharField(max_length=100, blank=True)
    species_parameters = models.ForeignKey('SpeciesParameters', on_delete=models.CASCADE, blank=True, null=True)
    # assimilate_partitioning_coeff_a = ArrayField(ArrayField(models.FloatField()))
    # base_daylength_a = ArrayField(ArrayField(models.FloatField()))
    assimilate_partitioning_coeff = models.JSONField(blank=True, null=True)
    base_daylength = models.JSONField(blank=True, null=True)    
    begin_sensitive_phase_heat_stress = models.FloatField()
    critical_temperature_heat_stress = models.FloatField()
    crop_height_p1 = models.FloatField()
    crop_height_p2 = models.FloatField()
    crop_specific_max_rooting_depth = models.FloatField()   
    # daylength_requirement_a = ArrayField(ArrayField(models.FloatField()))
    daylength_requirement = models.JSONField(blank=True, null=True)
    description = models.TextField()
    # drought_stress_threshold_a = ArrayField(models.FloatField())
    drought_stress_threshold = models.JSONField(blank=True, null=True)
    end_sensitive_phase_heat_stress = models.FloatField()
    frost_dehardening = models.FloatField()
    frost_hardening = models.FloatField()
    heat_sum_irrigation_end = models.FloatField()
    heat_sum_irrigation_start = models.FloatField()
    is_winter_crop = models.BooleanField(blank=True, null=True, default=False)
    lt50_cultivar = models.FloatField()
    latest_harvest_doy = models.IntegerField()
    low_temperature_exposure = models.FloatField()
    max_assimilation_rate = models.FloatField()
    max_crop_height = models.FloatField()
    # optimum_temperature_a = ArrayField(ArrayField(models.FloatField()))
    # organ_ids_for_cutting_a = ArrayField(models.JSONField(), default=list)
    # organ_ids_for_primary_yield_a = ArrayField(models.JSONField())
    # organ_ids_for_secondary_yield_a = ArrayField(models.JSONField())
    # organ_senescence_rate_a = ArrayField(ArrayField(models.FloatField()))
    optimum_temperature = models.JSONField(blank=True, null=True)
    organ_ids_for_cutting = models.JSONField(blank=True, null=True)
    organ_ids_for_primary_yield = models.JSONField(blank=True, null=True)
    organ_ids_for_secondary_yield = models.JSONField(blank=True, null=True)
    organ_senescence_rate = models.JSONField(blank=True, null=True)
    perennial = models.BooleanField()
    residue_n_ratio = models.FloatField()
    respiratory_stress = models.FloatField()
    # specific_leaf_area_a = ArrayField(ArrayField(models.FloatField()))
    # stage_kc_factor_a = ArrayField(ArrayField(models.FloatField()))
    # stage_temperature_sum_a = ArrayField(ArrayField(models.FloatField()))
    # vernalisation_requirement_a = ArrayField(models.FloatField())
    specific_leaf_area = models.JSONField(blank=True, null=True)
    stage_kc_factor = models.JSONField(blank=True, null=True)
    stage_temperature_sum = models.JSONField(blank=True, null=True)
    vernalisation_requirement = models.JSONField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)
    

    def __str__(self):
        return self.name

    def to_json(self) -> dict:
        return {
            "species_name": self.species_name,
            "AssimilatePartitioningCoeff": self.assimilate_partitioning_coeff,
            "BaseDaylength": [self.base_daylength, "h"],
            "BeginSensitivePhaseHeatStress": [self.begin_sensitive_phase_heat_stress, "°C d"],
            "CriticalTemperatureHeatStress": [self.critical_temperature_heat_stress, "°C"],
            "CropHeightP1": self.crop_height_p1,
            "CropHeightP2": self.crop_height_p2,
            "CropSpecificMaxRootingDepth": self.crop_specific_max_rooting_depth,
            "CultivarName": self.name,
            "DaylengthRequirement": [self.daylength_requirement, "h"],
            "Description": self.description,
            "DroughtStressThreshold": self.drought_stress_threshold,
            "EndSensitivePhaseHeatStress": [self.end_sensitive_phase_heat_stress, "°C d"],
            "FrostDehardening": self.frost_dehardening,
            "FrostHardening": self.frost_hardening,
            "HeatSumIrrigationEnd": self.heat_sum_irrigation_end,
            "HeatSumIrrigationStart": self.heat_sum_irrigation_start,
            "LT50cultivar": self.lt50_cultivar,
            "LatestHarvestDoy": self.latest_harvest_doy,
            "LowTemperatureExposure": self.low_temperature_exposure,
            "MaxAssimilationRate": self.max_assimilation_rate,
            "MaxCropHeight": [self.max_crop_height, "m"],
            "OptimumTemperature": [self.optimum_temperature, "°C"],
            "OrganIdsForCutting": self.organ_ids_for_cutting,
            "OrganIdsForPrimaryYield": self.organ_ids_for_primary_yield,
            "OrganIdsForSecondaryYield": self.organ_ids_for_secondary_yield,
            "OrganSenescenceRate": self.organ_senescence_rate,
            "Perennial": self.perennial,
            "ResidueNRatio": self.residue_n_ratio,
            "RespiratoryStress": self.respiratory_stress,
            "SpecificLeafArea": [self.specific_leaf_area, "ha kg-1"],
            "StageKcFactor": [self.stage_kc_factor, "1;0"],
            "StageTemperatureSum": [self.stage_temperature_sum, "°C d"],
            "VernalisationRequirement": self.vernalisation_requirement,
            "Type": self.__class__.__name__
        }
    
    """
    The import_from_json method is a class method that takes a JSON file path 
    and a name as arguments. It reads the JSON file and creates or updates a 
    Crop object based on the JSON data. The method is decorated with the @classmethod 
    decorator, which allows it to be called on the class itself rather than an 
    instance of the class. This is useful for creating or updating objects based 
    on external data sources.
    e.g. in the python shell: crop.import_from_json('/app/swn/_hohenfinow/monica-parameters/crops/wheat/winter-wheat.json', 'Winter Wheat')
    """

    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)

            cultivar_parameter_name = json_file_path.split('/')[-1].split('.')[0]
            if cultivar_parameter_name == '':
                cultivar_parameter_name = json_file_path.split('/')[-2]
            species_name = json_file_path.split('/')[-2]
            print('cultivar_parameter_name', cultivar_parameter_name)
            print('species_name', species_name)


            # Create or update SpeciesParameters object based on JSON data
            species_params, created = cls.objects.update_or_create(
                name=data["CultivarName"],
                defaults={
                    'species_name': species_name,
                    'assimilate_partitioning_coeff':  data["AssimilatePartitioningCoeff"],
                    'base_daylength':  data["BaseDaylength"][0],
                    'begin_sensitive_phase_heat_stress':  data["BeginSensitivePhaseHeatStress"][0],
                    'critical_temperature_heat_stress':  data["CriticalTemperatureHeatStress"][0],
                    'crop_height_p1':  data["CropHeightP1"],
                    'crop_height_p2':  data["CropHeightP2"],
                    'crop_specific_max_rooting_depth':  data["CropSpecificMaxRootingDepth"],
                    'name':  data["CultivarName"], # Name of json!
                    'daylength_requirement':  data["DaylengthRequirement"][0],
                    'description':  data["Description"],
                    'drought_stress_threshold':  data["DroughtStressThreshold"],
                    'end_sensitive_phase_heat_stress':  data["EndSensitivePhaseHeatStress"][0],
                    'frost_dehardening':  data["FrostDehardening"],
                    'frost_hardening':  data["FrostHardening"],
                    'heat_sum_irrigation_end':  data["HeatSumIrrigationEnd"],
                    'heat_sum_irrigation_start':  data["HeatSumIrrigationStart"],
                    'lt50_cultivar':  data["LT50cultivar"],
                    'latest_harvest_doy':  data["LatestHarvestDoy"],
                    'low_temperature_exposure':  data["LowTemperatureExposure"],
                    'max_assimilation_rate':  data["MaxAssimilationRate"],
                    'max_crop_height':  data["MaxCropHeight"][0],
                    'optimum_temperature':  data["OptimumTemperature"][0],
                    'organ_ids_for_cutting':  data["OrganIdsForCutting"],
                    'organ_ids_for_primary_yield':  data["OrganIdsForPrimaryYield"],
                    'organ_ids_for_secondary_yield':  data["OrganIdsForSecondaryYield"],
                    'organ_senescence_rate':  data["OrganSenescenceRate"],
                    'perennial':  data["Perennial"],
                    'residue_n_ratio':  data["ResidueNRatio"],
                    'respiratory_stress':  data["RespiratoryStress"],
                    'specific_leaf_area':  data["SpecificLeafArea"][0],
                    'stage_kc_factor':  data["StageKcFactor"][0],
                    'stage_temperature_sum':  data["StageTemperatureSum"][0],
                    'vernalisation_requirement':  data["VernalisationRequirement"],
                }
            )
            
            if created or not species_params._state.adding:
                species_params.save()
            
            return species_params

# this is the model for all jsons in monica-parammeters/crops/<crop_name>.json
class SpeciesParameters(models.Model):
    name = models.CharField(max_length=100)
    aboveground_organ = models.JSONField(blank=True, null=True)
    assimilate_reallocation = models.FloatField(blank=True, null=True)
    base_temperature = models.JSONField(blank=True, null=True)
    carboxylation_pathway = models.IntegerField(blank=True, null=True)
    critical_oxygen_content = models.JSONField(blank=True, null=True)
    cutting_delay_days = models.IntegerField(blank=True, null=True)
    default_radiation_use_efficiency = models.FloatField(blank=True, null=True)
    development_acceleration_by_nitrogen_stress = models.FloatField(blank=True, null=True)
    drought_impact_on_fertility_factor = models.FloatField(blank=True, null=True)
    field_condition_modifier = models.FloatField(blank=True, null=True)
    initial_kc_factor = models.FloatField(blank=True, null=True)
    initial_organ_biomass = models.JSONField(blank=True, null=True)
    initial_rooting_depth = models.FloatField(blank=True, null=True)
    is_perennial_crop = models.BooleanField(blank=True, null=True, default=False)
    limiting_temperature_heat_stress = models.FloatField(blank=True, null=True)
    luxury_n_coeff = models.FloatField(blank=True, null=True)
    max_crop_diameter = models.FloatField(blank=True, null=True)
    max_n_uptake_param = models.FloatField(blank=True, null=True)
    minimum_n_concentration = models.FloatField(blank=True, null=True)
    minimum_temperature_for_assimilation = models.FloatField(blank=True, null=True)
    optimum_temperature_for_assimilation = models.IntegerField(blank=True, null=True)
    maximum_temperature_for_assimilation = models.IntegerField(blank=True, null=True)
    minimum_temperature_root_growth = models.FloatField(blank=True, null=True)
    n_concentration_aboveground_biomass = models.FloatField(blank=True, null=True)
    n_concentration_b0 = models.FloatField(blank=True, null=True)
    n_concentration_pn = models.FloatField(blank=True, null=True)
    n_concentration_root = models.FloatField(blank=True, null=True)
    organ_growth_respiration = models.JSONField(blank=True, null=True)
    organ_maintenance_respiration = models.JSONField(blank=True, null=True)
    part_biological_n_fixation = models.FloatField(blank=True, null=True)
    plant_density = models.IntegerField(blank=True, null=True)
    root_distribution_param = models.FloatField(blank=True, null=True)
    root_form_factor = models.FloatField(blank=True, null=True)
    root_growth_lag = models.IntegerField(blank=True, null=True)
    root_penetration_rate = models.FloatField(blank=True, null=True)
    sampling_depth = models.FloatField(blank=True, null=True)
    specific_root_length = models.FloatField(blank=True, null=True)
    stage_after_cut = models.IntegerField(blank=True, null=True)
    stage_at_max_diameter = models.IntegerField(blank=True, null=True)
    stage_at_max_height = models.IntegerField(blank=True, null=True)
    stage_max_root_n_concentration = models.JSONField(blank=True, null=True)
    storage_organ = models.JSONField(blank=True, null=True)
    target_n30 = models.FloatField(blank=True, null=True)
    target_n_sampling_depth = models.FloatField(blank=True, null=True)
    stage_mobil_from_storage_coeff = models.JSONField(blank=True, null=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            if data.get('type') == cls.__class__.__name__:
            # Create or update SpeciesParameters object based on JSON data
                species_params, created = cls.objects.update_or_create(
                    name=data.get('SpeciesName'),
                    defaults={
                        'aboveground_organ': data.get('AbovegroundOrgan'),
                        'assimilate_reallocation': data.get('AssimilateReallocation'),
                        'base_temperature': data.get('BaseTemperature'),
                        'carboxylation_pathway': data.get('CarboxylationPathway'),
                        'critical_oxygen_content': data.get('CriticalOxygenContent'),
                        'cutting_delay_days': data.get('CuttingDelayDays'),
                        'default_radiation_use_efficiency': data.get('DefaultRadiationUseEfficiency'),
                        'development_acceleration_by_nitrogen_stress': data.get('DevelopmentAccelerationByNitrogenStress'),
                        'drought_impact_on_fertility_factor': data.get('DroughtImpactOnFertilityFactor'),
                        'field_condition_modifier': data.get('FieldConditionModifier'),
                        'initial_kc_factor': data.get('InitialKcFactor'),
                        'initial_organ_biomass': data.get('InitialOrganBiomass'),
                        'initial_rooting_depth': data.get('InitialRootingDepth'),
                        'limiting_temperature_heat_stress': data.get('LimitingTemperatureHeatStress'),
                        'luxury_n_coeff': data.get('LuxuryNCoeff'),
                        'max_crop_diameter': data.get('MaxCropDiameter'),
                        'max_n_uptake_param': data.get('MaxNUptakeParam'),
                        'minimum_n_concentration': data.get('MinimumNConcentration'),
                        'minimum_temperature_for_assimilation': data.get('MinimumTemperatureForAssimilation'),
                        'optimum_temperature_for_assimilation': data.get('OptimumTemperatureForAssimilation', None),
                        'maximum_temperature_for_assimilation': data.get('MaximumTemperatureForAssimilation', None),
                        'minimum_temperature_root_growth': data.get('MinimumTemperatureRootGrowth'),
                        'n_concentration_aboveground_biomass': data.get('NConcentrationAbovegroundBiomass'),
                        'n_concentration_b0': data.get('NConcentrationB0'),
                        'n_concentration_pn': data.get('NConcentrationPN'),
                        'n_concentration_root': data.get('NConcentrationRoot'),
                        'organ_growth_respiration': data.get('OrganGrowthRespiration'),
                        'organ_maintenance_respiration': data.get('OrganMaintenanceRespiration'),
                        'part_biological_n_fixation': data.get('PartBiologicalNFixation'),
                        'plant_density': data.get('PlantDensity'),
                        'root_distribution_param': data.get('RootDistributionParam'),
                        'root_form_factor': data.get('RootFormFactor'),
                        'root_growth_lag': data.get('RootGrowthLag'),
                        'root_penetration_rate': data.get('RootPenetrationRate'),
                        'sampling_depth': data.get('SamplingDepth'),
                        'specific_root_length': data.get('SpecificRootLength'),
                        'stage_after_cut': data.get('StageAfterCut'),
                        'stage_at_max_diameter': data.get('StageAtMaxDiameter'),
                        'stage_at_max_height': data.get('StageAtMaxHeight'),
                        'stage_max_root_n_concentration': data.get('StageMaxRootNConcentration'),
                        'storage_organ': data.get('StorageOrgan'),
                        'target_n30': data.get('TargetN30'),
                        'target_n_sampling_depth': data.get('TargetNSamplingDepth'),
                        'stage_mobil_from_storage_coeff': data.get('StageMobilFromStorageCoeff')
                    }
                )

                # Save the instance if it was created or updated
                if created or not species_params._state.adding:
                    species_params.save()

                return species_params

    def to_json(self):
        json_data = {  
            "SpeciesName": self.name,
            "AbovegroundOrgan": self.aboveground_organ,
            "AssimilateReallocation":self.assimilate_reallocation,
            "BaseTemperature":self.base_temperature,
            "CarboxylationPathway":self.carboxylation_pathway,
            "CriticalOxygenContent":self.critical_oxygen_content,
            "CuttingDelayDays":self.cutting_delay_days,
            "DefaultRadiationUseEfficiency":self.default_radiation_use_efficiency,
            "DevelopmentAccelerationByNitrogenStress":self.development_acceleration_by_nitrogen_stress,
            "DroughtImpactOnFertilityFactor":self.drought_impact_on_fertility_factor,
            "FieldConditionModifier":self.field_condition_modifier,
            "InitialKcFactor":self.initial_kc_factor,
            "InitialOrganBiomass":self.initial_organ_biomass,
            "InitialRootingDepth":self.initial_rooting_depth,
            "LimitingTemperatureHeatStress": self.limiting_temperature_heat_stress,
            "LuxuryNCoeff": self.luxury_n_coeff,
            "MaxCropDiameter":self.max_crop_diameter,
            "MaxNUptakeParam": self.max_n_uptake_param,
            "MinimumNConcentration":self.minimum_n_concentration,
            "MinimumTemperatureForAssimilation": self.minimum_temperature_for_assimilation,
            # TODO OptimumTemperature into model
            "OptimumTemperatureForAssimilation": self.optimum_temperature_for_assimilation,
            "MaximumTemperatureForAssimilation": self.maximum_temperature_for_assimilation,
            "MinimumTemperatureRootGrowth": self.minimum_temperature_root_growth,
            "NConcentrationAbovegroundBiomass": self.n_concentration_aboveground_biomass,
            "NConcentrationB0":self.n_concentration_b0,
            "NConcentrationPN": self.n_concentration_pn,
            "NConcentrationRoot": self.n_concentration_root,
            "OrganGrowthRespiration": self.organ_growth_respiration,
            "OrganMaintenanceRespiration": self.organ_maintenance_respiration,
            "PartBiologicalNFixation": self.part_biological_n_fixation,
            "PlantDensity": self.plant_density,
            "RootDistributionParam": self.root_distribution_param,
            "RootFormFactor": self.root_form_factor,
            "RootGrowthLag": self.root_growth_lag,
            "RootPenetrationRate": self.root_penetration_rate,
            "SamplingDepth": self.sampling_depth,
            "SpecificRootLength": self.specific_root_length,
            "StageAfterCut": self.stage_after_cut,
            "StageAtMaxDiameter": self.stage_at_max_diameter,
            "StageAtMaxHeight": self.stage_at_max_height,
            "StageMaxRootNConcentration": self.stage_max_root_n_concentration,
            "StorageOrgan": self.storage_organ,
            "TargetN30": self.target_n30,
            "TargetNSamplingDepth": self.target_n_sampling_depth,
            "type": self.__class__.__name__
        }
        
        if self.optimum_temperature_for_assimilation is None:
            del json_data["OptimumTemperatureForAssimilation"] 
        if self.maximum_temperature_for_assimilation is not None:
            del json_data["MaximumTemperatureForAssimilation"] 
    
        return json_data
    
# TODO probably obsolete. is actually already in the SpeciesParameters model
class OrganFromDB(models.Model):
    species_name = models.CharField(max_length=100, blank=True)
    species_parameters= models.ForeignKey(SpeciesParameters, on_delete=models.CASCADE, blank=True, null=True)   
    organ = models.ForeignKey('Organ', on_delete=models.CASCADE, blank=True, null=True)
    organ_name = models.CharField(max_length=100, blank=True)
    initial_organ_biomass = models.FloatField(blank=True, null=True)
    organ_maintainance_respiration = models.FloatField(blank=True, null=True)
    organ_growth_respiration = models.FloatField(blank=True, null=True)
    is_above_ground = models.BooleanField(blank=True, null=True)
    is_stoarge_organ = models.BooleanField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)

# crop residues
class CropResidueParameters(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    species_name = models.CharField(max_length=100,blank=True, null=True)
    species_parameters = models.ForeignKey(SpeciesParameters, on_delete=models.CASCADE, blank=True, null=True)
    aom_dry_matter_content = models.FloatField(blank=True, null=True)
    aom_fast_dec_coeff_standard = models.FloatField(blank=True, null=True)
    aom_nh4_content = models.FloatField(blank=True, null=True)
    aom_no3_content = models.FloatField(blank=True, null=True)
    aom_slow_dec_coeff_standard = models.FloatField(blank=True, null=True)
    cn_ratio_aom_fast = models.FloatField(blank=True, null=True)
    cn_ratio_aom_slow = models.FloatField(blank=True, null=True)
    n_concentration = models.FloatField(blank=True, null=True)
    corg_content = models.FloatField(blank=True, null=True)
    part_aom_slow_to_smb_fast = models.FloatField(blank=True, null=True)
    part_aom_slow_to_smb_slow = models.FloatField(blank=True, null=True)
    part_aom_to_aom_fast = models.FloatField(blank=True, null=True)
    part_aom_to_aom_slow = models.FloatField(blank=True, null=True)
    residue_type = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)

    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            name = json_file_path.split('/')[-1].split('.')[0]
            
            # Check if CropParameters with the given file_name exists
            crop_params = cls.objects.filter(name=name).first()

            # Create or update CropParameters object based on JSON data
            crop_residue_params, created = cls.objects.update_or_create(
                defaults={
                    'name': name,
                    'aom_dry_matter_content': data.get('AOM_DryMatterContent')[0],
                    'aom_fast_dec_coeff_standard': data.get('AOM_FastDecCoeffStandard')[0],
                    'aom_nh4_content': data.get('AOM_NH4Content')[0],
                    'aom_no3_content': data.get('AOM_NO3Content')[0],
                    'aom_slow_dec_coeff_standard': data.get('AOM_SlowDecCoeffStandard')[0],
                    'cn_ratio_aom_fast': data.get('CN_Ratio_AOM_Fast')[0],
                    'cn_ratio_aom_slow': data.get('CN_Ratio_AOM_Slow')[0],
                    'n_concentration': data.get('NConcentration')[0],
                    'corg_content': data.get('CorgContent')[0],
                    'part_aom_slow_to_smb_fast': data.get('PartAOM_Slow_to_SMB_Fast')[0],
                    'part_aom_slow_to_smb_slow': data.get('PartAOM_Slow_to_SMB_Slow')[0],
                    'part_aom_to_aom_fast': data.get('PartAOM_to_AOM_Fast')[0],
                    'part_aom_to_aom_slow': data.get('PartAOM_to_AOM_Slow')[0],
                    'residue_type': data.get('residueType'),
                    'species': data.get('species'),
                    
                },
                name=name  # Additional filter for update_or_create
            )

            # Save the instance if it was created or updated
            if created or not crop_residue_params._state.adding:
                crop_residue_params.save()

            return crop_residue_params


    def to_json(self):
        return {
            "AOM_DryMatterContent": [
                self.aom_dry_matter_content, 
                "kg DM kg FM-1",
                "Dry matter content of added organic matter"
                ],
            "AOM_FastDecCoeffStandard": [
                self.aom_fast_dec_coeff_standard, 
                "d-1",
                "Decomposition rate coefficient of fast AOM at standard conditions"
                ],
            "AOM_NH4Content": [
                self.aom_nh4_content, 
                "kg N kg DM-1",
                "Ammonium content in added organic matter"
                ],
            "AOM_NO3Content": [
                self.aom_no3_content, 
                "kg N kg DM-1",
                "Nitrate content in added organic matter"
                ],
            "AOM_SlowDecCoeffStandard": [
                self.aom_slow_dec_coeff_standard, 
                "d-1",
                "Decomposition rate coefficient of slow AOM at standard conditions"
                ],
            "CN_Ratio_AOM_Fast": [
                self.cn_ratio_aom_fast, 
                "25",
                "C to N ratio of the rapidly decomposing AOM pool"
                ],
            "CN_Ratio_AOM_Slow": [
                self.cn_ratio_aom_slow, 
                "",
                "C to N ratio of the slowly decomposing AOM pool"
                ],
            "NConcentration": [
                self.n_concentration, 
                "kg N kg DM-1",
                "Nitrogen content in added organic matter"
                ],
            "CorgContent": [
                self.corg_content, 
                "kg C kg DM-1",
                "Carbon content in added organic matter"
                ],
            "PartAOM_Slow_to_SMB_Fast": [
                self.part_aom_slow_to_smb_fast, 
                "kg kg-1",
                "Part of AOM slow consumed by fast soil microbial biomass"
                ],
            "PartAOM_Slow_to_SMB_Slow": [
                self.part_aom_slow_to_smb_slow, 
                "kg kg-1",
                "Part of AOM slow consumed by slow soil microbial biomass"
                ],
            "PartAOM_to_AOM_Fast": [
                self.part_aom_to_aom_fast, 
                "kg kg-1",
                "Part of AOM that is assigned to the rapidly decomposing pool"
                ],
            "PartAOM_to_AOM_Slow": [
                self.part_aom_to_aom_slow, 
                "kg kg-1",
                "Part of AOM that is assigned to the slowly decomposing pool"
                ],
            "residueType": self.residue_type,
            "species": self.species_name,
            "type": self.__class__.__name__
        }


class OrganicFertiliser(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    aom_dry_matter_content = models.FloatField(blank=True, null=True)
    aom_fast_dec_coeff_standard = models.FloatField(blank=True, null=True)
    aom_nh4_content = models.FloatField(blank=True, null=True)
    aom_no3_content = models.FloatField(blank=True, null=True)
    aom_slow_dec_coeff_standard = models.FloatField(blank=True, null=True)
    cn_ratio_aom_fast = models.FloatField(blank=True, null=True)
    cn_ratio_aom_slow = models.FloatField(blank=True, null=True)
    n_concentration = models.FloatField(blank=True, null=True)
    part_aom_slow_to_smb_fast = models.FloatField(blank=True, null=True)
    part_aom_slow_to_smb_slow = models.FloatField(blank=True, null=True)
    part_aom_to_aom_fast = models.FloatField(blank=True, null=True)
    part_aom_to_aom_slow = models.FloatField(blank=True, null=True)
    fertiliser_char_id = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        return self.name

    def to_json(self) -> dict:
        return {
            "AOM_DryMatterContent": [
                self.aom_dry_matter_content, 
                "kg DM kg FM-1", 
                "Dry matter content of added organic matter"
                ],
            "AOM_FastDecCoeffStandard": [
                self.aom_fast_dec_coeff_standard, 
                "d-1", 
                "Decomposition rate coefficient of fast AOM at standard conditions"
                ],
            "AOM_NH4Content": [
                self.aom_nh4_content, 
                "kg N kg DM-1", 
                "Ammonium content in added organic matter"
                ],
            "AOM_NO3Content": [
                self.aom_no3_content, 
                "kg N kg DM-1", 
                "Nitrate content in added organic matter"
                ],
            "AOM_SlowDecCoeffStandard": [
                self.aom_slow_dec_coeff_standard, 
                "d-1", 
                "Decomposition rate coefficient of slow AOM at standard conditions"
                ],
            "CN_Ratio_AOM_Fast": [
                self.cn_ratio_aom_fast, 
                "", 
                "C to N ratio of the rapidly decomposing AOM pool"
                ],
            "CN_Ratio_AOM_Slow": [
                self.cn_ratio_aom_slow, 
                "", 
                "C to N ratio of the slowly decomposing AOM pool"
                ],
            "NConcentration": self.n_concentration,
            "PartAOM_Slow_to_SMB_Fast": [
                self.part_aom_slow_to_smb_fast, 
                "kg kg-1", 
                "Part of AOM slow consumed by slow soil microbial biomass"
                ],
            "PartAOM_Slow_to_SMB_Slow": [
                self.part_aom_slow_to_smb_slow, 
                "kg kg-1", 
                "Part of AOM that is assigned to the rapidly decomposing pool"
                ],
            "PartAOM_to_AOM_Fast": [
                self.part_aom_to_aom_fast, 
                "kg kg-1", 
                "Part of AOM that is assigned to the slowly decomposing pool"
                ],
            "PartAOM_to_AOM_Slow": [
                self.part_aom_to_aom_slow, 
                "kg kg-1", 
                "Part of AOM that is assigned to the slowly decomposing pool"
                ],
            "id": self.fertiliser_char_id,
            "name": self.name,
            "type": "OrganicFertiliserParameters"
        }
    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            fertiliser_id = data.get('id')

        organic_fertiliser, created = cls.objects.update_or_create(
            defaults = {
                'aom_dry_matter_content': data.get('AOM_DryMatterContent')[0],
                'aom_fast_dec_coeff_standard': data.get('AOM_FastDecCoeffStandard')[0],
                'aom_nh4_content': data.get('AOM_NH4Content')[0],
                'aom_no3_content': data.get('AOM_NO3Content')[0],
                'aom_slow_dec_coeff_standard': data.get('AOM_SlowDecCoeffStandard')[0],
                'cn_ratio_aom_fast': data.get('CN_Ratio_AOM_Fast')[0],
                'cn_ratio_aom_slow': data.get('CN_Ratio_AOM_Slow')[0],
                'n_concentration': data.get('NConcentration'),
                'part_aom_slow_to_smb_fast': data.get('PartAOM_Slow_to_SMB_Fast')[0],
                'part_aom_slow_to_smb_slow': data.get('PartAOM_Slow_to_SMB_Slow')[0],
                'part_aom_to_aom_fast': data.get('PartAOM_to_AOM_Fast')[0],
                'part_aom_to_aom_slow': data.get('PartAOM_to_AOM_Slow')[0],
                'fertiliser_char_id': data.get('id'),
                'name': data.get('name'),
            },
            fertiliser_id=fertiliser_id )
        
        if created or not organic_fertiliser._state.adding:
            organic_fertiliser.save()

        return organic_fertiliser
    
# Mineral Fertilisers
class MineralFertiliser(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    carbamid = models.FloatField(blank=True, null=True)
    nh4 = models.FloatField(blank=True, null=True)
    no3 = models.FloatField(blank=True, null=True)
    fertiliser_id = models.CharField(max_length=100, blank=True, null=True)
    # type = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        return self.name

    def to_json(self) -> dict:
        return {
            "Carbamid": self.carbamid,
            "NH4": self.nh4,
            "NO3": self.no3,
            "id": self.fertiliser_id,
            "name": self.name,
            "type": "MineralFertiliserParameters"
        }
    
    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            fertiliser_id = data.get('id')
            
        mineral_fertiliser, created = cls.objects.update_or_create(
            defaults={
                'name': data.get('name'),
                'fertiliser_id': data.get('id'),
                'carbamid': data.get('Carbamid'),
                'nh4': data.get('NH4'),
                'no3': data.get('NO3'),
                'type': data.get('type')
            },
            fertiliser_id=fertiliser_id 
        )
        # Save the instance if it was created or updated
        if created or not mineral_fertiliser._state.adding:
            mineral_fertiliser.save()
        
        # TODO for export to .json file: 
        return mineral_fertiliser

class UserCropParameters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    default = models.BooleanField(default=False) # user's default
    canopy_reflection_coefficient = models.FloatField()
    growth_respiration_parameter1 = models.FloatField()
    growth_respiration_parameter2 = models.FloatField()
    growth_respiration_redux = models.FloatField()
    maintenance_respiration_parameter1 = models.FloatField()
    maintenance_respiration_parameter2 = models.FloatField()
    max_crop_n_demand = models.FloatField() 
    minimum_available_n = models.FloatField()
    minimum_n_concentration_root = models.FloatField()
    reference_albedo = models.FloatField()
    reference_leaf_area_index = models.FloatField()
    reference_max_assimilation_rate = models.FloatField()
    saturation_beta = models.FloatField()
    stomata_conductance_alpha = models.FloatField() 
    tortuosity = models.FloatField()
    is_default = models.BooleanField(blank=True, null=True, default=False) # system's default

    def to_json(self):
        return {
            "CanopyReflectionCoefficient": self.canopy_reflection_coefficient,
            "GrowthRespirationParameter1": self.growth_respiration_parameter1,
            "GrowthRespirationParameter2": self.growth_respiration_parameter2,
            "GrowthRespirationRedux": self.growth_respiration_redux,
            "MaintenanceRespirationParameter1": self.maintenance_respiration_parameter1,
            "MaintenanceRespirationParameter2": self.maintenance_respiration_parameter2,
            "MaxCropNDemand": self.max_crop_n_demand,
            "MinimumAvailableN": self.minimum_available_n,
            "MinimumNConcentrationRoot": self.minimum_n_concentration_root,
            "ReferenceAlbedo": self.reference_albedo,
            "ReferenceLeafAreaIndex": self.reference_leaf_area_index,
            "ReferenceMaxAssimilationRate": self.reference_max_assimilation_rate,
            "SaturationBeta": self.saturation_beta,
            "StomataConductanceAlpha": self.stomata_conductance_alpha,
            "Tortuosity": self.tortuosity,
            "type": self.__class__.__name__
        }
    
    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)

            if data.get('type') == cls.__class__.__name__:
            # Create or update CropParameters object based on JSON data
                crop_params, created = cls.objects.update_or_create(
                    {
                    'canopy_reflection_coefficient': data.get('CanopyReflectionCoefficient'),
                    'growth_respiration_parameter1': data.get('GrowthRespirationParameter1'),
                    'growth_respiration_parameter2': data.get('GrowthRespirationParameter2'),
                    'growth_respiration_redux': data.get('GrowthRespirationRedux'),
                    'maintenance_respiration_parameter1': data.get('MaintenanceRespirationParameter1'),
                    'maintenance_respiration_parameter2': data.get('MaintenanceRespirationParameter2'),
                    'max_crop_n_demand': data.get('MaxCropNDemand'),
                    'minimum_available_n': data.get('MinimumAvailableN'),
                    'minimum_n_concentration_root': data.get('MinimumNConcentrationRoot'),
                    'reference_albedo': data.get('ReferenceAlbedo'),
                    'reference_leaf_area_index': data.get('ReferenceLeafAreaIndex'),
                    'reference_max_assimilation_rate': data.get('ReferenceMaxAssimilationRate'),
                    'saturation_beta': data.get('SaturationBeta'),
                    'stomata_conductance_alpha': data.get('StomataConductanceAlpha'),
                    'tortuosity': data.get('Tortuosity'),
                    
                    }
                )
                if created or not crop_params._state.adding:
                    crop_params.save()

                return crop_params
        
class UserEnvironmentParameters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    default = models.BooleanField(default=False) # user's default
    name = models.CharField(max_length=100, null=True, blank=True)
    albedo = models.FloatField()
    rcp = models.CharField(max_length=10)
    atmospheric_co2 = models.FloatField() 
    atmospheric_co2s = models.JSONField(default=dict)
    yearly_co2_values = models.JSONField(default=dict)
    leaching_depth = models.FloatField()
    max_groundwater_depth = models.FloatField() 
    min_groundwater_depth = models.FloatField()
    min_groundwater_depth_month = models.IntegerField() 
    wind_speed_height = models.FloatField()
    time_step = models.IntegerField() 
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def to_json(self):
        return {
            "Albedo": self.albedo,
            "rcp": self.rcp,
            "AtmosphericCO2": self.atmospheric_co2,
            "0 means MONICA will calculate CO2 automatically, else use this value for whole simulation, unless more exact data are available": "",
            "AtmosphericCO2s": self.atmospheric_co2s,
            "year -> CO2-value pairs for yearly CO2 values": self.yearly_co2_values,
            "LeachingDepth": self.leaching_depth,
            "MaxGroundwaterDepth": self.max_groundwater_depth,
            "MinGroundwaterDepth": self.min_groundwater_depth,
            "MinGroundwaterDepthMonth": self.min_groundwater_depth_month,
            "WindSpeedHeight": self.wind_speed_height,
            "timeStep": self.time_step,
            "type": self.__class__.__name__
        }

    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            if data.get('type') == "UserEnvironmentParameters":
            # Create or update UserEnvironmentParameters object based on JSON data
                user_params, created = cls.objects.update_or_create(
                    albedo=data.get('Albedo'),
                    rcp=data.get('rcp'),
                    atmospheric_co2=data.get('AtmosphericCO2'),
                    atmospheric_co2s=data.get('AtmosphericCO2s'),
                    yearly_co2_values=data.get('year -> CO2-value pairs for yearly CO2 values'),
                    leaching_depth=data.get('LeachingDepth'),
                    max_groundwater_depth=data.get('MaxGroundwaterDepth'),
                    min_groundwater_depth=data.get('MinGroundwaterDepth'),
                    min_groundwater_depth_month=data.get('MinGroundwaterDepthMonth'),
                    wind_speed_height=data.get('WindSpeedHeight'),
                    time_step=data.get('timeStep'),       
                )

                if created or not user_params._state.adding:
                    user_params.save()

                return user_params

# modify implemented
class UserSoilMoistureParameters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    # default = models.BooleanField(default=False)
    correction_rain = models.FloatField() # TODO integer
    correction_snow = models.FloatField()
    critical_moisture_depth = models.FloatField()
    evaporation_zeta = models.FloatField() # TODO integer
    groundwater_discharge = models.FloatField() # TODO integer
    hydraulic_conductivity_redux = models.FloatField()
    kc_factor = models.FloatField()
    max_percolation_rate = models.FloatField() # TODO integer
    maximum_evaporation_impact_depth = models.FloatField() # TODO integer
    moisture_init_value = models.FloatField() # TODO integer
    new_snow_density_min = models.FloatField()
    refreeze_parameter1 = models.FloatField()
    refreeze_parameter2 = models.FloatField()
    refreeze_temperature = models.FloatField()
    saturated_hydraulic_conductivity = models.FloatField() # TODO integer
    snow_accumulation_threshold_temperature = models.FloatField()
    snow_max_additional_density = models.FloatField()
    snow_melt_temperature = models.FloatField()
    snow_packing = models.FloatField()
    snow_retention_capacity_max = models.FloatField()
    snow_retention_capacity_min = models.FloatField()
    surface_roughness = models.FloatField()
    temperature_limit_for_liquid_water = models.FloatField() # TODO integer
    xsa_critical_soil_moisture = models.FloatField()
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def to_json(self):
        return {
            "CorrectionRain": self.correction_rain,
            "CorrectionSnow": self.correction_snow,
            "CriticalMoistureDepth": self.critical_moisture_depth,
            "EvaporationZeta": self.evaporation_zeta,
            "GroundwaterDischarge": self.groundwater_discharge,
            "HydraulicConductivityRedux": self.hydraulic_conductivity_redux,
            "KcFactor": self.kc_factor,
            "MaxPercolationRate": self.max_percolation_rate,
            "MaximumEvaporationImpactDepth": self.maximum_evaporation_impact_depth,
            "MoistureInitValue": self.moisture_init_value,
            "NewSnowDensityMin": self.new_snow_density_min,
            "RefreezeParameter1": self.refreeze_parameter1,
            "RefreezeParameter2": self.refreeze_parameter2,
            "RefreezeTemperature": self.refreeze_temperature,
            "SaturatedHydraulicConductivity": self.saturated_hydraulic_conductivity,
            "SnowAccumulationTresholdTemperature": self.snow_accumulation_threshold_temperature,
            "SnowMaxAdditionalDensity": self.snow_max_additional_density,
            "SnowMeltTemperature": self.snow_melt_temperature,
            "SnowPacking": self.snow_packing,
            "SnowRetentionCapacityMax": self.snow_retention_capacity_max,
            "SnowRetentionCapacityMin": self.snow_retention_capacity_min,
            "SurfaceRoughness": self.surface_roughness,
            "TemperatureLimitForLiquidWater": self.temperature_limit_for_liquid_water,
            "XSACriticalSoilMoisture": self.xsa_critical_soil_moisture,
            "type": self.__class__.__name__
        }

    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        print("create_or_update")
        
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            
            if data.get('type') == "UserSoilMoistureParameters":
                
                # Create or update UserSoilMoistureParameters object based on JSON data
                soil_params, created = cls.objects.update_or_create(
                    correction_rain=data.get('CorrectionRain'),
                    correction_snow=data.get('CorrectionSnow'),
                    critical_moisture_depth=data.get('CriticalMoistureDepth'),
                    evaporation_zeta=data.get('EvaporationZeta'),
                    groundwater_discharge=data.get('GroundwaterDischarge'),
                    hydraulic_conductivity_redux=data.get('HydraulicConductivityRedux'),
                    kc_factor=data.get('KcFactor'),
                    max_percolation_rate=data.get('MaxPercolationRate'),
                    maximum_evaporation_impact_depth=data.get('MaximumEvaporationImpactDepth'),
                    moisture_init_value=data.get('MoistureInitValue'),
                    new_snow_density_min=data.get('NewSnowDensityMin'),
                    refreeze_parameter1=data.get('RefreezeParameter1'),
                    refreeze_parameter2=data.get('RefreezeParameter2'),
                    refreeze_temperature=data.get('RefreezeTemperature'),
                    saturated_hydraulic_conductivity=data.get('SaturatedHydraulicConductivity'),
                    snow_accumulation_threshold_temperature=data.get('SnowAccumulationTresholdTemperature'),
                    snow_max_additional_density=data.get('SnowMaxAdditionalDensity'),
                    snow_melt_temperature=data.get('SnowMeltTemperature'),
                    snow_packing=data.get('SnowPacking'),
                    snow_retention_capacity_max=data.get('SnowRetentionCapacityMax'),
                    snow_retention_capacity_min=data.get('SnowRetentionCapacityMin'),
                    surface_roughness=data.get('SurfaceRoughness'),
                    temperature_limit_for_liquid_water=data.get('TemperatureLimitForLiquidWater'),
                    xsa_critical_soil_moisture=data.get('XSACriticalSoilMoisture'),
                )

                if created or not soil_params._state.adding:
                    soil_params.save()

                return soil_params

# modify implemented
class UserSoilOrganicParameters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    # default = models.BooleanField(default=False)
    qten_factor = models.FloatField()
    temp_dec_optimal = models.FloatField()
    moisture_dec_optimal = models.FloatField()
    aom_fast_max_c_to_n = models.FloatField()
    aom_fast_utilization_efficiency = models.FloatField()
    aom_slow_utilization_efficiency = models.FloatField()
    activation_energy = models.FloatField()
    ammonia_oxidation_rate_coeff_standard = models.FloatField()
    atmospheric_resistance = models.FloatField()
    cn_ratio_smb = models.FloatField()
    denit1 = models.FloatField()
    denit2 = models.FloatField()
    denit3 = models.FloatField()
    hydrolysis_km = models.FloatField()
    hydrolysis_p1 = models.FloatField()
    hydrolysis_p2 = models.FloatField()
    immobilisation_rate_coeff_nh4 = models.FloatField()
    immobilisation_rate_coeff_no3 = models.FloatField()
    inhibitor_nh3 = models.FloatField()
    limit_clay_effect = models.FloatField()
    max_mineralisation_depth = models.FloatField()
    n2o_production_rate = models.FloatField()
    nitrite_oxidation_rate_coeff_standard = models.FloatField()
    part_smb_fast_to_som_fast = models.FloatField()
    part_smb_slow_to_som_fast = models.FloatField()
    part_som_fast_to_som_slow = models.FloatField()
    part_som_to_smb_fast = models.FloatField()
    part_som_to_smb_slow = models.FloatField()
    smb_fast_death_rate_standard = models.FloatField()
    smb_fast_maint_rate_standard = models.FloatField()
    smb_slow_death_rate_standard = models.FloatField()
    smb_slow_maint_rate_standard = models.FloatField()
    smb_utilization_efficiency = models.FloatField()
    som_fast_dec_coeff_standard = models.FloatField()
    som_fast_utilization_efficiency = models.FloatField()
    som_slow_dec_coeff_standard = models.FloatField()
    som_slow_utilization_efficiency = models.FloatField()
    spec_anaerob_denitrification = models.FloatField()
    transport_rate_coeff = models.FloatField()

    # Additional fields for stics subfield
    use_n2o = models.BooleanField(default=False)
    use_nit = models.BooleanField(default=False)
    use_denit = models.BooleanField(default=False)
    code_vnit = models.CharField(max_length=100)
    code_tnit = models.CharField(max_length=100)
    code_rationit = models.CharField(max_length=100)
    code_hourly_wfps_nit = models.CharField(max_length=100)
    code_pdenit = models.CharField(max_length=100)
    code_ratiodenit = models.CharField(max_length=100)
    code_hourly_wfps_denit = models.CharField(max_length=100)
    hminn = models.FloatField()
    hoptn = models.FloatField()
    phminnit = models.FloatField()
    phmaxnit = models.FloatField()
    nh4_min = models.FloatField()
    phminden = models.FloatField()
    phmaxden = models.FloatField()
    wfpsc = models.FloatField()
    tdenitopt_gauss = models.FloatField()
    scale_tdenitopt = models.FloatField()
    kd = models.FloatField()
    k_desat = models.FloatField()
    fnx = models.FloatField()
    vnitmax = models.FloatField()
    kamm = models.FloatField()
    tnitmin = models.FloatField()
    tnitopt = models.FloatField()
    tnitop2 = models.FloatField()
    tnitmax = models.FloatField()
    tnitopt_gauss = models.FloatField()
    scale_tnitopt = models.FloatField()
    rationit = models.FloatField()
    cmin_pdenit = models.FloatField()
    cmax_pdenit = models.FloatField()
    min_pdenit = models.FloatField()
    max_pdenit = models.FloatField()
    ratiodenit = models.FloatField()
    profdenit = models.FloatField()
    vpotdenit = models.FloatField()
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def to_json(self):
        return {
            "QTenFactor": [self.qten_factor, ""],
            "TempDecOptimal": [self.temp_dec_optimal, "C"],
            "MoistureDecOptimal": [self.moisture_dec_optimal, "%"],
            "AOM_FastMaxC_to_N": [self.aom_fast_max_c_to_n, ""],
            "AOM_FastUtilizationEfficiency": [self.aom_fast_utilization_efficiency, ""],
            "AOM_SlowUtilizationEfficiency": [self.aom_slow_utilization_efficiency, ""],
            "ActivationEnergy": [self.activation_energy, ""],
            "AmmoniaOxidationRateCoeffStandard": [self.ammonia_oxidation_rate_coeff_standard, "d-1"],
            "AtmosphericResistance": [self.atmospheric_resistance, "s m-1"],
            "CN_Ratio_SMB": [self.cn_ratio_smb, ""],
            "Denit1": [self.denit1, ""],
            "Denit2": [self.denit2, ""],
            "Denit3": [self.denit3, ""],
            "HydrolysisKM": [self.hydrolysis_km, ""],
            "HydrolysisP1": [self.hydrolysis_p1, ""],
            "HydrolysisP2": [self.hydrolysis_p2, ""],
            "ImmobilisationRateCoeffNH4": [self.immobilisation_rate_coeff_nh4, "d-1"],
            "ImmobilisationRateCoeffNO3": [self.immobilisation_rate_coeff_no3, "d-1"],
            "Inhibitor_NH3": [self.inhibitor_nh3, "kg N m-3"],
            "LimitClayEffect": [self.limit_clay_effect, "kg kg-1"],
            "MaxMineralisationDepth": self.max_mineralisation_depth,
            "N2OProductionRate": [self.n2o_production_rate, "d-1"],
            "NitriteOxidationRateCoeffStandard": [self.nitrite_oxidation_rate_coeff_standard, "d-1"],
            "PartSMB_Fast_to_SOM_Fast": [self.part_smb_fast_to_som_fast, ""],
            "PartSMB_Slow_to_SOM_Fast": [self.part_smb_slow_to_som_fast, ""],
            "PartSOM_Fast_to_SOM_Slow": [self.part_som_fast_to_som_slow, ""],
            "PartSOM_to_SMB_Fast": [self.part_som_to_smb_fast, ""],
            "PartSOM_to_SMB_Slow": [self.part_som_to_smb_slow, ""],
            "SMB_FastDeathRateStandard": [self.smb_fast_death_rate_standard, "d-1"],
            "SMB_FastMaintRateStandard": [self.smb_fast_maint_rate_standard, "d-1"],
            "SMB_SlowDeathRateStandard": [self.smb_slow_death_rate_standard, "d-1"],
            "SMB_SlowMaintRateStandard": [self.smb_slow_maint_rate_standard, "d-1"],
            "SMB_UtilizationEfficiency": [self.smb_utilization_efficiency, "d-1"],
            "SOM_FastDecCoeffStandard": [self.som_fast_dec_coeff_standard, "d-1"],
            "SOM_FastUtilizationEfficiency": [self.som_fast_utilization_efficiency, ""],
            "SOM_SlowDecCoeffStandard": [self.som_slow_dec_coeff_standard, "d-1"],
            "SOM_SlowUtilizationEfficiency": [self.som_slow_utilization_efficiency, ""],
            "SpecAnaerobDenitrification": [self.spec_anaerob_denitrification, "g gas-N g CO2-C-1"],
            "TransportRateCoeff": [self.transport_rate_coeff, "d-1"],
            "type": self.__class__.__name__,
            "stics": {
                "use_n2o": self.use_n2o,
                "use_nit": self.use_nit,
                "use_denit": self.use_denit,
                "code_vnit": [
                    self.code_vnit, 
                    "",
                    "Nitrification rate dependence on NH4: 1 = the nitrification rate is proportional to NH4 concentration ; 2 = the nitrification rate depends on NH4 concentration according to a Michaelis-Menten function (saturation)",
                    ],
                "code_tnit": [
                    self.code_tnit, 
                    "",
                    "Temperature function for nitrification: 1 = piecewise linear function ; 2 = gaussian function"
                    ],
                "code_rationit": [
                    self.code_rationit, 
                    "",
                    "Nitrification N20 ratio: 1 = constant ratio (parameter) ; 2 = variable ratio according to soil water filled pore space (WFPS)"
                    ],
                "code_hourly_wfps_nit": [
                    self.code_hourly_wfps_nit, 
                    "",
                    "Hourly WFPS calculation for nitrification: 1 = calculation of the hourly evolution of soil WFPS for days with rainfall ; 2 = option disabled"
                    ],
                "code_pdenit": [
                    self.code_pdenit, 
                    "",
                    "Denitrification potential: 1 = constant potential (parameter) ; 2 = potential estimated from soil organic C content"
                    ],
                "code_ratiodenit": [
                    self.code_ratiodenit, 
                    "",
                    "Denitrification N20 ratio: 1 = constant ratio (parameter) ; 2 = variable ratio according to pH, soil WFPS, NO3 concentration"
                    ],
                "code_hourly_wfps_denit": [
                    self.code_hourly_wfps_denit, 
                    "",
                    "Hourly WFPS calculation for denitrification: 1 = calculation of the hourly evolution of soil WFPS for days with rainfall ; 2 = option disabled"
                    ],
                "hminn": [
                    self.hminn, 
                    "",
                    "fraction of the soil water content at field capacity below which the nitrification is zero",
                    "param_gen.xml"
                    ],
                "hoptn": [
                    self.hoptn, 
                    "",
                    "fraction of the soil water content at field capacity above which nitrification is optimal",
                    "param_gen.xml"
                    ],
                "pHminnit": [
                    self.phminnit, 
                    "",
                    "pH below which nitrification is zero",
                    "param_gen.xml"
                    ],
                "pHmaxnit": [
                    self.phmaxnit, 
                    "",
                    "pH above which nitrification is optimal",
                    "param_gen.xml"
                    ],
                "nh4_min": [
                    self.nh4_min, 
                    "mg NH4-N/kg soil",
                    "minimum soil ammonium content (fixed ammonium, not available for nitrification)",
                    "param_gen.xml"
                    ],
                "pHminden": [
                    self.phminden, 
                    "",
                    "pH below which denitrification only produces N2O (for a soil WFPS of ~80%)",
                    "param_gen.xml"
                    ],
                "pHmaxden": [
                    self.phmaxden, 
                    "",
                    "pH above which denitrification only produces N2 (for a soil WFPS of ~80%)",
                    "param_gen.xml"
                    ],
                "wfpsc": [
                    self.wfpsc, 
                    "",
                    "pH above which denitrification only produces N2 (for a soil WFPS of ~80%)",
                    "param_gen.xml"
                    ],
                "tdenitopt_gauss": [
                    self.tdenitopt_gauss,
                     "°C",
                    "optimum temperature for denitrification",
                    "param_gen.xml"
                     ],
                "scale_tdenitopt": [
                    self.scale_tdenitopt, 
                    "°C",
                    "parameter controlling the range of temperature favourable to denitrification",
                    "param_gen.xml"
                    ],
                "Kd": [
                    self.kd, 
                    "mg NO3-N/L",
                    "half saturation constant for the function relating the NO3 concentration to the denitrification rate. Multiplying by gravimetric soil water content yields mg NO3-N/kg soil",
                    "param_gen.xml"
                    ],
                "k_desat": [
                    self.k_desat, 
                    "1/day",
                    "constant controlling the rate of desaturation of a soil layer (Hourly WFPS option enabled). A value of 3.0 allows 95% of the water to be drained in one day and thus to reach a soil water content very close to field capacity",
                    "param_gen.xml"
                    ],
                "fnx": [
                    self.fnx, 
                    "1/day",
                    "potential nitrification rate expressed as the fraction of available ammonium nitrified in one day (linear option for nitrification rate)",
                    "param_gen.xml"
                    ],
                "vnitmax": [
                    self.vnitmax, 
                    "mg NH4-N/kg soil/day",
                    "nitrification potential (Michaelis-Menten option for nitrification rate)",
                    "param_gen.xml"
                    ],
                "Kamm": [
                    self.kamm, 
                    "mg NH4-N/L",
                    "half saturation constant for the function relating NH4 concentration to nitrification rate (Michaelis-Menten option for nitrification rate). Multiplying by gravimetric soil water content yields mg NH4-N/kg soil",
                    "param_gen.xml"
                    ],
                "tnitmin": [
                    self.tnitmin, 
                    "°C",
                    "temperature below which nitrification is zero (option piecewise linear function)",
                    "param_gen.xml"
                    ],
                "tnitopt": [
                    self.tnitopt, 
                    "°C",
                    "temperature above which nitrification is optimal (option piecewise linear function)",
                    "param_gen.xml"
                    ],
                "tnitop2": [
                    self.tnitop2, 
                    "°C",
                    "temperature above which nitrification begins to decrease after the optimum (option piecewise linear function)",
                    "param_gen.xml"
                    ],
                "tnitmax": [
                    self.tnitmax, 
                    "°C",
                    "temperature above which nitrification is zero (option piecewise linear function)",
                    "param_gen.xml"
                    ],
                "tnitopt_gauss": [
                    self.tnitopt_gauss, 
                    "°C",
                    "optimum temperature for nitrification (if gaussian function option enabled)",
                    "param_gen.xml"
                    ],
                "scale_tnitopt": [
                    self.scale_tnitopt, 
                    "°C",
                    "parameter controlling the range of temperature favourable to nitrification (if gaussian function option enabled)",
                    "param_gen.xml"
                    ],
                "rationit": [
                    self.rationit, 
                    "",
                    "proportion of nitrified nitrogen emitted as N2O (if constant ratio option enabled)",
                    "param_gen.xml"
                    ],
                "cmin_pdenit": [
                    self.cmin_pdenit, 
                    "% [0-100]",
                    "organic carbon content below which the denitrification potential is minimal (option calculation of the denitrification potential enabled)",
                    "param_gen.xml"
                    ],
                "cmax_pdenit": [
                    self.max_pdenit, 
                    "% [0-100]", 
                    "organic carbon content above which the denitrification potential is maximum (option calculation of the denitrification potential enabled)", 
                    "param_gen.xml"
                    ],
                "min_pdenit": [
                    self.min_pdenit,
                    "mg N/Kg soil/day",
                    "minimum value of denitrification potential (option calculation of denitrification potential enabled)",
                    "param_gen.xml"
                    ],
                "max_pdenit": [
                    self.max_pdenit,
                    "mg N/kg soil/day",
                    "maximum value of denitrification potential (option calculation of denitrification potential enabled)",
                    "param_gen.xml"
                    ],
                "ratiodenit": [
                    self.ratiodenit,
                    "",
                    "proportion of denitrified nitrogen emitted as N2O (if constant ratio option enabled)",
                    "param_gen.xml"
                    ],
                "profdenit": [
                    self.profdenit,
                    "cm",
                    "maximum soil depth affected by denitrification",
                    "sols.xml"
                    ],
                "vpotdenit": [
                    self.vpotdenit,
                    "kg N/ha/day",
                    "denitrification potential (constant potential option) over soil thickness defined by profdenit",
                    "sols.xml"
                    ]
            }
        }

    @classmethod
    def create_or_update_from_json(cls, json_file_path):

        with open(json_file_path, 'r') as file:
            data = json.load(file)
            
            name = json_file_path.split('/')[-1].split('.')[0]
        if data.get('type') == "UserSoilOrganicParameters":
            soil_organic_params, created = cls.objects.update_or_create(
                name=name,
                qten_factor = data.get('QTenFactor')[0],
                temp_dec_optimal = data.get('TempDecOptimal')[0],
                moisture_dec_optimal = data.get('MoistureDecOptimal')[0],
                aom_fast_max_c_to_n = data.get('AOM_FastMaxC_to_N')[0],
                aom_fast_utilization_efficiency = data.get('AOM_FastUtilizationEfficiency')[0],
                aom_slow_utilization_efficiency = data.get('AOM_SlowUtilizationEfficiency')[0],
                activation_energy = data.get('ActivationEnergy')[0],
                ammonia_oxidation_rate_coeff_standard = data.get('AmmoniaOxidationRateCoeffStandard')[0],
                atmospheric_resistance = data.get('AtmosphericResistance')[0],
                cn_ratio_smb = data.get('CN_Ratio_SMB')[0],
                denit1 = data.get('Denit1')[0],
                denit2 = data.get('Denit2')[0],
                denit3 = data.get('Denit3')[0],
                hydrolysis_km = data.get('HydrolysisKM')[0],
                hydrolysis_p1 = data.get('HydrolysisP1')[0],
                hydrolysis_p2 = data.get('HydrolysisP2')[0],
                immobilisation_rate_coeff_nh4 = data.get('ImmobilisationRateCoeffNH4')[0],
                immobilisation_rate_coeff_no3 = data.get('ImmobilisationRateCoeffNO3')[0],
                inhibitor_nh3 = data.get('Inhibitor_NH3')[0],
                limit_clay_effect = data.get('LimitClayEffect')[0],
                max_mineralisation_depth = data.get('MaxMineralisationDepth'),
                n2o_production_rate = data.get('N2OProductionRate')[0],
                nitrite_oxidation_rate_coeff_standard = data.get('NitriteOxidationRateCoeffStandard')[0],
                part_smb_fast_to_som_fast = data.get('PartSMB_Fast_to_SOM_Fast')[0],
                part_smb_slow_to_som_fast = data.get('PartSMB_Slow_to_SOM_Fast')[0],
                part_som_fast_to_som_slow = data.get('PartSOM_Fast_to_SOM_Slow')[0],
                part_som_to_smb_fast = data.get('PartSOM_to_SMB_Fast')[0],
                part_som_to_smb_slow = data.get('PartSOM_to_SMB_Slow')[0],
                smb_fast_death_rate_standard = data.get('SMB_FastDeathRateStandard')[0],
                smb_fast_maint_rate_standard = data.get('SMB_FastMaintRateStandard')[0],
                smb_slow_death_rate_standard = data.get('SMB_SlowDeathRateStandard')[0],
                smb_slow_maint_rate_standard = data.get('SMB_SlowMaintRateStandard')[0],
                smb_utilization_efficiency = data.get('SMB_UtilizationEfficiency')[0],
                som_fast_dec_coeff_standard = data.get('SOM_FastDecCoeffStandard')[0],
                som_fast_utilization_efficiency = data.get('SOM_FastUtilizationEfficiency')[0],
                som_slow_dec_coeff_standard = data.get('SOM_SlowDecCoeffStandard')[0],
                som_slow_utilization_efficiency = data.get('SOM_SlowUtilizationEfficiency')[0],
                spec_anaerob_denitrification = data.get('SpecAnaerobDenitrification')[0],
                transport_rate_coeff = data.get('TransportRateCoeff')[0],
                use_n2o = data.get('stics').get('use_n2o'),
                use_nit = data.get('stics').get('use_nit'),
                use_denit = data.get('stics').get('use_denit'),
                code_vnit = data.get('stics').get('code_vnit')[0],
                code_tnit = data.get('stics').get('code_tnit')[0],
                code_rationit = data.get('stics').get('code_rationit')[0],
                code_hourly_wfps_nit = data.get('stics').get('code_hourly_wfps_nit')[0],
                code_pdenit = data.get('stics').get('code_pdenit')[0],
                code_ratiodenit = data.get('stics').get('code_ratiodenit')[0],
                code_hourly_wfps_denit = data.get('stics').get('code_hourly_wfps_denit')[0],
                hminn = data.get('stics').get('hminn')[0],
                hoptn = data.get('stics').get('hoptn')[0],
                phminnit = data.get('stics').get('pHminnit')[0],
                phmaxnit = data.get('stics').get('pHmaxnit')[0],
                nh4_min = data.get('stics').get('nh4_min')[0],
                phminden = data.get('stics').get('pHminden')[0],
                phmaxden = data.get('stics').get('pHmaxden')[0],
                wfpsc = data.get('stics').get('wfpsc')[0],
                tdenitopt_gauss = data.get('stics').get('tdenitopt_gauss')[0],
                scale_tdenitopt = data.get('stics').get('scale_tdenitopt')[0],
                kd = data.get('stics').get('Kd')[0],
                k_desat = data.get('stics').get('k_desat')[0],
                fnx = data.get('stics').get('fnx')[0],
                vnitmax = data.get('stics').get('vnitmax')[0],
                kamm = data.get('stics').get('Kamm')[0],
                tnitmin = data.get('stics').get('tnitmin')[0],
                tnitopt = data.get('stics').get('tnitopt')[0],
                tnitop2 = data.get('stics').get('tnitop2')[0],
                tnitmax = data.get('stics').get('tnitmax')[0],
                tnitopt_gauss = data.get('stics').get('tnitopt_gauss')[0],
                scale_tnitopt = data.get('stics').get('scale_tnitopt')[0],
                rationit = data.get('stics').get('rationit')[0],
                cmin_pdenit = data.get('stics').get('cmin_pdenit')[0],
                cmax_pdenit = data.get('stics').get('cmax_pdenit')[0],
                min_pdenit = data.get('stics').get('min_pdenit')[0],
                max_pdenit = data.get('stics').get('max_pdenit')[0],
                ratiodenit = data.get('stics').get('ratiodenit')[0],
                profdenit = data.get('stics').get('profdenit')[0],
                vpotdenit = data.get('stics').get('vpotdenit')[0],
            )
            return soil_organic_params

# modify implemented
class SoilTemperatureModuleParameters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    base_temperature = models.FloatField()
    initial_surface_temperature = models.FloatField()
    density_air = models.FloatField()
    specific_heat_capacity_air = models.FloatField()
    density_humus = models.FloatField()
    specific_heat_capacity_humus = models.FloatField()
    density_water = models.FloatField()
    specific_heat_capacity_water = models.FloatField()
    quartz_raw_density = models.FloatField()
    specific_heat_capacity_quartz = models.FloatField()
    n_tau = models.FloatField()
    soil_albedo = models.FloatField()
    soil_moisture = models.FloatField()
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def to_json(self):
        return {
        "BaseTemperature": self.base_temperature,
        "InitialSurfaceTemperature": self.initial_surface_temperature,        
        "DensityAir": [self.density_air, "kg/m3"],
        "SpecificHeatCapacityAir": [self.specific_heat_capacity_air, "J/(kg*K)", "at 300 K"],
        "DensityHumus": [self.density_humus, "kg/m3"],
        "SpecificHeatCapacityHumus": [self.specific_heat_capacity_humus, "J/(kg*K)"],
        "DensityWater": [self.density_water, "kg/m3"],
        "SpecificHeatCapacityWater": [self.specific_heat_capacity_water, "J/(kg*K)"], 
        "QuartzRawDensity": [self.quartz_raw_density, "kg/m3"],
        "SpecificHeatCapacityQuartz": [self.specific_heat_capacity_quartz, "J/(kg*K)"],
        
        "NTau": self.n_tau,
        "SoilAlbedo": self.soil_albedo,
        "SoilMoisture": self.soil_moisture,
        "type": "SoilTemperatureModuleParameters"
        }

    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        if data.get('type') == "SoilTemperatureModuleParameters":
            # Create or update SoilTemperatureModuleParameters object based on JSON data
            soil_temp_params, created = cls.objects.update_or_create(
                base_temperature=data.get('BaseTemperature'),
                initial_surface_temperature=data.get('InitialSurfaceTemperature'),
                density_air=data.get('DensityAir')[0],
                specific_heat_capacity_air=data.get('SpecificHeatCapacityAir')[0],
                density_humus=data.get('DensityHumus')[0],
                specific_heat_capacity_humus=data.get('SpecificHeatCapacityHumus')[0],
                density_water=data.get('DensityWater')[0],
                specific_heat_capacity_water=data.get('SpecificHeatCapacityWater')[0],
                quartz_raw_density=data.get('QuartzRawDensity')[0],
                specific_heat_capacity_quartz=data.get('SpecificHeatCapacityQuartz')[0],
                n_tau=data.get('NTau'),
                soil_albedo=data.get('SoilAlbedo'),
                soil_moisture=data.get('SoilMoisture')
            )

            if created or not soil_temp_params._state.adding:
                soil_temp_params.save()

            return soil_temp_params

# modify implemented
class UserSoilTransportParameters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    # default = models.BooleanField(default=False)
    ad = models.FloatField()
    diffusion_coefficient_standard = models.FloatField()
    dispersion_length = models.FloatField()
    n_deposition = models.FloatField()
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def to_json(self):
        return {
            "AD": self.ad,
            "DiffusionCoefficientStandard": self.diffusion_coefficient_standard,
            "DispersionLength": self.dispersion_length,
            "NDeposition": self.n_deposition,
            "type": self.__class__.__name__
        }
    
    @classmethod
    def create_or_update_from_json(cls, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        if data.get('type') == cls.__class__.__name__:
        # Create or update UserSoilTransport object based on JSON data
            soil_transport_params, created = cls.objects.update_or_create(
                ad=data.get('AD'),
                diffusion_coefficient_standard=data.get('DiffusionCoefficientStandard'),
                dispersion_length=data.get('DispersionLength'),
                n_deposition=data.get('NDeposition'),
                
            )

            if created or not soil_transport_params._state.adding:
                soil_transport_params.save()

            return soil_transport_params
        
class UserSimulationSettings(models.Model):
    """
    This model is the simj json.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    default = models.BooleanField(default=False)

    debug = models.BooleanField(default=True)
    use_secondary_yields = models.BooleanField(default=False)
    nitrogen_response_on = models.BooleanField(default=False)
    water_deficit_response_on = models.BooleanField(default=False)
    emergence_moisture_control_on = models.BooleanField(default=False)
    emergence_flooding_control_on = models.BooleanField(default=False)
    use_n_min_mineral_fertilising_method = models.BooleanField(default=False)
    n_min_user_params_min = models.FloatField(default=None, null=True, blank=True)
    n_min_user_params_max = models.FloatField(default=None, null=True, blank=True)
    n_min_user_params_delay_in_days = models.IntegerField(default=None, null=True, blank=True)
    n_min_fertiliser_partition = models.ForeignKey(MineralFertiliser, on_delete=models.CASCADE, null=True, blank=True)
    julian_day_automatic_fertilising = models.IntegerField(default=None, null=True, blank=True)
    use_automatic_irrigation = models.BooleanField(default=False)
    auto_irrigation_params_nitrate_concentration = models.FloatField(default=None, null=True, blank=True)
    auto_irrigation_params_sulfate_concentration = models.FloatField(default=None, null=True, blank=True)
    auto_irrigation_params_amount = models.FloatField(default=None, null=True, blank=True)
    auto_irrigation_params_threshold = models.FloatField(default=None, null=True, blank=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        return self.name
    
    def to_json(self):
        return {
            "debug?": self.debug,
            "UseSecondaryYields": self.use_secondary_yields,
            "NitrogenResponseOn": self.nitrogen_response_on,
            "WaterDeficitResponseOn": self.water_deficit_response_on,
            "EmergenceMoistureControlOn": self.emergence_moisture_control_on,
            "EmergenceFloodingControlOn": self.emergence_flooding_control_on,
            "UseNMinMineralFertilisingMethod": self.use_n_min_mineral_fertilising_method,
            "NMinUserParams": {
            "min": self.n_min_user_params_min,
            "max": self.n_min_user_params_max,
            "delayInDays": self.n_min_user_params_delay_in_days
            },
            "NMinFertiliserPartition": self.n_min_fertiliser_partition.to_json() if self.n_min_fertiliser_partition else None,
            "JulianDayAutomaticFertilising": self.julian_day_automatic_fertilising,
            "UseAutomaticIrrigation": self.use_automatic_irrigation,
            "AutoIrrigationParams": {
            "irrigationParameters": {
                "nitrateConcentration": [self.auto_irrigation_params_nitrate_concentration, "mg dm-3"],
                "sulfateConcentration": [self.auto_irrigation_params_sulfate_concentration, "mg dm-3"]
            },
            "amount": [self.auto_irrigation_params_amount, "mm"],
            "threshold": self.auto_irrigation_params_threshold
            }
        }

class SiteParameters(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField() # heightNN
    slope = models.FloatField()
    n_deposition = models.FloatField()
    soil_profile = models.ForeignKey(buek_models.SoilProfile, on_delete=models.CASCADE)

    def to_json(self):
        return {
            "Latitude": self.latitude,
            "Slope": self.slope,
            "HeightNN": [self.altitude, "m"],
            "NDeposition": [self.n_deposition, "kg N ha-1 y-1"],
            "SoilProfileParameters": self.soil_profile.get_monica_horizons_json()
        }


class CentralParameterProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_crop_parameters = models.ForeignKey(UserCropParameters, on_delete=models.CASCADE)
    user_environment_parameters = models.ForeignKey(UserEnvironmentParameters, on_delete=models.CASCADE)
    user_soil_moisture_parameters = models.ForeignKey(UserSoilMoistureParameters, on_delete=models.CASCADE)
    user_soil_transport_parameters = models.ForeignKey(UserSoilTransportParameters, on_delete=models.CASCADE)
    user_soil_organic_parameters = models.ForeignKey(UserSoilOrganicParameters, on_delete=models.CASCADE)
    simulation_parameters = models.ForeignKey(UserSimulationSettings, on_delete=models.CASCADE)
    site_parameters = models.ForeignKey(SiteParameters, on_delete=models.CASCADE)
    def to_json(self):
        return {
            "type": self.__class__.__name__,
            "userCropParameters": self.user_crop_parameters.to_json(),
            "userEnvironmentParameters": self.user_environment_parameters.to_json(),
            "userSoilMoistureParameters": self.user_soil_moisture_parameters.to_json(),
            "userSoilTemperatureParameters": self.user_soil_temperature_parameters.to_json(),
            "userSoilTransportParameters": self.user_soil_transport_parameters.to_json(),
            "userSoilOrganicParameters": self.user_soil_organic_parameters.to_json(),
            "simulationParameters": self.simulation_parameters.to_json(),
            "siteParameters": self.site_parameters.to_json()
        }
    
# Simulation related models
class SimulationEnvironment(models.Model):
    debug_mode = models.BooleanField(default=True)
    params = models.JSONField()
    crop_rotation = ArrayField(models.BooleanField(), null=True, blank=True) # worksteps

    user_environment_parameters = models.ForeignKey(UserEnvironmentParameters, on_delete=models.CASCADE)
    general_soil_moisture_parameters = models.ForeignKey(UserSoilMoistureParameters, on_delete=models.CASCADE)
    general_soil_organic_parameters = models.ForeignKey(UserSoilOrganicParameters, on_delete=models.CASCADE)
    general_soil_transport = models.ForeignKey(UserSoilTransportParameters, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)

    def to_json(self):
        return {
            "type": "Env",
            "debugMode": self.debug_mode,
            "params": self.params,
            "cropRotation": self.crop_rotation.to_json(),
            "UserEnvironmentParameters": self.user_environment_parameters.to_json(),
            "GeneralSoilMoistureParameters": self.general_soil_moisture_parameters.to_json(),
            "GeneralSoilOrganicParameters": self.general_soil_organic_parameters.to_json(),
            "GeneralSoilTransport": self.general_soil_transport.to_json()
        }


class Workstep(models.Model):
    date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta: 
        abstract = True
        
    def to_json(self):
        return {
            "date": self.date.strftime('%Y-%m-%d') if self.date else None
        }
    

class WorkstepMineralFertilisation(Workstep):
    amount = models.FloatField()
    mineral_fertiliser = models.ForeignKey(MineralFertiliser, on_delete=models.CASCADE)

    def to_json(self):
        json_data = super().to_json()
        json_data.update({
            "type": "MineralFertilisation",
            "amount": [self.amount, "kg N ha-1"], # TODO the unit was actually 'kg N' - is it per ha?
            "partition": self.mineral_fertiliser.to_json()
        })
        return json_data

class WorkstepOrganicFertilisation(Workstep):
    amount = models.FloatField()
    organic_fertiliser = models.ForeignKey(OrganicFertiliser, on_delete=models.CASCADE)
    incorporation = models.BooleanField()

    def to_json(self):
        json_data = super().to_json()
        json_data.update({
            "type": "OrganicFertilisation",
            "amount": [self.amount, "kg N ha-1"], # TODO the unit was actually 'kg N' - is it per ha?
            "parameters": self.mineral_fertiliser.to_json(),
            "incorporation": self.incorporation
        })
        return json_data

class WorkstepTillage(Workstep):
    tillage_depth = models.FloatField()

    def to_json(self):
        json_data = super().to_json()
        json_data.update({
            "type": "Tillage",
            "depth": [self.tillage_depth, "m"]
        })
        return json_data
    
class WorkstepIrrigation(Workstep):
    amount = models.IntegerField()

    def to_json(self):
        json_data = super().to_json()
        json_data.update({
            "type": "Irrigation",
            "amount": [self.amount, "mm"]
        })
        return json_data

class WorkstepSowing(Workstep):
    species = models.ForeignKey(SpeciesParameters, on_delete=models.CASCADE)
    cultivar = models.ForeignKey(CultivarParameters, on_delete=models.CASCADE)
    residue_parameters = models.ForeignKey(CropResidueParameters, on_delete=models.CASCADE)
    
    # plants per m2
    plant_density = models.IntegerField() # TODO this is actually a SPECIES parameter!!!
    
    def to_json(self):
        json_data = super().to_json()
        json_data.update({
            "is-winter-crop": self.cultivar.is_winter_crop, 
            "is-perennial-crop": self.species.is_perennial_crop, 
            "cropParams": {
                "species": self.species.to_json(),
                "cultivar": self.cultivar.to_json(),
            },
            "residueParams": self.residue_parameters.to_json(),
        })
        return json_data

class WorkstepHarvest(Workstep):

    def to_json(self):
        json_data = super().to_json()
        json_data.update({
            "type": "Harvest"
        })
        return json_data

    
class Output(models.Model):
    short_name = models.CharField(max_length=100)
    to_layers = models.BooleanField(default=False)
    to_organs = models.BooleanField(default=False)
    settable = models.BooleanField(default=False)
    unit = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
class OutputEvent(models.Model):
    short_name = models.CharField(max_length=100)
    event_json = models.JSONField()
    description = models.TextField(null=True, blank=True)

class OutputAggregation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

class Organ(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)



# --------------------GEODATA ------------------------------------

# from django.contrib.gis.db import models

# class DigitalElevationModel(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     grid_file = models.FileField(upload_to='ascii_grids/')
#     crs = models.IntegerField(default=25832) 

#     def __str__(self):
#         return self.name


# TODO: can be deleted, but is used in process_wheather_data
class WeatherData(models.Model):
    point = gis_models.PointField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    date = models.DateField()
    tas = models.FloatField()
    tasmin = models.FloatField()
    tasmax = models.FloatField()
    sfcwind = models.FloatField()
    rsds = models.FloatField()
    pr = models.FloatField()
    hurs = models.FloatField()

    def __str__(self):
        return f"{self.date} - {self.point}"


"""
This model is a GIS multipoint of the centroids of the DWD weather grid.
All gridcells are represented in this table, the column is_valid holds the Boolean of weather 
it is a no_data point.
The nearest climate station refers to those referenced in the klimertrag sowing dates (class SeedHarvestDates).
 The forecast_lat_idx and forecast_lon_idx are the indices of the DWD forecast grid (5km x 5km) that are closest to the
grid cell.
"""
class DWDGridToPointIndices(models.Model):
    point = gis_models.PointField()
    lat = models.FloatField()
    lon = models.FloatField()
    lat_idx = models.IntegerField()
    lon_idx = models.IntegerField()
    is_valid = models.BooleanField(default=True)
    nearest_climate_station_for_sowing_dates = models.IntegerField(null=True, blank=True)
    forecast_lat_idx = models.IntegerField(null=True, blank=True)
    forecast_lon_idx = models.IntegerField(null=True, blank=True)

    soilprofile_id = models.IntegerField(null=True, blank=True)
    landcover_code = models.IntegerField(null=True, blank=True)
    soilprofile_id_21 = models.IntegerField(null=True, blank=True)
    landcover_code_21 = models.IntegerField(null=True, blank=True)
    soilprofile_id_23 = models.IntegerField(null=True, blank=True)
    landcover_code_23 = models.IntegerField(null=True, blank=True)
    soilprofile_id_31 = models.IntegerField(null=True, blank=True)
    landcover_code_31 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.point} - {self.lat_idx} - {self.lon_idx}"
    
    def to_folder_path(self):
        return f"{self.lat_idx}/{self.lon_idx}/"
    
    def create_instance(self, lat, lat_idx, lon, lon_idx):
        return self.objects.create(point=Point(lat, lon), lat=lat, lat_idx=lat_idx, lon=lon, lon_idx=lon_idx)
    
        """
        Returns all DWDGridToPointIndices instances with points within the given geometry.
        If no points are within the geometry, returns the closest point.
        `geom` should be a GEOSGeometry object representing the desired geometry.
        """
        start = datetime.now()
        
        # Filter instances based on point geometry within the provided geometry
        points_within_geom = cls.objects.filter(point__within=geom)

        if points_within_geom.exists():
            print("Time elapsed: ", datetime.now() - start, 'multiple', len(points_within_geom))
            
            return list(points_within_geom)
        else:
            """
            The input geometry is buffered by 0.0085 degrees, roughly 500+m to find the nearest points in the grid.
            This approach is faster than simply finding the nearest distance and it limits the disatnce to the existing 
            weather data to the buffer"""

            buffered_geom = geom.buffer(.0085)
            filtered_points = cls.objects.filter(point__within=buffered_geom)
            if filtered_points.exists():
                annotated_points = filtered_points.annotate(
                    distance_to_geom=Distance('point', geom)
                )

                closest_point = annotated_points.order_by('distance_to_geom').first()

                if closest_point is not None:
                                      
                    print("Time elapsed: ", datetime.now() - start)
            
                    return [closest_point]
            else:
                # TODO handle error when search area or point is outside of the available weather data
                print("No points found within the buffered geometry")
                return None
            

class DWDForecastGridToPointIndices(models.Model):
    point = gis_models.PointField()
    lat = models.FloatField()
    lon = models.FloatField()
    lat_idx = models.IntegerField()
    lon_idx = models.IntegerField()
    nearest_climate_station_for_sowing_dates = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.point} - {self.lat_idx} - {self.lon_idx}"
    

class SeedHarvestclimateStation(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    geom = gis_models.PointField(blank=True, null=True)

    def __str__(self):
        return f"Climate station at {self.lat} - {self.lon}"
    

# TODO check all crop_txt for the correct cultivar_parameter!! 
class SeedHarvestDates(models.Model):
    climate_station = models.ForeignKey(SeedHarvestclimateStation, on_delete=models.CASCADE)
    name_of_csv = models.CharField(max_length=100, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    crop_txt = models.CharField(max_length=100)
    cultivar_parameters = models.ForeignKey(CultivarParameters, on_delete=models.CASCADE, null=True, blank=True)
    avg_sowing_doy = models.IntegerField(null=True, blank=True)
    no_of_sowing_datasets = models.IntegerField(null=True, blank=True)
    avg_harvest_doy = models.IntegerField(null=True, blank=True)
    no_of_harvest_datasets = models.IntegerField(null=True, blank=True)
    earliest_sowing_doy = models.IntegerField(null=True, blank=True)
    latest_sowing_doy = models.IntegerField(null=True, blank=True)
    earliest_harvest_doy = models.IntegerField(null=True, blank=True)
    latest_harvest_doy = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.crop_txt} - {self.species_parameters_id} - {self.lat} - {self.lon}"
    
    @classmethod
    def load_klimertrag_csv(cls, csv_file_path):
        filename = csv_file_path.split('/')[-1].split('.')[0]
        
        data = pd.read_csv(csv_file_path)
        for index, row in data.iterrows():
            seed_harvest_dates = cls(
                climate_station= SeedHarvestclimateStation.objects.get(id=row.get('climate.station', None)),
                name_of_csv=filename,
                lat=row.get('lat', None),
                lon=row.get('long', None),
                crop_txt=row.get('crop', None),
                avg_sowing_doy=row.get('avg.sowing.doy', None),
                no_of_sowing_datasets=row.get('X..values.sowing', None),
                avg_harvest_doy=row.get('avg.harvest.doy', None),
                no_of_harvest_datasets=row.get('X..values.harvest', None),
                earliest_sowing_doy=row.get('earliest.sowing.doy', None),
                latest_sowing_doy=row.get('latest.sowing.doy', None),
                earliest_harvest_doy=row.get('earliest.harvest.doy', None),
                latest_harvest_doy=row.get('latest.harvest.doy', None)
            )
            seed_harvest_dates.save()

    

    def __str__(self):
        return f"Winter Wheat - {self.seed_harvest_dates}"

           
class DWDGridAsPolygon(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    lat_idx = models.IntegerField()
    lon_idx = models.IntegerField()
    geom = gis_models.PolygonField()
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"Polygon with centroid lat {self.lat} and longitude {self.lon} at the indeices {self.lat_idx} and {self.lon_idx}."

    @classmethod
    def get_idx(cls, lat, lon):
        point = Point(lon, lat)

        try:
            # Find the polygon containing the point
            instance = cls.objects.filter(geom__intersects=point).first()
            return instance.lat_idx, instance.lon_idx
        except cls.DoesNotExist:
            return None, None

class DWDForecastGridAsPolygon(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    lat_idx = models.IntegerField()
    lon_idx = models.IntegerField()
    geom = gis_models.PolygonField()

    def __str__(self):
        return f"Polygon with centroid lat {self.lat} and longitude {self.lon} at the indeices {self.lat_idx} and {self.lon_idx}."

    @classmethod
    def get_idx(cls, lat, lon):
        point = Point(lon, lat)

        try:
            # Find the polygon containing the point
            instance = cls.objects.filter(geom__intersects=point).first()
            return instance.lat_idx, instance.lon_idx
        except cls.DoesNotExist:
            return None, None




class MonicaEnvironment(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    debug_mode = models.BooleanField(default=False)
    params = models.ForeignKey(CentralParameterProvider, on_delete=models.CASCADE, null=True, blank=True)
    crop_rotation = models.JSONField(null=True, blank=True)
    crop_rotations = models.JSONField(null=True, blank=True, default=None)
    events = models.JSONField(null=True, blank=True)

    def to_json(self):
        return{
            "type": "Env",
            "debugMode": self.debug_mode,
            "params": self.params.to_json(),
            "cropRotation": self.crop_rotation,
            "cropRotations": None,
            "events": self.events
        }
        


class MonicaSimulation(models.Model): # Project at Point
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    slope = models.FloatField()
    n_deposition = models.FloatField()
    soil_profile = models.ForeignKey(buek_models.SoilProfile, on_delete=models.CASCADE)
