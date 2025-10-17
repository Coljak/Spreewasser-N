import { ToolboxProject } from './toolbox_project.js';

export class Drainage extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'drainage';
        // this.id = data.id ?? null;
        // this.userField = data.userField ?? null;

        this.location_known = data.location_known ?? true; 
        this.location = data.location ?? null;      
        
        this.threshold = data.threshold ?? 0;    
    }
   

    static fromJson(json) {
      return new Drainage(json);
    }

};
ToolboxProject.registerSubclass('drainage', Drainage);
