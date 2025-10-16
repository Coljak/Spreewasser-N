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
        this.gek_costs_max = data.gek_costs_max ?? null;
        this.gek_costs_min = data.gek_costs_min ?? null;

        this.all_sieker_gek_ids = data.all_sieker_gek_ids ?? [];
        this.selected_sieker_geks = data.selected_sieker_geks ?? [];

        this.all_filtered_sieker_gek_ids = data.all_filtered_sieker_gek_ids ?? [];

        this.all_sieker_gek_measure_ids = data.all_sieker_gek_measure_ids ?? [];
        this.selected_sieker_gek_measures = data.selected_sieker_gek_measures ?? [];
    }
   

    static fromJson(json) {
      return new SiekerGek(json);
    }


};

ToolboxProject.registerSubclass('sieker_gek', SiekerGek);