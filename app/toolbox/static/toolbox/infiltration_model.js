
export class Infiltration {
    constructor (infiltration = {}) {
        this.id = infiltration.id ?? null;
        this.userField = infiltration.userField ?? null;

        this.sink_area_min = infiltration.sink_area_min ?? null;
        this.sink_area_max = infiltration.sink_area_max ?? null;
        this.sink_volume_min = infiltration.sink_volume_min ?? null;
        this.sink_volume_max = infiltration.sink_volume_max ?? null;
        this.sink_depth_min = infiltration.sink_depth_min ?? null;
        this.sink_depth_max = infiltration.sink_depth_max ?? null;
        this.sink_land_use = infiltration.sink_land_use ?? [];
        this.all_sink_ids = infiltration.all_sink_ids ?? [];
        this.selected_sinks = infiltration.selected_sinks ?? [];

        this.enlarged_sink_area_min = infiltration.enlarged_sink_area_min ?? null;
        this.enlarged_sink_area_max = infiltration.enlarged_sink_area_max ?? null;
        this.enlarged_sink_volume_min = infiltration.enlarged_sink_volume_minn ?? null;
        this.enlarged_sink_volume_max = infiltration.enlarged_sink_volume_max ?? null;
        this.enlarged_sink_depth_min = infiltration.enlarged_sink_depth_min ?? null;
        this.enlarged_sink_depth_max = infiltration.enlarged_sink_depth_max ?? null;
        this.enlarged_sink_volume_construction_barrier_min = infiltration.enlarged_sink_volume_construction_barrier_min ?? null;
        this.enlarged_sink_volume_construction_barrier_max = infiltration.enlarged_sink_volume_construction_barrier_max ?? null;
        this.enlarged_sink_volume_gained_min = infiltration.enlarged_sink_volume_gained_min ?? null;
        this.enlarged_sink_volume_gained_max = infiltration.enlarged_sink_volume_gained_max ?? null;
        this.enlarged_sink_land_use = infiltration.enlarged_sink_land_use ?? [];

        this.all_enlarged_sink_ids = infiltration.all_enlarged_sink_ids ?? [];
        this.selected_enlarged_sinks = infiltration.selected_enlarged_sinks ?? [];

        this.stream_min_surplus_volume_min = infiltration.stream_min_surplus_volume_min ?? null;
        this.stream_min_surplus_volume_max = infiltration.stream_min_surplus_volume_max ?? null;
        this.stream_mean_surplus_volume_min = infiltration.stream_mean_surplus_volume_min ?? null;
        this.stream_mean_surplus_volume_max = infiltration.stream_mean_surplus_volume_max ?? null;
        this.stream_max_surplus_volume_min = infiltration.stream_max_surplus_volume_min ?? null;
        this.stream_max_surplus_volume_max = infiltration.stream_max_surplus_volume_max ?? null;
        this.stream_plus_days_min = infiltration.stream_plus_days_min ?? null;
        this.stream_plus_days_max = infiltration.stream_plus_days_max ?? null;
        this.stream_distance_to_userfield = infiltration.stream_distance_to_userfield ?? 0;

        this.lake_min_surplus_volume_min = infiltration.lake_min_surplus_volume_min ?? null;
        this.lake_min_surplus_volume_max = infiltration.lake_min_surplus_volume_max ?? null;
        this.lake_mean_surplus_volume_min = infiltration.lake_mean_surplus_volume_min ?? null;
        this.lake_mean_surplus_volume_max = infiltration.lake_mean_surplus_volume_max ?? null;
        this.lake_max_surplus_volume_min = infiltration.lake_max_surplus_volume_min ?? null;
        this.lake_max_surplus_volume_max = infiltration.lake_max_surplus_volume_max ?? null;
        this.lake_plus_days_min = infiltration.lake_plus_days_min ?? null;
        this.lake_plus_days_max = infiltration.lake_plus_days_max ?? null;
        this.lake_distance_to_userfield = infiltration.lake_distance_to_userfield ?? 0;

        this.all_lake_ids = infiltration.all_lake_ids ?? [];
        this.selected_lakes = infiltration.selected_lakes ?? [];
        this.all_stream_ids = infiltration.all_stream_ids ?? [];
        this.selected_streams = infiltration.selected_streams ?? [];

        this.weighting_overall_usability = infiltration.weighting_overall_usability ?? 20;
        this.weighting_soil_index = infiltration.weighting_soil_index ?? 80;

        this.weighting_forest_field_capacity = infiltration.weighting_forest_field_capacity ?? 33;
        this.weighting_forest_hydraulic_conductivity_1m = infiltration.weighting_forest_hydraulic_conductivity_1m ?? 33;
        this.weighting_forest_hydraulic_conductivity_2m = infiltration.weighting_forest_hydraulic_conductivity_2m ?? 33;

        this.weighting_agriculture_field_capacity = infiltration.weighting_agriculture_field_capacity ?? 33;
        this.weighting_agriculture_hydromorphy = infiltration.weighting_agriculture_hydromorphy ?? 33;
        this.weighting_agriculture_soil_type = infiltration.weighting_agriculture_soil_type ?? 33;

        this.weighting_grassland_field_capacity = infiltration.weighting_grassland_field_capacity ?? 25;
        this.weighting_grassland_hydromorphy = infiltration.weighting_grassland_hydromorphy ?? 25;
        this.weighting_grassland_soil_type = infiltration.weighting_grassland_soil_type ?? 25;
        this.weighting_grassland_soil_water_ratio = infiltration.weighting_grassland_soil_water_ratio ?? 25;

    }

    updateButtonState() {
        console.log('updateButtonState', this);
        if (document.getElementById("divInfiltration")){
            
            const hasSink = this.selected_sinks.length > 0;
            const hasEnlargedSink = this.selected_enlarged_sinks.length > 0;
            const hasStream = this.selected_streams.length > 0;
            const hasLake = this.selected_lakes.length > 0;
            
    
            // Adjust to your actual button ID
            if ((hasSink || hasEnlargedSink) && (hasLake || hasStream)) {
                document.getElementById("btnGetInlets").classList.remove('disabled');
                console.log('(hasSink && hasWaterbody)')
            } else {
                document.getElementById("btnGetInlets").classList.add('disabled');
                console.log('!(hasSink && hasWaterbody)')
            };
        }
    };

    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new Infiltration(json);
    }
         // Save project to localStorage
    saveToLocalStorage() {
        this.updateButtonState();
        localStorage.setItem('infiltration', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('infiltration');
        return storedProject ? Infiltration.fromJson(JSON.parse(storedProject)) : null;
    }




};