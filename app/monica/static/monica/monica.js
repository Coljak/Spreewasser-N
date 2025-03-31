
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
        this.longitude = project.longitude ?? 10.0;
        this.latitude = project.latitude ?? 52.0;
        this.userField = project.userField ?? null;
        // this.swnForecast = project.swnForecast ?? false;

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
        this.soilProfileType = project.soilProfileType ?? 'buekSoilProfile';
        this.soilProfileId = project.soilProfileId ?? null;
    }

    // Convert instance to JSON for storage
    toJson() {
        console.log("MonicaProject toJson", this);
        return JSON.stringify(this);
    }

    // Save project to localStorage
    saveToLocalStorage() {
        console.log('MonicaProject saveToLocalStorage', this);
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

    addWorkstep(workstepType, date=null, rotationIndex, options = {}) {
        console.log('MonicaProject addWorkstep', workstepType, date, rotationIndex, options);
        this.rotation[rotationIndex].workstepIndex += 1;
        const workstepIndex = this.rotation[rotationIndex].workstepIndex;
        const workstep = new Workstep(workstepType, date, workstepIndex, options);

        this.rotation[rotationIndex][workstepType].push(workstep);
        this.saveToLocalStorage();

    }
};

export class Rotation {
    constructor(rotationIndex, existingRotation = {}) {
        this.rotationIndex = rotationIndex;
        this.workstepIndex = existingRotation.workstepIndex ?? 1; // 2 because of the sowing and harvestWorksteps

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

export async function loadProjectFromDB(project_id) {
    console.log('loadProjectFromDB id', project_id);
    return fetch('load-project/' + project_id + '/')
        .then(response => response.json())
        .then(data => {
            if (data.message.success) {
                handleAlerts(data.message);
                const project = new MonicaProject(data.project);
                console.log('loadProjectFromDB project', project);
                project.saveToLocalStorage();
                return project;  // Return the project after it has been loaded
            } else {
                handleAlerts(data.message);
                return null;  // Return null if the project wasn't loaded successfully
            }
        })
        .catch(error => {
            console.error('Error:', error);
            return null;  // Return null in case of error
        });
};

export const loadProjectToGui = (project) => {
    // console.log('loadProjectToGui', project);
    console.log("Project is loading..", project)
    window.isLoading = true;
    document.querySelector('#cropRotation').innerHTML = '';
    
    
    $('#projectName').val(project.name);
    $('#projectDescription').val(project.description);
    $('#id_longitude').val(project.longitude);
    $('#id_latitude').val(project.latitude);
    $('userFieldSelect').val(project.userField);
    
    $('#monicaStartDatePicker').datepicker('update', new Date(project.startDate));
    // TODO check if this is necessary/ what to do with it
    
    $('#monicaEndDatePicker').datepicker('update', new Date(project.endDate));
    $('#id_user_environment').val(Number(project.userEnvironmentParametersId));
    $('#id_user_crop_parameters').val(Number(project.userCropParametersId));
    $('#id_user_simulation_settings').val(project.userSimulationSettingsId);
    $('#id_soil_moisture').val(project.userSoilMoistureParametersId);
    $('#id_soil_organic').val(project.userSoilOrganicParametersId);
    $('#id_soil_temperature').val(project.userSoilTemperatureParametersId);
    $('#id_soil_transport').val(project.userSoilTransportParametersId);
    // console.log('loadProjectToGui project.rotation', project.rotation);
    project.rotation.forEach(rotation => {
        addRotationToGui(rotation.rotationIndex, rotation);
    });
    window.isLoading = false;
};

const addRotationToGui = (rotationIndex, rotation=null) => {

    let exists = false;
    $('#cropRotation').children().each(function() {
        
        if ($(this).attr('rotation-index') === rotationIndex.toString()) {
            exists = true;
        };
    });
    if (!exists) {
        const rotationTemplate = document.getElementById('rotationTemplate').cloneNode(true);
        const newRotation = document.createElement('div');
        newRotation.classList.add('card', 'mb-3', 'rotation');
        newRotation.setAttribute('rotation-index', rotationIndex);

        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body');

        var newId = 'id_workstep_type_' + rotationIndex;
        var workstepSelector = rotationTemplate.querySelector('.workstep-type-select')
        rotationTemplate.querySelector(`label[for="${workstepSelector.id}"]`).htmlFor = newId;
        workstepSelector.setAttribute('id', newId);
        workstepSelector.setAttribute('name', newId);

        cardBody.innerHTML = `<h5 class="card-title">Rotation ${rotationIndex + 1}</h5>` + rotationTemplate.innerHTML;

        newRotation.appendChild(cardBody);
        $('#cropRotation').append(newRotation);

    };

    if (rotation) {
        // const rotationIndex = rotation.rotationIndex;
        Object.entries(rotation).forEach(([workstepType, worksteps]) => { 
            // rotationIndex and workstepIndex is at the same level in the rotation as the workstepTypes
            if (workstepType !== 'rotationIndex' && workstepType !== 'workstepIndex') {
                console.log('AddRotationToGui forEach workstepType', workstepType, 'worksteps', worksteps);
                if (worksteps.length > 0) {
                    worksteps.forEach(workstep => { 
                        addWorkstepToGui(workstepType, rotationIndex, workstep.workstepIndex, workstep=workstep)     

                    }) ;
                };
            };
        });              
    };
};


const addWorkstepToGui = (workstepType, rotationIndex, workstepIndex, workstep=null) => {
    console.log("addWorkstepToGui", workstepType, rotationIndex, workstepIndex, workstep);
    // load and modify the according workstep template
    const formTemplate = document.getElementById(workstepType + '-template');
    const newForm = formTemplate.cloneNode(true);
    newForm.removeAttribute('id');

    newForm.querySelectorAll('*[id]').forEach(element => {
       
        const newId = `${element.id}_${workstepType}_${rotationIndex}_${workstepIndex}`;
        newForm.querySelector(`label[for="${element.id}"]`).htmlFor = newId;
        element.id = newId;
        element.setAttribute('workstep-index', workstepIndex);
        element.setAttribute('workstep-type', workstepType);
        
    });
    newForm.querySelector('form').setAttribute('workstep-type', workstepType);
    newForm.querySelector('form').setAttribute('workstep-index', workstepIndex);
    newForm.querySelector('form').setAttribute('rotation-index', rotationIndex);

    // add and initialize the datepicker
    $(newForm).find('.datepicker').datepicker({
        language: 'de-DE',
        format: "dd.mm.yyyy",
        weekStart: 1,
        autoclose: true
    });

    // TODO test which one is better
    // 
    
    const parentDiv = document.querySelector(`div[rotation-index='${rotationIndex}']`); 
    const cardBody = parentDiv ? parentDiv.querySelector(`:scope > .card-body`) : null;
    const addWorkstepDiv = cardBody.querySelector('.add-workstep');
    cardBody.insertBefore(newForm, addWorkstepDiv);


    
//--------------------------------------------------
    if (workstep) {
        console.log('IN addRotationToGui, if (rotation) workstep', workstepType);
        const datepickerInput = newForm.querySelector('.workstep-datepicker'); // Ensure correct selection
        if (datepickerInput) {
            $(datepickerInput).datepicker('update', new Date(workstep.date));
        } else {
            console.error("Datepicker input not found inside the form.");
        }

        if (workstepType === 'sowingWorkstep') {
            console.log('workstepType if workstep.options.species', workstepType, workstep.options.species);
            const speciesSelector = newForm.querySelector(`select[name="species"]`);
            const cultivarSelector = newForm.querySelector(`select[name="cultivar"]`);
            const residueSelector = newForm.querySelector(`select[name="residue"]`);
            if (!((workstep.options.species === null) || (workstep.options.species === ''))) {
                // console.error('SPECIES!!!!', workstep.options.species);

            // }
            // if (speciesSelector && !speciesSelector.value) {
                
                console.log('speciesSelector', speciesSelector.value);
                // Watch when the species dropdown gets its options
                observeDropdown(`#${speciesSelector.id}`, (dropdown) => {
                    dropdown.value = workstep.options.species;  
                    
                    fetch('/monica/get_options/cultivar-parameters/' + workstep.options.species + '/')
                        .then(response => response.json())
                        .then(data => {
                            populateDropdown(data, cultivarSelector);
                        })
                        .then(() => {
                            cultivarSelector.value = workstep.options.cultivar;  
                        });


                    // TODO these fetches may be duplicates
                    fetch('/monica/get_options/crop-residue-parameters/' + workstep.options.species + '/')
                        .then(response => response.json())
                        .then(data => {
                        populateDropdown(data, residueSelector);
                        })
                        .then(() => {
                            residueSelector.value = workstep.options.residue; 
                        });
                });
                
            } 
            else if (speciesSelector && !speciesSelector.value) {
                speciesSelector.value = workstep.options.species;
            }
            

        } else {    
            for (const [key, value] of Object.entries(workstep.options)) {
                const input = newForm.querySelector(`select[name=${key}], input[name=${key}]`);

                if (input) {
                    if (input.type ==="checkbox") {
                        input.checked = value;
                    } else {
                        input.value = value;
                    }
                } else {
                    console.error("Input not found with name:", key);
                }
            };
        }
    }
};


export function handleDateChange(event) {
    console.log('handleDateChange', event);
    if (!window.isLoading) {
        const input = $(event.target);
        const project = MonicaProject.loadFromLocalStorage();
        let name = input.attr('name');

        const date = input.datepicker('getUTCDate');
        if (date) {  // Prevent errors if datepicker is empty
            project[name] = date.toISOString().split('T')[0];
            console.log(`${input.attr('id')} name:`, name, project[name]);
            project.saveToLocalStorage();
        }
    }
};