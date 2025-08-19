export class SiekerGek {
    constructor (siekerGek = {}) {
        this.id = siekerGek.id ?? null;
        this.userField = siekerGek.userField ?? null;
        this.selected_gek_retention = siekerGek.selected_gek_retention ?? [];
        this.gek_priority = siekerGek.gek_priority ?? null;
        this.landuse = siekerGek.landuse ?? [];
        this.all_sieker_gek_ids = siekerGek.all_sieker_gek_ids ?? [];
        this.selected_sieker_geks = siekerGek.selected_sieker_geks ?? [];

        this.all_sieker_gek_measure_ids = siekerGek.all_sieker_gek_measure_ids ?? [];
        this.selected_sieker_gek_measures = siekerGek.selected_sieker_gek_measures ?? [];
    }
    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new SiekerGek(json);
    }

    // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('projectSiekerGeks', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('projectSiekerGeks');
        return storedProject ? SiekerGek.fromJson(JSON.parse(storedProject)) : null;
    }
};
