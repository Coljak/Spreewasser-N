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
        this.sieker_sink_urbanarea_percent_min = data.sieker_sink_urbanarea_percent_min ?? null;
        this.sieker_sink_urbanarea_percent_max = data.sieker_sink_urbanarea_percent_max ?? null;
        this.sieker_sink_wetlands_percent_min = data.sieker_sink_wetlands_percent_min ?? null;
        this.sieker_sink_wetlands_percent_max = data.sieker_sink_wetlands_percent_max ?? null;

        this.sieker_sink_feasibility = data.sieker_sink_feasibility ?? [];

        // this.sieker_sink_distance_t_min = data.sieker_sink_distance_t_min ?? null;
        // this.sieker_sink_distance_t_max = data.sieker_sink_distance_t_max ?? null;
        // this.sieker_sink_dist_lake_min = data.sieker_sink_dist_lake_min ?? null;
        // this.sieker_sink_dist_lake_max = data.sieker_sink_dist_lake_max ?? null;

        // this.sieker_sink_waterdist_min = data.sieker_sink_waterdist_min ?? null;
        // this.sieker_sink_waterdist_max = data.sieker_sink_waterdist_max ?? null;

        this.all_sieker_sink_ids = data.all_sieker_sink_ids ?? [];
        this.selected_sieker_sinks = data.selected_sieker_sinks ?? [];

        this.sieker_stream_min_surplus_volume_min = data.sieker_stream_min_surplus_volume_min ?? null;
        this.sieker_stream_min_surplus_volume_max = data.sieker_stream_min_surplus_volume_max ?? null;
        this.sieker_stream_mean_surplus_volume_min = data.sieker_stream_mean_surplus_volume_min ?? null;
        this.sieker_stream_mean_surplus_volume_max = data.sieker_stream_mean_surplus_volume_max ?? null;
        this.sieker_stream_max_surplus_volume_min = data.sieker_stream_max_surplus_volume_min ?? null;
        this.sieker_stream_max_surplus_volume_max = data.sieker_stream_max_surplus_volume_max ?? null;
        this.sieker_stream_plus_days_min = data.sieker_stream_plus_days_min ?? null;
        this.sieker_stream_plus_days_max = data.sieker_stream_plus_days_max ?? null;
        this.sieker_stream_distance_to_userfield = data.sieker_stream_distance_to_userfield ?? 0;

        this.sieker_lake_min_surplus_volume_min = data.sieker_lake_min_surplus_volume_min ?? null;
        this.sieker_lake_min_surplus_volume_max = data.sieker_lake_min_surplus_volume_max ?? null;
        this.sieker_lake_mean_surplus_volume_min = data.sieker_lake_mean_surplus_volume_min ?? null;
        this.sieker_lake_mean_surplus_volume_max = data.sieker_lake_mean_surplus_volume_max ?? null;
        this.sieker_lake_max_surplus_volume_min = data.sieker_lake_max_surplus_volume_min ?? null;
        this.sieker_lake_max_surplus_volume_max = data.sieker_lake_max_surplus_volume_max ?? null;
        this.sieker_lake_plus_days_min = data.sieker_lake_plus_days_min ?? null;
        this.sieker_lake_plus_days_max = data.sieker_lake_plus_days_max ?? null;
        this.sieker_lake_distance_to_userfield = data.sieker_lake_distance_to_userfield ?? 0;

        this.all_sieker_lake_ids = data.all_sieker_lake_ids ?? [];
        this.selected_sieker_lakes = data.selected_sieker_lakes ?? [];
        this.all_sieker_stream_ids = data.all_sieker_stream_ids ?? [];
        this.selected_sieker_streams = data.selected_sieker_streams ?? [];

        this.result_sinks = data.result_sinks ?? [];
        this.result_streams = data.result_streams ?? [];
        this.result_lakes = data.result_lakes ?? [];
        this.result_timeseries = data.result_timeseries ?? [];
        this.result_result = data.result_result ?? [];
        this.selected_sieker_sink_results = data.selected_sieker_sink_results ?? [];

    }

    updateButtonState() {
        if (document.getElementById("divSiekerSink")){
            
            const hasSink = this.selected_sieker_sinks.length > 0;
            const hasStream = this.selected_sieker_streams.length > 0;
            const hasLake = this.selected_sieker_lakes.length > 0;
            const btn = document.getElementById("btnGetSiekerSinkResults")
            const btnSpan = document.getElementById('spanBtnGetSiekerSinkResults');
    
            // Adjust to your actual button ID
            if ((hasSink) && (hasLake || hasStream)) {
                btn.classList.remove('disabled');
                btnSpan.removeAttribute('title');

            } else {
                btn.classList.add('disabled');
                btnSpan.setAttribute('title', 'Sie müssen mindestens eine Senke und ein Gewässer auswählen!');

            }
        }
    };

    static fromJson(json) {
      return new SiekerSink(json);
    }

    saveToLocalStorage() {
        super.saveToLocalStorage(); 
        this.updateButtonState();  
    }
};

ToolboxProject.registerSubclass('sieker_sink', SiekerSink);