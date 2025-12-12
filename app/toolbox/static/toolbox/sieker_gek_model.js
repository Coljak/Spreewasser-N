import { ToolboxProject } from './toolbox_project.js';
export class SiekerGek extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'sieker_gek';
        // this.id = data.id ?? null;
        // this.userField = data.userField ?? null;
        this.gek_priority = data.gek_priority ?? null;
        // gek retention filters
        this.gek_landuse = data.gek_landuse ?? [];   
        // this.selected_gek_landuses = data.selected_gek_landuses ?? [];     
        this.gek_costs_max = data.gek_costs_max ?? null;
        this.gek_costs_min = data.gek_costs_min ?? null;

        this.all_sieker_gek_ids = data.all_sieker_gek_ids ?? [];
        this.selected_sieker_geks = data.selected_sieker_geks ?? [];

        this.all_filtered_sieker_gek_ids = data.all_filtered_sieker_gek_ids ?? [];
        this.selected_filtered_sieker_geks = data.selected_filtered_sieker_geks ?? [];

        this.all_sieker_gek_measure_ids = data.all_sieker_gek_measure_ids ?? [];
        this.selected_sieker_gek_measures = data.selected_sieker_gek_measures ?? [];

        this.result_geks = data.result_geks ?? [];
        this.result_measures = data.result_measures ?? [];
        this.result_crs = data.result_crs ?? [];
    }
   

    static fromJson(json) {
      return new SiekerGek(json);
    }


};

ToolboxProject.registerSubclass('sieker_gek', SiekerGek);