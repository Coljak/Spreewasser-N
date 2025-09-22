export class SiekerWetland {
    constructor (siekerWetland = {}) {
        this.id = siekerWetland.id ?? null;
        this.userField = siekerWetland.userField ?? null;

        this.wetland_landuse = siekerWetland.wetland_landuse ?? [];        
        this.feasibility = siekerWetland.feasibility ?? '1';

        this.all_sieker_wetland_ids = siekerWetland.all_sieker_wetland_ids ?? [];
        this.selected_sieker_wetlands = siekerWetland.selected_sieker_wetlands ?? [];

        this.all_filtered_sieker_wetland_ids = siekerWetland.all_filtered_sieker_wetland_ids ?? [];

        this.all_sieker_wetland_measure_ids = siekerWetland.all_sieker_wetland_measure_ids ?? [];
        this.selected_sieker_wetland_measures = siekerWetland.selected_sieker_wetland_measures ?? [];
    }
    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new SiekerWetland(json);
    }

    // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('sieker_wetlands', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('sieker_wetlands');
        return storedProject ? SiekerWetland.fromJson(JSON.parse(storedProject)) : null;
    }
};
