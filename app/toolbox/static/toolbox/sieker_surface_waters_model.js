import { ToolboxProject } from './toolbox_project.js';
export class SiekerSurfaceWaters extends ToolboxProject {
    constructor (data = {}) {
        super(data);
        this.toolboxType = 'sieker_surface_water';
        // this.id = data.id ?? null;
        // this.userField = data.userField ?? null;

        this.all_sieker_surface_water_ids = data.all_sieker_surface_water_ids ?? [];
        this.selected_sieker_surface_waters = data.selected_sieker_surface_waters ?? [];

        this.all_sieker_water_level_ids = data.all_sieker_water_level_ids ?? [];
        this.selected_sieker_water_levels = data.selected_sieker_water_levels ?? [];

        this.sieker_surface_water_filtered = data.sieker_surface_water_filtered ?? false;

        this.sieker_surface_water_d_max_m_max = data.sieker_surface_water_d_max_m_max ?? null;
        this.sieker_surface_water_d_max_m_min = data.sieker_surface_water_d_max_m_min ?? null;
        this.sieker_surface_water_vol_mio_m3_min = data.sieker_surface_water_vol_mio_m3_min ?? null;
        this.sieker_surface_water_vol_mio_m3_max = data.sieker_surface_water_vol_mio_m3_max ?? null;
        this.sieker_surface_water_area_ha_min = data.sieker_surface_water_area_ha_min ?? null;
        this.sieker_surface_water_area_ha_max = data.sieker_surface_water_area_ha_max ?? null;
        // TODO BADESEEN!

        this.all_result_lakes_ids = data.all_result_lakes_ids ?? [];
        
        // this.selected_result_lakes = data.selected_result_lakes ?? [];
        // this.all_result_water_level_ids = data.all_result_water_level_ids ?? [];
        // this.selected_result_water_levels = data.selected_result_water_levels ?? [];
        // this.all_result_timeseries_ids = data.all_result_timeseries_ids ?? [];
        // this.selected_result_timeseriess = data.selected_result_timeseriess ?? [];

        this.result_lakes = data.result_lakes ?? [];
        this.result_stations = data.result_stations ?? [];
        this.result_timeseries = data.result_timeseries ?? [];


    }
    

    static fromJson(json) {
      return new SiekerSurfaceWaters(json);
    }

};

ToolboxProject.registerSubclass('sieker_surface_water', SiekerSurfaceWaters);