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

    }

    

    static fromJson(json) {
      return new SiekerSink(json);
    }
};

ToolboxProject.registerSubclass('sieker_sink', SiekerSink);