import { ToolboxProject } from './toolbox_project.js';
export class SiekerSurfaceWaters extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'sieker_surface_water';
        // this.id = data.id ?? null;
        // this.userField = data.userField ?? null;
        this.sieker_surface_waters_distance_min = data.sieker_surface_waters_distance_min ?? null;
        this.all_sieker_surface_water_ids = data.all_sieker_surface_water_ids ?? [];
        this.selected_sieker_surface_waters = data.selected_sieker_surface_waters ?? [];

        this.sieker_surface_water_d_max_m_max = data.sieker_surface_water_d_max_m_max ?? null;
        this.sieker_surface_water_d_max_m_min = data.sieker_surface_water_d_max_m_min ?? null;
        this.sieker_surface_water_vol_mio_m3_min = data.sieker_surface_water_vol_mio_m3_min ?? null;
        this.sieker_surface_water_vol_mio_m3_max = data.sieker_surface_water_vol_mio_m3_max ?? null;
        this.sieker_surface_water_area_ha_min = data.sieker_surface_water_area_ha_min ?? null;
        this.sieker_surface_water_area_ha_max = data.sieker_surface_water_area_ha_max ?? null;
        // TODO BADESEEN!



    }
    

    static fromJson(json) {
      return new SiekerSurfaceWaters(json);
    }

};

ToolboxProject.registerSubclass('sieker_surface_water', SiekerSurfaceWaters);