
import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, populateDropdown } from '/static/shared/utils.js';
export class MonicaCalculation {
    constructor(project) {
        this.project = project;
        this.startDate = null;
        this.endDate = null;
        this.creationDate = null;
        this.name = null;
        this.description = null;
        this.daily = {
            Date: [],
            Precip: [],
            Irrig: [],
            AbBiom: [],
            Stage: [],
            Yield: [],
            LAI: [],
            PASW: [],
            Mois_1: [],
            Mois_2: [],
            Mois_3: [],
            SOC_1: [],
            SOC_2: [],
            SOC_3: [],
        };
    }
};


export class MonicaProject {
    constructor(project = {}) {
        this.id = project.id ?? null;
        this.name = project.name ?? '';
        this.updated = project.updated ?? null;
        this.todaysDate = project.todaysDate ?? new Date().toISOString().split('T')[0];
        this.startDate = project.startDate ?? '2024-01-01';
        this.endDate = project.endDate ?? '2024-08-31';
        this.description = project.description ?? '';
        // Site
        this.siteId = project.siteId ?? null;
        this.longitude = project.longitude ?? 10.0;
        this.latitude = project.latitude ?? 52.0;
        this.userField = project.userField ?? null;
        this.altitude = project.altitude ?? 0;
        this.slope = project.slope ?? 0;
        this.n_deposition = project.n_deposition ?? 0;
        this.soilProfileType = project.soilProfileType ?? 'buekSoilProfile';
        this.soilProfileId = project.soilProfileId ?? null;
        this.soilProfileBuekPolygons = project.soilProfileBuekPolygons ?? [];
        this.profile_source = project.profile_source ?? 'recommended';
        this.soilProfileLandusage = project.soilProfileLandusage ?? null;
        this.soilProfileAreaPercentage = project.soilProfileAreaPercentage ?? null;
        this.soilProfileSystemUnit = project.soilProfileSystemUnit ?? null;
        
        // this.swnForecast = project.swnForecast ?? false;
        // Crop Raotation
        if (Array.isArray(project.rotation) && project.rotation.length > 0) {
            console.log('MonicaProject constructor project.rotation', project.rotation);
            this.rotation = project.rotation.map(rotation => new Rotation(rotation.rotationIndex, rotation));
        } else {
            this.rotation = [];  
            this.addRotation();  
        }

        // Model setup
        this.modelSetupId = project.modelSetupId ?? 1;
        this.userEnvironmentParametersId = project.userEnvironmentParametersId ?? 1;
        this.userSoilMoistureParametersId = project.userSoilMoistureParametersId ?? 1;
        this.userSoilTemperatureParametersId = project.userSoilTemperatureParametersId ?? 1;
        this.userSoilTransportParametersId = project.userSoilTransportParametersId ?? 1;
        this.userCropParametersId = project.userCropParametersId ?? 1;
        this.userSoilOrganicParametersId = project.userSoilOrganicParametersId ?? 1;
        this.userSimulationSettingsId = project.userSimulationSettingsId ?? 1;
        
    }

    // Convert instance to JSON for storage
    toJson() {
        console.log("MonicaProject toJson", this);
        return JSON.stringify(this);
    }

    // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('monica_project', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('monica_project');
        return storedProject ? MonicaProject.fromJson(JSON.parse(storedProject)) : null;
    }

    // Static method to create MonicaProject from JSON
    static fromJson(json) {
        return new MonicaProject(json);
    }

    // Add a new rotation with default worksteps
    addRotation() {
        console.log('MonicaProject addRotation');
        if (!Array.isArray(this.rotation)) {
            this.rotation = [];
        }
        const rotationIndex = this.rotation.length;
        const rotation = new Rotation(rotationIndex);

        this.rotation.push(rotation);
        this.saveToLocalStorage();
    }

    getRotation(rotationIndex) {
        return this.rotation[rotationIndex]
    }


    addWorkstep(workstepType, date=null, rotationIndex, options = {}) {
        console.log('MonicaProject addWorkstep', workstepType, date, rotationIndex, options);
        let rotation = this.rotation[rotationIndex];
        
        if (date === null) {
            console.log('this.rotation[rotationIndex]', this.rotation[rotationIndex])
            // let dateObj = new Date(this.rotation[rotationIndex].find(ws => ws.workstepIndex === this.rotation[rotationIndex].workstepIndex)?.date);
            let previousWorkstep = this.rotation[rotationIndex].getWorkstep(rotation.workstepIndex)
            console.log('previousWorkstep', previousWorkstep);
            let previousDate = previousWorkstep.date;
            console.log('previousDate', previousDate)
            let dateObj = new Date(previousDate)
            console.log('1',dateObj)
            dateObj.setDate(dateObj.getDate() + 1);
            console.log('2', dateObj)
            date = dateObj.toISOString().slice(0, 10);
            console.log('Calculated date for new workstep:', date);
        }
        
        this.rotation[rotationIndex].workstepIndex +=1;
        
        const workstep = new Workstep(workstepType, date, this.rotation[rotationIndex].workstepIndex, options);
        rotation.workstepIndex += 1;
        this.rotation[rotationIndex][workstepType].push(workstep);
        this.saveToLocalStorage();
        return workstep;
    }
};

