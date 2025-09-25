export class TuMar {
    constructor (tuMar = {}) {
        this.id = tuMar.id ?? null;
        this.userField = tuMar.userField ?? null;
        // TODO
        this.weighting_aquifer_thickness = tuMar.weighting_aquifer_thickness ?? 5;    
        this.weighting_depth_groundwater = tuMar.weighting_depth_groundwater ?? 5;
        this.weighting_hydraulic_conductivity = tuMar.weighting_hydraulic_conductivity ?? 5;
        this.weighting_land_use = tuMar.weighting_land_use ?? 5;
        this.weighting_distance_to_source_water = tuMar.weighting_distance_to_source_water ?? 5;
        this.weighting_distance_to_well = tuMar.weighting_distance_to_well ?? 5;

        this.aquifer_thickness_thickness_gt_60 = tuMar.aquifer_thickness_thickness_gt_60 ?? 5;
        this.aquifer_thickness_thickness_40_to_60 = tuMar.aquifer_thickness_thickness_40_to_60 ?? 4;
        this.aquifer_thickness_thickness_30_to_40 = tuMar.aquifer_thickness_thickness_30_to_40 ?? 3;
        this.aquifer_thickness_thickness_20_to_30 = tuMar.aquifer_thickness_thickness_20_to_30 ?? 2;
        this.aquifer_thickness_thickness_lt_20 = tuMar.aquifer_thickness_thickness_lt_20 ?? 1;
        this.depth_groundwater_depth_lt_20 = tuMar.depth_groundwater_depth_lt_20 ?? 5;
        this.depth_groundwater_depth_20_to_30 = tuMar.depth_groundwater_depth_20_to_30 ?? 4;
        this.depth_groundwater_depth_30_to_40 = tuMar.depth_groundwater_depth_30_to_40 ?? 3;
        this.depth_groundwater_depth_40_to_50 = tuMar.depth_groundwater_depth_40_to_50 ?? 2;
        this.depth_groundwater_depth_gt_50 = tuMar.depth_groundwater_depth_gt_50 ?? 1;
        this.land_use_forest_closed_coniferous = tuMar.land_use_forest_closed_coniferous ?? 5;
        this.land_use_forest_closed_deciduous = tuMar.land_use_forest_closed_deciduous ?? 5;
        this.land_use_forest_closed_mixed = tuMar.land_use_forest_closed_mixed ?? 5;
        this.land_use_forest_closed_unknown = tuMar.land_use_forest_closed_unknown ?? 5;
        this.land_use_forest_open_coniferous = tuMar.land_use_forest_open_coniferous ?? 5;
        this.land_use_forest_open_deciduous = tuMar.land_use_forest_open_deciduous ?? 5;
        this.land_use_forest_open_mixed = tuMar.land_use_forest_open_mixed ?? 5;
        this.land_use_forest_open_unknown = tuMar.land_use_forest_open_unknown ?? 5;
        this.land_use_shrubs = tuMar.land_use_shrubs ?? 4;
        this.land_use_herbaceous_vegetation = tuMar.land_use_herbaceous_vegetation ?? 5;
        this.land_use_cropland = tuMar.land_use_cropland ?? 2;
        this.land_use_urban = tuMar.land_use_urban ?? 0;
        this.land_use_permanent_waterbodies = tuMar.land_use_permanent_waterbodies ?? 0;
        this.land_use_herbaceous_wetland = tuMar.land_use_herbaceous_wetland ?? 0;
        this.distance_to_source_distance_lt_250 = tuMar.distance_to_source_distance_lt_250 ?? 0;
        this.distance_to_source_distance_250_to_500 = tuMar.distance_to_source_distance_250_to_500 ?? 1;
        this.distance_to_source_distance_500_to_800 = tuMar.distance_to_source_distance_500_to_800 ?? 5;
        this.distance_to_source_distance_800_1200 = tuMar.distance_to_source_distance_800_1200 ?? 4;
        this.distance_to_source_distance_1200_to_1500 = tuMar.distance_to_source_distance_1200_to_1500 ?? 3;
        this.distance_to_source_distance_gt_1500 = tuMar.distance_to_source_distance_gt_1500 ?? 2;
        this.distance_to_well_zone_1_and_2 = tuMar.distance_to_well_zone_1_and_2 ?? 0;
        this.distance_to_well_zone_3 = tuMar.distance_to_well_zone_3 ?? 5;
        this.distance_to_well_well_catchment = tuMar.distance_to_well_well_catchment ?? 4;
        this.distance_to_well_out_of_catchment_lt_5km = tuMar.distance_to_well_out_of_catchment_lt_5km ?? 3;
        this.distance_to_well_out_of_catchment_gt_5km = tuMar.distance_to_well_out_of_catchment_gt_5km ?? 2;
        this.hydraulic_conductivity_conductivity_gt_30 = tuMar.hydraulic_conductivity_conductivity_gt_30 ?? 5;
        this.hydraulic_conductivity_conductivity_20_to_30 = tuMar.hydraulic_conductivity_conductivity_20_to_30 ?? 4;
        this.hydraulic_conductivity_conductivity_10_to_20 = tuMar.hydraulic_conductivity_conductivity_10_to_20 ?? 3;
        this.hydraulic_conductivity_conductivity_5_to_10 = tuMar.hydraulic_conductivity_conductivity_5_to_10 ?? 2;
        this.hydraulic_conductivity_conductivity_lt_5 = tuMar.hydraulic_conductivity_conductivity_lt_5 ?? 1;


    }
    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new TuMar(json);
    }

    // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('tu_mar', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('tu_mar');
        return storedProject ? TuMar.fromJson(JSON.parse(storedProject)) : null;
    }
};
