import { ToolboxProject } from './toolbox_project.js';

export class Drainage extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'drainage';

        this.location_known = data.location_known ?? true; 
        this.location = data.location ?? null;      
        
        this.drainage_threshold = data.drainage_threshold ?? 0;   
        this.parent_natural_creeks = data.parent_natural_creeks ?? [];
        this.parent_non_natural_creeks = data.parent_non_natural_creeks ?? [];
        this.parent_ditches = data.parent_ditches ?? [];
        this.parent_rivers = data.parent_rivers ?? [];
        this.parent_pipes = data.parent_pipes ?? [];
        this.drainage_natural_creeks = data.drainage_natural_creeks ?? [];
        this.drainage_non_natural_creeks = data.drainage_non_natural_creeks ?? [];
        this.drainage_ditches = data.drainage_ditches ?? [];
        this.drainage_rivers = data.drainage_rivers ?? [];
        this.drainage_pipes = data.drainage_pipes ?? [];
        this.drainage_network_types = data.drainage_network_types ?? [];
        this.drained_area_types = data.drained_area_types ?? [];

        this.result_probability_raster = data.result_probability_raster ?? [];
        this.result_drainage_network = data.result_drainage_network ?? [];
        this.result_drained_areas = data.result_drained_areas ?? [];
        
    }
   

    static fromJson(json) {
      return new Drainage(json);
    }
    saveToLocalStorage() {
      this.parents = [...this.parent_ditches, ...this.parent_rivers, ...this.parent_pipes, ...this.parent_non_natural_creeks, ...this.parent_natural_creeks];  
        super.saveToLocalStorage(); 
        
    }

};
ToolboxProject.registerSubclass('drainage', Drainage);