export class Rotation {
    constructor(rotationIndex, existingRotation = {}) {
        this.rotationIndex = rotationIndex;
        // this.workstepIndex = existingRotation.workstepIndex ?? 0; // 2 because of the sowing and harvestWorksteps

        // Initialize worksteps, ensuring defaults if none exist
        this.sowingWorkstep = existingRotation.sowingWorkstep ?? [new Workstep('sowingWorkstep', null, 0, {
            "species":'',
            "cultivar": null,
            "residue": null
            })];
        this.harvestWorkstep = existingRotation.harvestWorkstep ?? [new Workstep('harvestWorkstep', null, 1, {})];
        this.tillageWorkstep = existingRotation.tillageWorkstep ?? [];
        this.mineralFertilisationWorkstep = existingRotation.mineralFertilisationWorkstep ?? [];
        this.organicFertilisationWorkstep = existingRotation.organicFertilisationWorkstep ?? [];
        this.irrigationWorkstep = existingRotation.irrigationWorkstep ?? [];
        this.automaticHarvestWorkstep = existingRotation.automaticHarvestWorkstep ?? [];
        this.nDemandFertilizationWorkstep = existingRotation.nDemandFertilizationWorkstep ?? [];
    
        const allWorksteps = [
            ...this.sowingWorkstep,
            ...this.harvestWorkstep,
            ...this.tillageWorkstep,
            ...this.mineralFertilisationWorkstep,
            ...this.organicFertilisationWorkstep,
            ...this.irrigationWorkstep,
            ...this.automaticHarvestWorkstep,
            ...this.nDemandFertilizationWorkstep
        ];

        if (allWorksteps.length === 0) {
            this.workstepIndex = 0; // no worksteps yet
        } else {
            this.workstepIndex = Math.max(...allWorksteps.map(ws => ws.workstepIndex));
        }
    
    
    }

    getWorkstep(targetIndex) {
    // Normalize targetIndex to a number if provided
        if (typeof targetIndex !== 'number' || Number.isNaN(targetIndex)) {
            targetIndex = undefined;
        }

        let found = null;
        // collect all worksteps
        const all = [];

        for (const key of Object.keys(this)) {
        if (key === 'workstepIndex') continue;
        const arr = this[key];
        if (!Array.isArray(arr)) continue;
        for (const ws of arr) {
            // normalize the stored index to number if possible
            const idx = Number(ws?.workstepIndex);
            if (Number.isFinite(idx)) {
            // push normalized object so comparisons are numeric
            all.push({ ws, idx });
            if (idx === targetIndex) {
                return ws; // exact match immediately
            }
            }
        }
        }

    // if no exact match and no targetIndex provided, return the latest (max idx)
        if (all.length === 0) return null;

        // find max index entry
        let max = all[0];
        for (const entry of all) {
        if (entry.idx > max.idx) max = entry;
        }

        // if targetIndex was provided but not found, try closest lower index:
        if (typeof targetIndex === 'number') {
        // find largest idx <= targetIndex
        let best = null;
        for (const entry of all) {
            if (entry.idx <= targetIndex) {
            if (!best || entry.idx > best.idx) best = entry;
            }
        }
        return best ? best.ws : max.ws;
        }

    // targetIndex not provided → return latest
    return max.ws;
  }

}

export class Workstep {
    constructor(workstep, date = null, workstepIndex = 0, options = {}) {

        this.options = options;
        this.workstep = workstep;
        this.date = date;
        this.workstepIndex = workstepIndex;
        this.options = options;
    }
};
