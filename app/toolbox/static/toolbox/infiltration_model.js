import { ToolboxProject } from './toolbox_project.js';

export class Infiltration extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'infiltration';
        // this.id = data.id ?? null;
        // this.userField = data.userField ?? null;

        this.sink_area_min = data.sink_area_min ?? null;
        this.sink_area_max = data.sink_area_max ?? null;
        this.sink_volume_min = data.sink_volume_min ?? null;
        this.sink_volume_max = data.sink_volume_max ?? null;
        this.sink_depth_min = data.sink_depth_min ?? null;
        this.sink_depth_max = data.sink_depth_max ?? null;
        this.sink_land_use = data.sink_land_use ?? [];
        this.all_sink_ids = data.all_sink_ids ?? [];
        this.selected_sinks = data.selected_sinks ?? [];

        this.enlarged_sink_area_min = data.enlarged_sink_area_min ?? null;
        this.enlarged_sink_area_max = data.enlarged_sink_area_max ?? null;
        this.enlarged_sink_volume_min = data.enlarged_sink_volume_minn ?? null;
        this.enlarged_sink_volume_max = data.enlarged_sink_volume_max ?? null;
        this.enlarged_sink_depth_min = data.enlarged_sink_depth_min ?? null;
        this.enlarged_sink_depth_max = data.enlarged_sink_depth_max ?? null;
        this.enlarged_sink_volume_construction_barrier_min = data.enlarged_sink_volume_construction_barrier_min ?? null;
        this.enlarged_sink_volume_construction_barrier_max = data.enlarged_sink_volume_construction_barrier_max ?? null;
        this.enlarged_sink_volume_gained_min = data.enlarged_sink_volume_gained_min ?? null;
        this.enlarged_sink_volume_gained_max = data.enlarged_sink_volume_gained_max ?? null;
        this.enlarged_sink_land_use = data.enlarged_sink_land_use ?? [];

        this.all_enlarged_sink_ids = data.all_enlarged_sink_ids ?? [];
        this.selected_enlarged_sinks = data.selected_enlarged_sinks ?? [];

        this.stream_min_surplus_volume_min = data.stream_min_surplus_volume_min ?? null;
        this.stream_min_surplus_volume_max = data.stream_min_surplus_volume_max ?? null;
        this.stream_mean_surplus_volume_min = data.stream_mean_surplus_volume_min ?? null;
        this.stream_mean_surplus_volume_max = data.stream_mean_surplus_volume_max ?? null;
        this.stream_max_surplus_volume_min = data.stream_max_surplus_volume_min ?? null;
        this.stream_max_surplus_volume_max = data.stream_max_surplus_volume_max ?? null;
        this.stream_plus_days_min = data.stream_plus_days_min ?? null;
        this.stream_plus_days_max = data.stream_plus_days_max ?? null;
        this.stream_distance_to_userfield = data.stream_distance_to_userfield ?? 0;

        this.lake_min_surplus_volume_min = data.lake_min_surplus_volume_min ?? null;
        this.lake_min_surplus_volume_max = data.lake_min_surplus_volume_max ?? null;
        this.lake_mean_surplus_volume_min = data.lake_mean_surplus_volume_min ?? null;
        this.lake_mean_surplus_volume_max = data.lake_mean_surplus_volume_max ?? null;
        this.lake_max_surplus_volume_min = data.lake_max_surplus_volume_min ?? null;
        this.lake_max_surplus_volume_max = data.lake_max_surplus_volume_max ?? null;
        this.lake_plus_days_min = data.lake_plus_days_min ?? null;
        this.lake_plus_days_max = data.lake_plus_days_max ?? null;
        this.lake_distance_to_userfield = data.lake_distance_to_userfield ?? 0;

        this.all_lake_ids = data.all_lake_ids ?? [];
        this.selected_lakes = data.selected_lakes ?? [];
        this.all_stream_ids = data.all_stream_ids ?? [];
        this.selected_streams = data.selected_streams ?? [];

        this.weighting_overall_usability = data.weighting_overall_usability ?? 20;
        this.weighting_soil_index = data.weighting_soil_index ?? 80;

        this.weighting_forest_field_capacity = data.weighting_forest_field_capacity ?? 33;
        this.weighting_forest_hydraulic_conductivity_1m = data.weighting_forest_hydraulic_conductivity_1m ?? 33;
        this.weighting_forest_hydraulic_conductivity_2m = data.weighting_forest_hydraulic_conductivity_2m ?? 33;

        this.weighting_agriculture_field_capacity = data.weighting_agriculture_field_capacity ?? 33;
        this.weighting_agriculture_hydromorphy = data.weighting_agriculture_hydromorphy ?? 33;
        this.weighting_agriculture_soil_type = data.weighting_agriculture_soil_type ?? 33;

        this.weighting_grassland_field_capacity = data.weighting_grassland_field_capacity ?? 25;
        this.weighting_grassland_hydromorphy = data.weighting_grassland_hydromorphy ?? 25;
        this.weighting_grassland_soil_type = data.weighting_grassland_soil_type ?? 25;
        this.weighting_grassland_soil_water_ratio = data.weighting_grassland_soil_water_ratio ?? 25;

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

    

    static fromJson(json) {
      return new Infiltration(json);
    }

};

ToolboxProject.registerSubclass('infiltration', Infiltration);