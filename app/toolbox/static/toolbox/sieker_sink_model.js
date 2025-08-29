export class SiekerSink {
    constructor (siekerSink = {}) {
        this.id = siekerSink.id ?? null;
        this.userField = siekerSink.userField ?? null;
        this.sieker_sink_volume_max = siekerSink.sieker_sink_volume_max ?? null;
        this.sieker_sink_volume_min = siekerSink.sieker_sink_volume_min ?? null;
        this.sieker_sink_area_max = siekerSink.sieker_sink_area_max ?? null;
        this.sieker_sink_area_min = siekerSink.sieker_sink_area_min ?? null;
        this.sieker_sink_depth_min = siekerSink.sieker_sink_depth_min ?? null;
        this.sieker_sink_depth_max = siekerSink.sieker_sink_depth_max ?? null;
        this.sieker_sink_avg_depth_min = siekerSink.sieker_sink_avg_depth_min ?? null;
        this.sieker_sink_avg_depth_max = siekerSink.sieker_sink_avg_depth_max ?? null;

        // this.sieker_sink_max_elevation_min = siekerSink.sieker_sink_max_elevation_min ?? null;
        // this.sieker_sink_max_elevation_max = siekerSink.sieker_sink_max_elevation_max ?? null;
        // this.sieker_sink_min_elevation_min = siekerSink.sieker_sink_min_elevation_min ?? null;
        // this.sieker_sink_min_elevation_max = siekerSink.sieker_sink_min_elevation_max ?? null;
        this.sieker_sink_urbanarea_percent_min = siekerSink.sieker_sink_urbanarea_percent_min ?? null;
        this.sieker_sink_urbanarea_percent_max = siekerSink.sieker_sink_urbanarea_percent_max ?? null;
        this.sieker_sink_wetlands_percent_min = siekerSink.sieker_sink_wetlands_percent_min ?? null;
        this.sieker_sink_wetlands_percent_max = siekerSink.sieker_sink_wetlands_percent_max ?? null;

        this.sieker_sink_distance_t_min = siekerSink.sieker_sink_distance_t_min ?? null;
        this.sieker_sink_distance_t_max = siekerSink.sieker_sink_distance_t_max ?? null;
        this.sieker_sink_dist_lake_min = siekerSink.sieker_sink_dist_lake_min ?? null;
        this.sieker_sink_dist_lake_max = siekerSink.sieker_sink_dist_lake_max ?? null;

        this.sieker_sink_waterdist_min = siekerSink.sieker_sink_waterdist_min ?? null;
        this.sieker_sink_waterdist_max = siekerSink.sieker_sink_waterdist_max ?? null;

        this.all_sieker_sink_ids = siekerSink.all_sieker_sink_ids ?? [];
        this.selected_sieker_sinks = siekerSink.selected_sieker_sinks ?? [];

        this.sieker_sink_feasibility = siekerSink.sieker_sink_feasibility ?? [];

        this.selected_sieker_sinks = siekerSink.selected_sieker_sinks ?? [];

    }

    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new SiekerSink(json);
    }
        // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('sieker_sink', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('sieker_sink');
        return storedProject ? SiekerSink.fromJson(JSON.parse(storedProject)) : null;
    }
};
