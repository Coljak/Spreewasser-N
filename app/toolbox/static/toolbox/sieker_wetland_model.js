import { ToolboxProject } from './toolbox_project.js';

export class SiekerWetland extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'sieker_wetland';
        // this.id = data.id ?? null;
        // this.userField = data.userField ?? null;

        this.wetland_landuse = data.wetland_landuse ?? [];        
        this.feasibility = data.feasibility ?? '1';

        this.all_sieker_wetland_ids = data.all_sieker_wetland_ids ?? [];
        this.selected_sieker_wetlands = data.selected_sieker_wetlands ?? [];

        this.all_filtered_sieker_wetland_ids = data.all_filtered_sieker_wetland_ids ?? [];

        this.all_sieker_wetland_measure_ids = data.all_sieker_wetland_measure_ids ?? [];
        this.selected_sieker_wetland_measures = data.selected_sieker_wetland_measures ?? [];
    }


    static fromJson(json) {
      return new SiekerWetland(json);
    }
};

ToolboxProject.registerSubclass('sieker_wetland', SiekerWetland);