import { ToolboxProject } from './toolbox_project.js';

export class Injection extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'injection';
        // this.id = data.id ?? null;
        // this.userField = data.userField ?? null;
        // TODO
        this.weighting_aquifer_thickness = data.weighting_aquifer_thickness ?? 5;    
        this.weighting_depth_groundwater = data.weighting_depth_groundwater ?? 5;
        this.weighting_hydraulic_conductivity = data.weighting_hydraulic_conductivity ?? 5;
        this.weighting_land_use = data.weighting_land_use ?? 5;
        this.weighting_distance_to_source_water = data.weighting_distance_to_source_water ?? 5;
        this.weighting_distance_to_well = data.weighting_distance_to_well ?? 5;

        this.aquifer_thickness_thickness_gt_60 = data.aquifer_thickness_thickness_gt_60 ?? 5;
        this.aquifer_thickness_thickness_40_to_60 = data.aquifer_thickness_thickness_40_to_60 ?? 4;
        this.aquifer_thickness_thickness_30_to_40 = data.aquifer_thickness_thickness_30_to_40 ?? 3;
        this.aquifer_thickness_thickness_20_to_30 = data.aquifer_thickness_thickness_20_to_30 ?? 2;
        this.aquifer_thickness_thickness_lt_20 = data.aquifer_thickness_thickness_lt_20 ?? 1;
        this.depth_groundwater_depth_lt_20 = data.depth_groundwater_depth_lt_20 ?? 5;
        this.depth_groundwater_depth_20_to_30 = data.depth_groundwater_depth_20_to_30 ?? 4;
        this.depth_groundwater_depth_30_to_40 = data.depth_groundwater_depth_30_to_40 ?? 3;
        this.depth_groundwater_depth_40_to_50 = data.depth_groundwater_depth_40_to_50 ?? 2;
        this.depth_groundwater_depth_gt_50 = data.depth_groundwater_depth_gt_50 ?? 1;
        this.land_use_forest_closed_coniferous = data.land_use_forest_closed_coniferous ?? 5;
        this.land_use_forest_closed_deciduous = data.land_use_forest_closed_deciduous ?? 5;
        this.land_use_forest_closed_mixed = data.land_use_forest_closed_mixed ?? 5;
        this.land_use_forest_closed_unknown = data.land_use_forest_closed_unknown ?? 5;
        this.land_use_forest_open_coniferous = data.land_use_forest_open_coniferous ?? 5;
        this.land_use_forest_open_deciduous = data.land_use_forest_open_deciduous ?? 5;
        this.land_use_forest_open_mixed = data.land_use_forest_open_mixed ?? 5;
        this.land_use_forest_open_unknown = data.land_use_forest_open_unknown ?? 5;
        this.land_use_shrubs = data.land_use_shrubs ?? 4;
        this.land_use_herbaceous_vegetation = data.land_use_herbaceous_vegetation ?? 5;
        this.land_use_cropland = data.land_use_cropland ?? 2;
        this.land_use_urban = data.land_use_urban ?? 0;
        this.land_use_permanent_waterbodies = data.land_use_permanent_waterbodies ?? 0;
        this.land_use_herbaceous_wetland = data.land_use_herbaceous_wetland ?? 0;
        this.distance_to_source_distance_lt_250 = data.distance_to_source_distance_lt_250 ?? 0;
        this.distance_to_source_distance_250_to_500 = data.distance_to_source_distance_250_to_500 ?? 1;
        this.distance_to_source_distance_500_to_800 = data.distance_to_source_distance_500_to_800 ?? 5;
        this.distance_to_source_distance_800_1200 = data.distance_to_source_distance_800_1200 ?? 4;
        this.distance_to_source_distance_1200_to_1500 = data.distance_to_source_distance_1200_to_1500 ?? 3;
        this.distance_to_source_distance_gt_1500 = data.distance_to_source_distance_gt_1500 ?? 2;
        this.distance_to_well_zone_1_and_2 = data.distance_to_well_zone_1_and_2 ?? 0;
        this.distance_to_well_zone_3 = data.distance_to_well_zone_3 ?? 5;
        this.distance_to_well_well_catchment = data.distance_to_well_well_catchment ?? 4;
        this.distance_to_well_out_of_catchment_lt_5km = data.distance_to_well_out_of_catchment_lt_5km ?? 3;
        this.distance_to_well_out_of_catchment_gt_5km = data.distance_to_well_out_of_catchment_gt_5km ?? 2;
        this.hydraulic_conductivity_conductivity_gt_30 = data.hydraulic_conductivity_conductivity_gt_30 ?? 5;
        this.hydraulic_conductivity_conductivity_20_to_30 = data.hydraulic_conductivity_conductivity_20_to_30 ?? 4;
        this.hydraulic_conductivity_conductivity_10_to_20 = data.hydraulic_conductivity_conductivity_10_to_20 ?? 3;
        this.hydraulic_conductivity_conductivity_5_to_10 = data.hydraulic_conductivity_conductivity_5_to_10 ?? 2;
        this.hydraulic_conductivity_conductivity_lt_5 = data.hydraulic_conductivity_conductivity_lt_5 ?? 1;


    }
 
    static fromJson(json) {
      return new Injection(json);
    }
};

ToolboxProject.registerSubclass('injection', Injection);
