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

        this.suitability_tickness_gt_60 = tuMar.suitability_tickness_gt_60 ?? 5;
        this.suitability_tickness_40_to_60 = tuMar.suitability_tickness_40_to_60 ?? 4;
        this.suitability_tickness_30_to_40 = tuMar.suitability_tickness_30_to_40 ?? 3;
        this.suitability_tickness_20_to_30 = tuMar.suitability_tickness_20_to_30 ?? 2;
        this.suitability_tickness_lt_20 = tuMar.suitability_tickness_lt_20 ?? 1;
        this.suitability_depth_lt_20 = tuMar.suitability_depth_lt_20 ?? 5;
        this.suitability_depth_20_to_30 = tuMar.suitability_depth_20_to_30 ?? 4;
        this.suitability_depth_30_to_40 = tuMar.suitability_depth_30_to_40 ?? 3;
        this.suitability_depth_40_to_50 = tuMar.suitability_depth_40_to_50 ?? 2;
        this.suitability_depth_gt_50 = tuMar.suitability_depth_gt_50 ?? 1;
        this.suitability_forest_closed_coniferous = tuMar.suitability_forest_closed_coniferous ?? 5;
        this.suitability_forest_closed_deciduous = tuMar.suitability_forest_closed_deciduous ?? 5;
        this.suitability_forest_closed_mixed = tuMar.suitability_forest_closed_mixed ?? 5;
        this.suitability_forest_closed_unknown = tuMar.suitability_forest_closed_unknown ?? 5;
        this.suitability_forest_open_coniferous = tuMar.suitability_forest_open_coniferous ?? 5;
        this.suitability_forest_open_deciduous = tuMar.suitability_forest_open_deciduous ?? 5;
        this.suitability_forest_open_mixed = tuMar.suitability_forest_open_mixed ?? 5;
        this.suitability_forest_open_unknown = tuMar.suitability_forest_open_unknown ?? 5;
        this.suitability_shrubs = tuMar.suitability_shrubs ?? 4;
        this.suitability_herbaceous_vegetation = tuMar.suitability_herbaceous_vegetation ?? 5;
        this.suitability_cropland = tuMar.suitability_cropland ?? 2;
        this.suitability_urban = tuMar.suitability_urban ?? 0;
        this.suitability_permanent_waterbodies = tuMar.suitability_permanent_waterbodies ?? 0;
        this.suitability_herbaceous_wetland = tuMar.suitability_herbaceous_wetland ?? 0;
        this.suitability_distance_lt_250 = tuMar.suitability_distance_lt_250 ?? 0;
        this.suitability_distance_250_to_500 = tuMar.suitability_distance_250_to_500 ?? 1;
        this.suitability_distance_500_to_800 = tuMar.suitability_distance_500_to_800 ?? 5;
        this.suitability_distance_800_1200 = tuMar.suitability_distance_800_1200 ?? 4;
        this.suitability_distance_1200_to_1500 = tuMar.suitability_distance_1200_to_1500 ?? 3;
        this.suitability_distance_gt_1500 = tuMar.suitability_distance_gt_1500 ?? 2;
        this.suitability_zone_1_and_2 = tuMar.suitability_zone_1_and_2 ?? 0;
        this.suitability_zone_3 = tuMar.suitability_zone_3 ?? 5;
        this.suitability_well_catchment = tuMar.suitability_well_catchment ?? 4;
        this.suitability_out_of_catchment_lt_5km = tuMar.suitability_out_of_catchment_lt_5km ?? 3;
        this.suitability_out_of_catchment_gt_5km = tuMar.suitability_out_of_catchment_gt_5km ?? 2;
        this.suitability_conductivity_gt_30 = tuMar.suitability_conductivity_gt_30 ?? 5;
        this.suitability_conductivity_20_to_30 = tuMar.suitability_conductivity_20_to_30 ?? 4;
        this.suitability_conductivity_10_to_20 = tuMar.suitability_conductivity_10_to_20 ?? 3;
        this.suitability_conductivity_5_to_10 = tuMar.suitability_conductivity_5_to_10 ?? 2;
        this.suitability_conductivity_lt_5 = tuMar.suitability_conductivity_lt_5 ?? 1;


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
