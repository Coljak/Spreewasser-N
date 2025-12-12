import { ToolboxProject } from './toolbox_project.js';

export class SiekerWetland extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'wetland';    
        this.feasibility = data.feasibility ?? '1';

        this.all_wetland_ids = data.all_wetland_ids ?? [];
        this.selected_wetlands = data.selected_wetlands ?? [];

        this.wetland_stream_mean_surplus_volume_min = data.wetland_stream_mean_surplus_volume_min ?? null;
        this.wetland_stream_mean_surplus_volume_max = data.wetland_stream_mean_surplus_volume_max ?? null;     
        this.wetland_stream_plus_days_min = data.wetland_stream_plus_days_min ?? null;
        this.wetland_stream_plus_days_max = data.wetland_stream_plus_days_max ?? null;
        this.wetland_stream_distance_to_userfield = data.wetland_stream_distance_to_userfield ?? 0;

        this.wetland_lake_mean_surplus_volume_min = data.wetland_lake_mean_surplus_volume_min ?? null;
        this.wetland_lake_mean_surplus_volume_max = data.wetland_lake_mean_surplus_volume_max ?? null;
        this.wetland_lake_plus_days_min = data.wetland_lake_plus_days_min ?? null;
        this.wetland_lake_plus_days_max = data.wetland_lake_plus_days_max ?? null;
        this.wetland_lake_distance_to_userfield = data.wetland_lake_distance_to_userfield ?? 0;

        this.all_wetland_lake_ids = data.all_wetland_lake_ids ?? [];
        this.selected_wetland_lakes = data.selected_wetland_lakes ?? [];
        this.all_wetland_stream_ids = data.all_wetland_stream_ids ?? [];
        this.selected_wetland_streams = data.selected_wetland_streams ?? [];


        this.all_wetland_result_ids = data.all_wetland_result_ids ?? [];
        this.selected_wetland_results = data.selected_wetland_results ?? [];
        // download choices
        this.result_wetlands = data.result_wetlands ?? [];
        this.result_streams = data.result_streams ?? [];
        this.result_lakes = data.result_lakes ?? [];
        this.result_timeseries = data.result_timeseries ?? [];
        this.result_result = data.result_result ?? [];
        this.result_waterbodies = data.result_waterbodies ?? [];
        
        this.result_crs = data.result_crs ?? [];

    }


    static fromJson(json) {
      return new SiekerWetland(json);
    }

    updateButtonState() {
        if (document.getElementById("divSiekerWetland")){

            const hasSink = this.selected_wetlands.length > 0;
            const hasStream = this.selected_wetland_streams.length > 0;
            const hasLake = this.selected_wetland_lakes.length > 0;
            const btn = document.querySelector("#btnGetSiekerWetlandResults");
            const btnSpan = document.getElementById('spanBtnGetSiekerWetlandResults');

            // Adjust to your actual button ID
            if ((hasSink) && (hasLake || hasStream)) {
                btn.classList.remove('disabled');
                btnSpan.removeAttribute('title');

            } else {
                btn.classList.add('disabled');
                btnSpan.setAttribute('title', 'Sie müssen mindestens eine Feuchtgebiet und ein Gewässer auswählen!');

            }
        }
    };

    saveToLocalStorage() {
        super.saveToLocalStorage(); 
        this.updateButtonState();  
    }
};

ToolboxProject.registerSubclass('wetland', SiekerWetland);