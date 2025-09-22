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



        this.feasibility = tuMar.feasibility ?? '1';

        this.all_sieker_wetland_ids = tuMar.all_sieker_wetland_ids ?? [];
        this.selected_sieker_wetlands = tuMar.selected_sieker_wetlands ?? [];

        this.all_filtered_sieker_wetland_ids = tuMar.all_filtered_sieker_wetland_ids ?? [];

        this.all_sieker_wetland_measure_ids = tuMar.all_sieker_wetland_measure_ids ?? [];
        this.selected_sieker_wetland_measures = tuMar.selected_sieker_wetland_measures ?? [];
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
