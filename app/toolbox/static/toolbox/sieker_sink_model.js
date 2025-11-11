import { ToolboxProject } from './toolbox_project.js';
export class SiekerSink extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'sieker_sink';
        // this.id = data.id ?? null;
        // this.userField = data.userField ?? null;
        this.sieker_sink_volume_max = data.sieker_sink_volume_max ?? null;
        this.sieker_sink_volume_min = data.sieker_sink_volume_min ?? null;
        this.sieker_sink_area_max = data.sieker_sink_area_max ?? null;
        this.sieker_sink_area_min = data.sieker_sink_area_min ?? null;
        this.sieker_sink_depth_min = data.sieker_sink_depth_min ?? null;
        this.sieker_sink_depth_max = data.sieker_sink_depth_max ?? null;
        this.sieker_sink_avg_depth_min = data.sieker_sink_avg_depth_min ?? null;
        this.sieker_sink_avg_depth_max = data.sieker_sink_avg_depth_max ?? null;

        // this.sieker_sink_max_elevation_min = data.sieker_sink_max_elevation_min ?? null;
        // this.sieker_sink_max_elevation_max = data.sieker_sink_max_elevation_max ?? null;
        // this.sieker_sink_min_elevation_min = data.sieker_sink_min_elevation_min ?? null;
        // this.sieker_sink_min_elevation_max = data.sieker_sink_min_elevation_max ?? null;
        this.sieker_sink_urbanarea_percent_min = data.sieker_sink_urbanarea_percent_min ?? null;
        this.sieker_sink_urbanarea_percent_max = data.sieker_sink_urbanarea_percent_max ?? null;
        this.sieker_sink_wetlands_percent_min = data.sieker_sink_wetlands_percent_min ?? null;
        this.sieker_sink_wetlands_percent_max = data.sieker_sink_wetlands_percent_max ?? null;

        this.sieker_sink_distance_t_min = data.sieker_sink_distance_t_min ?? null;
        this.sieker_sink_distance_t_max = data.sieker_sink_distance_t_max ?? null;
        this.sieker_sink_dist_lake_min = data.sieker_sink_dist_lake_min ?? null;
        this.sieker_sink_dist_lake_max = data.sieker_sink_dist_lake_max ?? null;

        this.sieker_sink_waterdist_min = data.sieker_sink_waterdist_min ?? null;
        this.sieker_sink_waterdist_max = data.sieker_sink_waterdist_max ?? null;

        this.all_sieker_sink_ids = data.all_sieker_sink_ids ?? [];
        this.selected_sieker_sinks = data.selected_sieker_sinks ?? [];

        this.sieker_sink_feasibility = data.sieker_sink_feasibility ?? [];

        this.selected_sieker_sinks = data.selected_sieker_sinks ?? [];

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

    }

    

    static fromJson(json) {
      return new SiekerSink(json);
    }
};

ToolboxProject.registerSubclass('sieker_sink', SiekerSink);