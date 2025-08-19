export class SiekerSurfaceWaters {
    constructor (siekerSurfaceWaters = {}) {
        this.id = siekerSurfaceWaters.id ?? null;
        this.userField = siekerSurfaceWaters.userField ?? null;
        this.sieker_surface_waters_distance_min = siekerSurfaceWaters.sieker_surface_waters_distance_min ?? null;
        this.all_sieker_large_lake_ids = siekerSurfaceWaters.all_sieker_large_lake_ids ?? [];
        this.selected_sieker_large_lakes = siekerSurfaceWaters.selected_sieker_large_lakes ?? [];

        this.sieker_large_lake_d_max_m_max = siekerSurfaceWaters.sieker_large_lake_d_max_m_max ?? null;
        this.sieker_large_lake_d_max_m_min = siekerSurfaceWaters.sieker_large_lake_d_max_m_min ?? null;
        this.sieker_large_lake_vol_mio_m3_min = siekerSurfaceWaters.sieker_large_lake_vol_mio_m3_min ?? null;
        this.sieker_large_lake_vol_mio_m3_max = siekerSurfaceWaters.sieker_large_lake_vol_mio_m3_max ?? null;
        this.sieker_large_lake_area_ha_min = siekerSurfaceWaters.sieker_large_lake_area_ha_min ?? null;
        this.sieker_large_lake_area_ha_max = siekerSurfaceWaters.sieker_large_lake_area_ha_max ?? null;
        // TODO BADESEEN!



    }
    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new SiekerSurfaceWaters(json);
    }

    // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('projectSiekerSurfaceWaters', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('projectSiekerSurfaceWaters');
        return storedProject ? SiekerSurfaceWaters.fromJson(JSON.parse(storedProject)) : null;
    }
};

