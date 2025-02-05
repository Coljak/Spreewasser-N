// import { handleAlerts } from `${staticBasePath}swn/js/base`;
// Utility functions
export const alertBox = document.getElementById('alert-box');

const handleAlerts = (message) => {
    if (message.success == true) {
        var type = 'success';
    } else if (message.success == false) {
        var type = 'warning';
    } else {;};
    alertBox.innerHTML = `
            <div class="alert alert-${type} alert-dismissible " role="alert">
                    ${message.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">
            </div>`;
    alertBox.classList.remove('d-none');
    setTimeout(() => {
        alertBox.classList.add('d-none');
    }, 5000);
};

const getCsrfToken = () => {
    return document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
};

function formatDateToISO(date) {
    return date.toISOString().split('T')[0];
}


class MonicaCalculation {
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
}



export class MonicaProject {
    constructor(project = {}) {
        this.id = project.id ?? null;
        this.name = project.name ?? '';
        this.todaysDate = project.todaysDate ?? new Date().toISOString().split('T')[0];
        this.startDate = project.startDate ?? '2024-01-01';
        this.endDate = project.endDate ?? '2024-08-31';
        this.description = project.description ?? '';
        this.longitude = project.longitude ?? 10.0;
        this.latitude = project.latitude ?? 52.0;
        this.userField = project.userField ?? null;
        this.swnForecast = project.swnForecast ?? false;

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
        this.soilProfileType = project.soilProfileType ?? 'soilprofile';
        this.soilProfileId = project.soilProfileId ?? null;
    }

    // Convert instance to JSON for storage
    toJson() {
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
        if (!Array.isArray(this.rotation)) {
            this.rotation = [];
        }
        const rotationIndex = this.rotation.length;
        const rotation = new Rotation(rotationIndex);

        this.rotation.push(rotation);
        this.saveToLocalStorage();
    }

    addWorkstep(workstepType, rotationIndex) {
        this.rotation[rotationIndex].workstepIndex += 1;
        const workstepIndex = this.rotation[rotationIndex].workstepIndex;
        const workstep = new Workstep(workstepType, null, workstepIndex, {});

        this.rotation[rotationIndex][workstepType].push(workstep);
        this.saveToLocalStorage();

    }
}

class Rotation {
    constructor(rotationIndex, existingRotation = {}) {
        this.rotationIndex = rotationIndex;
        this.workstepIndex = existingRotation.workstepIndex ?? 2; // 2 because of the sowing and harvestWorksteps

        // Initialize worksteps, ensuring defaults if none exist
        this.sowingWorkstep = existingRotation.sowingWorkstep ?? [new Workstep('sowingWorkstep', null, 0, {
            "species":null,
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

class Workstep {
    constructor(workstep, date = null, workstepIndex = 0, options = {}) {
        this.workstep = workstep;
        this.date = date;
        this.workstepIndex = workstepIndex;
        this.options = options;
    }
}



// Date Picker
var startDate = '01.01.2007';
var setStartDate = '01.02.2024';
var setEndDate = '01.08.2024';
var endDate = '26.11.2024';

const setLanguage =  (language_code)=>{
    $('.datepicker').datepicker({
        language: language_code,
        autoclose: true
    })
};

const observeDropdown = (selector, callback) => {
    const dropdown = document.querySelector(selector);
    if (!dropdown) 
        {
            console.error(`Dropdown not found: ${selector}`);
            return; // Exit if dropdown does not exist
        }
    if (dropdown.options.length > 0) {
        callback(dropdown);
        return; // Exit if options are already loaded
    }

    const observer = new MutationObserver((mutations, obs) => {
        mutations.forEach(mutation => {
            if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
                callback(dropdown);
                obs.disconnect(); // Stop observing after options are loaded
            }
        });
    });

    observer.observe(dropdown, { childList: true });
};



const runSimulation = (monicaProject) => {   
    console.log('runSimulation', monicaProject);
    fetch(runSimulationUrl, {
        method: 'POST',
        body: JSON.stringify(monicaProject),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('data', data.message.success);
        if (data.message.success) {
            console.log('SUCCESS', data.message)
            $('#runSimulationButton').prop('disabled', true);
            $('#runSimulationButton').text('...Simulation running');
            // Remove 'active' class from all nav links
            $('.nav-link.monica').removeClass('active');

            $('#resultTab').removeClass('disabled').addClass('active').trigger('click');
            
            
            var colors = [
                'rgba(255, 200, 0, 0.7)', 
                'rgba(0, 150, 200, 0.7)', 
                'rgba(0, 200, 255, 0.7)', 
                'rgba(0, 255, 200, 0.7)',
                'rgba(0, 255, 100, 0.7)']

            var resultOutput = {
               
                'Yield': false,
                'Irrig': true,
                'organ': false,
                'AbBiom': true,
                'Mois_1': true,
                'Mois_2': true,
                'Mois_3': true,
                'SOC_1': false,
                'SOC_2': false,
                'SOC_3': false,
                'LAI': false,

            }


            var dates = data.message.message[0].daily.Date;
            var datasets = [
            {
                type: 'bar',  // Specifies the type as bar for precipitation
                yAxisID: 'y1',  // Optional: Add a separate y-axis if needed
                label: 'Precipitation',
                data: data.message.message[0].daily.Precip,
                backgroundColor: 'rgba(0, 0, 255, 0.5)',  // Semi-transparent blue
                borderColor: 'rgba(0, 0, 255, 0.7)',
                borderWidth: 1,
            },
        ];
            for (let i = 0; i < data.message.message.length; i++) {
                console.log(i);
                var msg = data.message.message[i].daily
                
                if (resultOutput.Yield) {
                    datasets.push({
                        yAxisID: 'y2',
                        label: `Yield_${i}`,
                        data: msg.Yield,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                    });
                };
                if (resultOutput.AbBiom) {
                    datasets.push({
                        yAxisID: 'y2',
                        label: `Biomass_${i}`,
                        data: msg.AbBiom,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                    });
                };

                if (resultOutput.Irrig){
                    datasets.push({
                        type: 'bar',  // Specifies the type as bar for precipitation
                        yAxisID: 'y1',  // Optional: Add a separate y-axis if needed
                        label: `Irrigation_${i}`,
                        data: msg.Irrig,
                        backgroundColor: colors[i],  // Semi-transparent blue
                        borderColor: colors[i],
                        borderWidth: 1,
                        pointHitRadius: 10,
                    });
                };

                if (resultOutput.organ) {
                    datasets.push({
                        type: 'bar',  // Specifies the type as bar for precipitation
                        yAxisID: 'y1',  // Optional: Add a separate y-axis if needed
                        label: `Stage_${i}`,
                        data: msg.Stage,
                        backgroundColor: colors[i],  // Semi-transparent blue
                        borderColor: colors[i],
                        borderWidth: 1,
                        pointHitRadius: 10,
                    });
                };
                if (resultOutput.Mois_1) {
                    datasets.push({
                        yAxisID: 'y3',
                        label: `Moisture 0-10cm ${i}`,
                        data: msg.Mois_1,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                    });
                };
                if (resultOutput.Mois_2) {
                    datasets.push({
                        yAxisID: 'y3',
                        label: `Moisture 10-20cm ${i}`,
                        data: msg.Mois_1,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                    });
                };
                if (resultOutput.Mois_3) {
                    datasets.push({
                        yAxisID: 'y3',
                        label: `Moisture 20-30cm ${i}`,
                        data: msg.Mois_3,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                    });
                };
                if (resultOutput.SOC_1) {
                    datasets.push({
                        yAxisID: 'y4',
                        label: `SOC 0-10cm ${i}`,
                        data: msg.Mois_1,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                    });
                };
                if (resultOutput.SOC_2) {
                    datasets.push({
                        yAxisID: 'y4',
                        label: `SOC 10-20cm ${i}`,
                        data: msg.SOC_2,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                    });
                };
                if (resultOutput.SOC_3) {
                    datasets.push({
                        yAxisID: 'y4',
                        label: `SOC 20-30cm ${i}`,
                        data: msg.SOC_3,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                    });
                };
                if (resultOutput.LAI) {
                    datasets.push({
                        yAxisID: 'y5',
                        label: `LAI ${i}`,
                        data: msg.LAI,
                        borderWidth: 2,
                        borderColor: colors[i],
                        pointHitRadius: 10,
                        pointHoverRadius: 10,
                        pointHoverBackgroundColor: 'rgba(0, 0, 0, 0)',
                        pointHoverBorderColor: 'rgba(0, 0, 0, 0)',
                    });
                };

            };
            console.log("Datasets", datasets)


            
            // const dailyData = data.message.daily;
            // const dates = dailyData.Date;
            // chartDiv.innerHTML = '<canvas id="Chart" height="100"></canvas>'
            chartDiv.innerHTML = '<canvas id="Chart"></canvas>'
            const ctx = document.getElementById('Chart')
            const chart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: dates,
                    datasets: datasets,
                },
                options: {
                    elements: {
                        point: {
                        radius: 0,
                        },
                    },
                    responsive: true,
                    plugins: {
                        // title: {
                        //     display: true,
                        //     text: 'Custom Chart Title'
                        // },
                        legend: {
                            position: 'right'
                        }
                    }
                },
               
            });
            chart.update();
            

            $('#runSimulationButton').prop('disabled', false);
            $('#runSimulationButton').text('Run Simulation');

        } else {
            handleAlerts(data.message);
        }    
    })
    .then(() => {
        $('#resultTab').removeClass('disabled').addClass('active').trigger('click');
    });
};

const loadProjectToGui = (project) => {

    console.log('loadProject', project);
    let startDate = new Date(project.startDate);
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
    project.rotation.forEach(rotation => {
        addRotationToGui(rotation.rotationIndex, rotation);
    });
    
};

const addRotationToGui = (rotationIndex, rotation=null) => {
    // check if rotation already exists
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
        if(!rotation){
            addWorkstepToGui('sowingWorkstep', rotationIndex, 0, cardBody);
            addWorkstepToGui('harvestWorkstep', rotationIndex, 1, cardBody);
        } else {
            Object.entries(rotation).forEach(([workstepType, value]) => {
                if (workstepType !== 'rotationIndex' && workstepType !== 'workstepIndex') {
                    if (value.length > 0) {
                        value.forEach(workstep => {
                            addWorkstepToGui(workstepType, rotationIndex, workstep.workstepIndex, cardBody, workstep=workstep);
                            
                        });
                    }
                }
            });    
        }
    };

    if (rotation) {
        const rotationIndex = rotation.rotationIndex;
        Object.entries(rotation).forEach(([workstepType, value]) => {
            
            if (workstepType !== 'rotationIndex' && workstepType !== 'workstepIndex') {
                if (value.length > 0) {
                    value.forEach(workstep => { 
                        const form = document.querySelector(`form[rotation-index="${rotationIndex}"][workstep-index="${workstep.workstepIndex}"]`);
                        if (form) {
                            const datepickerInput = form.querySelector('.workstep-datepicker'); // Ensure correct selection
                            if (datepickerInput) {
                                $(datepickerInput).datepicker('update', new Date(workstep.date));
                            } else {
                                console.error("Datepicker input not found inside the form.");
                            }

                            if (workstepType === 'sowingWorkstep') {
                                console.log('workstepType', workstepType);
                                const speciesSelector = form.querySelector(`select[name="species"]`);
                                const cultivarSelector = form.querySelector(`select[name="cultivar"]`);
                                const residueSelector = form.querySelector(`select[name="residue"]`);
                                console.log('input', speciesSelector.id);
                                if (speciesSelector) {
                                    console.log('if input true');
                                        // Usage: Watch when the species dropdown gets its options
                                    observeDropdown(`#${speciesSelector.id}`, (dropdown) => {
                                        console.log('dropdown', dropdown);
                                        console.log('workstep.options.species', workstep.options.species);
                                        dropdown.value = workstep.options.species;  // Set value once options are ready
                                        
                                        fetch('/monica/get_options/cultivar-parameters/' + workstep.options.species + '/')
                                            .then(response => response.json())
                                            .then(data => {
                                                cultivarSelector.innerHTML = '';  // Clear current options
                                                data.options.forEach(option => {
                                                    const optionElement = document.createElement('option');
                                                    optionElement.value = option.id;
                                                    optionElement.text = option.name;
                                                    cultivarSelector.appendChild(optionElement);                     
                                                });  
                                                
                                            })
                                            .then(() => {
                                                cultivarSelector.value = workstep.options.cultivar;  // Set value once options are ready
                                            });
                

                
                                            fetch('/monica/get_options/crop-residue-parameters/' + workstep.options.species + '/')
                                                .then(response => response.json())
                                                .then(data => {
                                                    residueSelector.innerHTML = '';
                                                    data.options.forEach(option => {
                                                        const optionElement = document.createElement('option');
                                                        optionElement.value = option.id;
                                                        optionElement.text = option.name;
                                                        residueSelector.appendChild(optionElement);
                                                    });
                                                })
                                                .then(() => {
                                                    residueSelector.value = workstep.options.residue;  // Set value once options are ready
                                                });
                                        //     };
                                        
                                        // observeDropdown(`#${cultivarSelector.id}`, (dropdown) => {
                                        //     dropdown.value = workstep.options.cultivar;  // Set value once options are ready
                                        //     dropdown.dispatchEvent(new Event('change', { bubbles: true }));
                                        // });
                                        // observeDropdown(`#${residueSelector.id}`, (dropdown) => {
                                        //     dropdown.value = workstep.options.residue;  // Set value once options are ready
                                        //     dropdown.dispatchEvent(new Event('change', { bubbles: true }));
                                        // });

                                    });
                                    
                                } else {
                                    console.error("Input not found with name:", key);
                                }
                              

                            } else {    
                                for (const [key, value] of Object.entries(workstep.options)) {
                                    const input = form.querySelector(`select[name="species"], input[name="species"]`);

                                    if (input) {
                                        input.value = value;
                                    } else {
                                        console.error("Input not found with name:", key);
                                    }
                                };
                            }
                        } else {
                            console.error("Form not found with rotation-index:", rotationIndex, "and workstep-index:", workstep.workstepIndex);
                        };
                    }) ;
                };
            };
        });              
    };

};

         
        // newForm.querySelector('.workstep-datepicker').value = workstep.date;
        // if (Object.keys(workstep.options).length > 0) {
        //     console.log('565 workstep.options', workstep.options);
        //     for (const [key, value] of Object.entries(workstep.options)) {
        //         console.log('567 key, value in for loop', key, value);
        //         if (value !== null) {
        //             console.log('567 key, value in for loop', key, value);
        //             form.querySelector(`select[name='${key}']`).value = value;
        //         }
        //     }
        // }
        // for (const [key, value] of Object.entries(workstep.options)) {
        //     newForm.querySelector(`input[name='${key}']`).value = value;
        // }
    // }




const addWorkstepToGui = (workstepType, rotationIndex, workstepIndex, parentDiv, workstep=null) => {
    console.log("workstep: ", workstep);
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


    $(newForm).find('.datepicker').datepicker({
        language: 'de-DE',
        format: "dd.mm.yyyy",
        weekStart: 1,
        autoclose: true
    });

    // TODO test which one is better
    $(newForm).find('.workstep-datepicker').on('changeDate', function (e) {
        const project = MonicaProject.loadFromLocalStorage();
        const rotationIndex = e.target.closest('.rotation').getAttribute('rotation-index');
        const workstepIndex = e.target.getAttribute('workstep-index');
        const workstepType = e.target.getAttribute('workstep-type');
        // const dateValue = null;
        try{
            const dateValue = $(this).datepicker('getUTCDate').toISOString().split('T')[0];
            project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex).date = dateValue;
            project.saveToLocalStorage();
        } catch {
            ;
        }    
    });
    // TODO test which one is better
    $(newForm).find('.workstep-datepicker').on('focusout', function (e) {
        const project = MonicaProject.loadFromLocalStorage();
        const rotationIndex = e.target.closest('.rotation').getAttribute('rotation-index');
        const workstepIndex = e.target.getAttribute('workstep-index');
        const workstepType = e.target.getAttribute('workstep-type');
        // const dateValue = null;
        try{
            const dateValue = $(this).datepicker('getUTCDate').toISOString().split('T')[0];
            project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex).date = dateValue;
            project.saveToLocalStorage();
        } catch {
            ;
        }
    });


    const addWorkstepDiv = parentDiv.querySelector('.add-workstep');
    parentDiv.insertBefore(newForm, addWorkstepDiv);



    // if (workstep) {
    //     console.log("563 workstep: ", workstep);
    //     $(newForm).find('.workstep-datepicker').datepicker('update', new Date(workstep.date));
    //     // newForm.querySelector('.workstep-datepicker').value = workstep.date;
    //     if (workstep.options != {}) {
    //         console.log('565 workstep.options', workstep.options);
    //         for (const [key, value] of Object.entries(workstep.options)) {
    //             console.log('567 key, value in for loop', key, value);
    //             if (value !== null) {
    //                 console.log('567 key, value in for loop', key, value);
    //                 newForm.querySelector(`select[name='${key}']`).value = value;
    //             }
    //         }
    //     }
    //     // for (const [key, value] of Object.entries(workstep.options)) {
    //     //     newForm.querySelector(`input[name='${key}']`).value = value;
    //     // }
    // }

};



// Parameters Modal
const bindModalEventListeners = (parameters) => {
    console.log('bindModalEventListeners', parameters);
    try {
        const modalForm = document.getElementById('modalForm');
        console.log('modalForm', modalForm);
        modalForm.addEventListener('submit', (event) => {
            event.preventDefault();
        });
        
        document.getElementById('saveModalParameters').addEventListener('click', async () => {
            console.log("bindModalEventListeners saveModalParameters clicked");
            // change the selected Option's text in case the name was changed in the modal
            const modalData = new FormData(modalForm);
            // in case the name was changed in the modal, change the selected option's text
            const parameterName = modalForm.getAttribute('parameter-name');
            const selectedOption = $('.select.form-select.' + parameterName).find('option:selected');
            selectedOption.text(modalData.get('name'));
            const modalAction = 'save'

            const modalClose = await submitModalForm(modalForm, modalAction);
            console.log('modalClose', modalClose);
            if (modalClose) {
                
                $('#formModal').modal('hide');
            }
        });

        document.getElementById('saveAsNewModalParameters').addEventListener('click', () => {
            console.log("bindModalEventListeners saveAsNewModalParameters clicked");
            const modalForm = document.getElementById('modalForm');

            const modalAction = 'save_as_new'

            const modalClose = submitModalForm(modalForm, modalAction);
            console.log('modalClose', modalClose);
            if (modalClose) {
                $('#formModal').modal('hide');
            }
        });

        document.getElementById('deleteParameters').addEventListener('click', () => {
            console.log("bindModalEventListeners deleteParameters clicked");
            const modalForm = document.getElementById('modalForm');
            const modalAction = 'delete'
            const modalClose = submitModalForm(modalForm, modalAction);
            console.log('modalClose', modalClose);
            if (modalClose) {
                $('#formModal').modal('hide');
            }
        });
    } catch {
        console.log('no modal save buttons found');
    }
    if (parameters === 'user-simulation-settings') {
        // extra event listeners for the simulation settings modal
        try {   
            $('#id_use_automatic_irrigation').on('change', function (event) {
                $('#automatic_irrigation_params').toggle(event.target.checked);
            });

            $('#id_use_n_min_mineral_fertilising_method').on('change', function (event) {
                $('#n_min_fertilisation_params').toggle(event.target.checked);
            });
        } catch {
            // the modal is not a simulation settings modal
            ;
        };
    } 
};

const updateDropdown = (parameterType, rotationIndex, newId) => {
    console.log('updateDropdown', parameterType, rotationIndex, newId);
    // the absolute path is needed because most options are exclusively from /monica
    let baseUrl = '/monica/get_options/';
    // save project differs in monica and swn, therefore:
    if (parameterType === 'monica-project') {
        console.log('updateDropdown saveProject');
        baseUrl = 'get_options/';
    }
    console.log('updateDropdown baseUrl', baseUrl);

    fetch(baseUrl + parameterType + '/')
        .then(response => response.json())
        .then(data => {
            console.log('updateDropdown', data);
            var select = document.querySelector('.form-select.' + parameterType); 
            if (rotationIndex != '') {
                const rotationDiv = document.querySelector(`div[rotation-index='${rotationIndex}']`);
                select = rotationDiv.querySelector('.select-parameters.' + parameterType);
            } 
            select.innerHTML = '';
            data.options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.id;
                optionElement.text = option.name;
                select.appendChild(optionElement);
            });
            if (newId != '') {
                select.value = newId
            }
        })
        .catch(error => console.log('Error in updateDropdown', error));
};

const submitModalForm = (modalForm, modalAction) => {
    const actionUrl =  modalForm.getAttribute('data-action-url');
    const absoluteUrl = '/monica/' + actionUrl;
    const formData = new FormData(modalForm);
    formData.append('modal_action', modalAction);


    fetch(absoluteUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("check 2", data)
        if (data.message.success) {
            $('#formModal').modal('hide');
            //TODO: deal with it
            handleAlerts(data.message);
            const parameterType = actionUrl.split('/')[0];
            const rotationIndex = actionUrl.split('/')[2];
            if (modalAction === 'save_as_new') {
                var urlParts = actionUrl.split('/');
                console.log("updateDropdown saveAsNew", actionUrl.split('/')[0], data.new_id);

                updateDropdown(parameterType, rotationIndex, data.new_id);
            } else if (modalAction === 'delete') {
                console.log("updateDropdown deleteParams", actionUrl.split('/')[0], '');
                updateDropdown(parameterType, rotationIndex, '');
            }
            return true;
        } else {
            alert('Error saving form: ' + data.errors);
            return false;
        }
    })
    .catch(error => console.error('Error:', error));
};

// TODO refactor initiaizeSoilModal
// TODO implement getSoilProfiles for swn - all poygon ids
var initializeSoilModal = function (polygonIds, userFieldId, systemUnitJson, landusageChoices) {
    // console.log('userFieldId', userFieldId);
    const landUsageField = document.getElementById('id_land_usage');
    const soilProfileField = document.getElementById('id_soil_profile');
    const horizonsField = document.getElementById('div_id_horizons');
    const areaPercenteageField = document.getElementById('id_area_percentage');
    const systemUnitField = document.getElementById('id_system_unit');
    // const profileText = document.getElementById('id_profile');
    const table = document.getElementById('tableHorizons');

    var selectedSoilProfile = 0;

    soilProfileField.addEventListener('change', function() {
        
        const selectedLandUsage = landUsageField.value;
        const selectedSystemUnit = systemUnitField.value;
        const selectedAreaPercenteage = areaPercenteageField.value;
        selectedSoilProfile = soilProfileField.value;
        
        
        const horizons = systemUnitJson[selectedLandUsage][selectedSystemUnit]['soil_profiles'][selectedAreaPercenteage][selectedSoilProfile]['horizons'];
        horizonsField.innerHTML = '<p class="text-start">Landuse: ' + selectedLandUsage + '</br>System unit: ' + selectedSystemUnit + '</br>Area percentage: ' + selectedAreaPercenteage + '</br>Soil profile: ' + selectedSoilProfile + '</p>';
        table.innerHTML = '';
        const headerRow = table.insertRow();
        headerRow.classList.add("table-dark")
        const headerCell = headerRow.insertCell();
        
        headerCell.textContent = 'Horizonte';
        for (let horizon in horizons) {
            const headerCellHorizon = headerRow.insertCell();
            headerCellHorizon.textContent = horizon;
            
        }
        for (let key in horizons[1]) {
            const dataRow = table.insertRow();
            const dataRowHeaderCell  = dataRow.insertCell();
            dataRowHeaderCell.classList.add("table-dark")
            for (let horizon in horizons) {
                dataRowHeaderCell.textContent = key;
                const dataRowDataCell  = dataRow.insertCell();
                let value = horizons[horizon][key];
                if (typeof(value) === 'number') {
                    
                    value = value.toFixed(2);
                }
                dataRowDataCell.textContent = value;   
            } 
        }
    });

    // Populate soil profile and area percenteage when land usage changes
    areaPercenteageField.addEventListener('change', function() {
        console.log('areaPercenteageField change event')
        const selectedLandUsage = landUsageField.value;
        const selectedSystemUnit = systemUnitField.value;
        const selectedAreaPercenteage = areaPercenteageField.value;

        const selectableSoilProfiles =  systemUnitJson[selectedLandUsage][selectedSystemUnit]['soil_profiles'][selectedAreaPercenteage];
        console.log('selectableSoilProfiles', selectableSoilProfiles);

        const profileOptions = new Object();
        let profileNo = 1;
        for (let soilprofile_id in selectableSoilProfiles) {
            
            profileOptions[soilprofile_id] = 'Profil ' + profileNo;
            profileNo++;
        };
        console.log('profileOptions', profileOptions);
        soilProfileField.innerHTML = '';
        for (const key in profileOptions) {
            const option = document.createElement('option');
            option.value = key;
            option.text = profileOptions[key];
            soilProfileField.appendChild(option);
        };
        soilProfileField.dispatchEvent(new Event('change'));
    
    });

    systemUnitField.addEventListener('change', function() {
        console.log('systemUnitField change event');
        const selectedLandUsage = landUsageField.value;
        const selectedSystemUnit = systemUnitField.value;
        console.log('selectedSystemUnit', selectedSystemUnit);
        console.log('selectedLandUsage', selectedLandUsage);
        const selectableAreaPercentages =  systemUnitJson[selectedLandUsage][selectedSystemUnit]['area_percentages'].reverse();
        console.log('selectableAreaPercentages', selectableAreaPercentages);
        areaPercenteageField.innerHTML = '';
        selectableAreaPercentages.forEach(item => {
            areaPercenteageField.appendChild(new Option(item));
        });
        areaPercenteageField.dispatchEvent(new Event('change'));
    });

    landUsageField.addEventListener('change', function(){
        console.log('landUsageField change event')
        const selectedLandUsage = landUsageField.value;
        
        const selectableSystemUnits =  new Array()
        for (let [key, value] of Object.entries(systemUnitJson[selectedLandUsage])){
            if (!selectableSystemUnits.includes(key)){
                selectableSystemUnits.push(key);
            }}
            selectableSystemUnits.sort();
        systemUnitField.innerHTML = '';
        selectableSystemUnits.forEach(item => {
            systemUnitField.appendChild(new Option(item));
        });
        // trigger change event to update system unit
        systemUnitField.dispatchEvent(new Event('change'));
        console.log('selectableSystemUnits', selectableSystemUnits.sort());
    });

    for (const key in landusageChoices) {
        const option = document.createElement('option');
        option.value = key;
        option.text = landusageChoices[key];
        landUsageField.appendChild(option);
    }
    
    landUsageField.dispatchEvent(new Event('change'));

    const btnSelectSoilProfile = document.getElementById("btnSelectSoilProfile");
    btnSelectSoilProfile.addEventListener("click", function () {      
        const project = MonicaProject.loadFromLocalStorage();
        
        project.soilProfileId = soilProfileField.value;
        console.log('project.soilProfileId', project.soilProfileId);
        project.saveToLocalStorage();
    });

};


const fetchModalContent = (params) => {
    try {

        let url = '/monica/' + params.parameters + '/';
        if (params.parameters_id) {
            url += params.parameters_id + '/';
        }
        if (params.rotation_index) {
            url += params.rotation_index + '/';
        }
        if (params.lon) {
            url += params.lat + '/' + params.lon + '/';
        }

        // Fetch the content
   

        if (params.parameters === 'select-soil-profile') {
            fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('fetchModalContent', data);
                const modal = $('#modalManualSoilSelection');
                const polygonIds = data.polygon_ids;
                const systemUnitJson = JSON.parse(data.system_unit_json);
                const landUsageChoices = JSON.parse(data.landusage_choices);
                initializeSoilModal(polygonIds, null, systemUnitJson, landUsageChoices);
                $('#modalManualSoilSelection').modal('show');
 
            })
        } else {
            fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok', response.text());
                }
                return response.text();
            })
            .then(data => {
                document.getElementById('modalModifyParamsContent').innerHTML = data;
                bindModalEventListeners(params.parameters);
            })
            .catch(error => console.error('Error:', error));
        }   
    } catch (error) {
        console.error('Error:', error);
    }

};


const validateProject = (project) => {
    var valid = true;
    console.log("VALIDATION", project)
    // if (project.name === null) {
    //     valid = false;
    //     handleAlerts('warning', 'Please provide a project name');
    // } else 
    if (project.longitude === null || project.latitude === null) {
        valid = false;
        handleAlerts({'success': false, 'message': 'Please provide a valid location'});
    } else if (project.startDate === null || project.endDate === null) {
        valid = false;
        handleAlerts({'success': false, 'message': 'Please provide a valid date range'});
    } else if (project.rotation.length === 0) {
        valid = false;
        handleAlerts({'success': false, 'message': 'Please provide a crop rotation'});
    } else if (project.rotation.some(rotation => rotation.sowingWorkstep.some(sowingWorkstep => sowingWorkstep.date == null))) {
        valid = false;
        handleAlerts({'success': false, 'message': 'Please provide a sowing date for each crop'});
    } else if (project.rotation.some(rotation => rotation.sowingWorkstep.some(sowingWorkstep => new Date(sowingWorkstep.date) < new Date(project.startDate) || new Date(sowingWorkstep.date) > new Date(project.endDate)))) {
        valid = false;
        handleAlerts({'success': false, 'message': 'Please provide a sowing date for each crop that is within your selected timeframe'});
    } else if (project.rotation.some(rotation => rotation.sowingWorkstep.some(sowingWorkstep => sowingWorkstep.options.species == null))) {
        valid = false;
        handleAlerts({'success': false, 'message': 'Please provide a crop for each sowing workstep!'});
    }
    return valid;
};
// var project = new MonicaProject();
// Event listeners
var language = 'de-DE'
document.addEventListener('DOMContentLoaded', () => {
    
    // if (window.location.href.split('/').includes('monica')) {
    //     project.swnForecast = false;
    // } else {
    //     project.swnForecast = true;
    // };

    setLanguage(language);
    $('#monicaStartDatePicker').datepicker({
        startDate: startDate,
        endDate: endDate,
    });

//     $('.datepicker').datepicker({
//         format: {
//             /*
//              * Say our UI should display a week ahead,
//              * but textbox should store the actual date.
//              * This is useful if we need UI to select local dates,
//              * but store in UTC
//              */
//             toDisplay: function (date, format, language) {
//                 var d = new Date(date);
//                 d.setDate(d.getDate());
//                 return d.toISOString();
//             },
//             toValue: function (date, format, language) {
//                 if (language === 'de-DE') {
//                     date = date.split('.');
//                     date = date[2] + '-' + date[1] + '-' + date[0];
//                     return date
                
//                     }
//             }
//         }
// });
    
    $('#monicaStartDatePicker').datepicker('update', setStartDate);
    $('#monicaEndDatePicker').datepicker('update', setEndDate);
    $('#todaysDatePicker').datepicker('update', new Date('2024-05-15'));
    $('#todaysDatePicker').trigger('focusout');


    const calculateDaysInRotation = function() {
        var startDate = project.startDate;
        var endDate = project.endDate;  
        // var startDate = $('#monicaStartDatePicker').datepicker('getDate');
        // var endDate = $('#monicaEndDatePicker').datepicker('getDate');
        var daysInRotation = (endDate - startDate) / (1000 * 60 * 60 * 24);
        var yearsInRotation = Math.ceil(daysInRotation / 365);
        return [daysInRotation, yearsInRotation];
    };



    // NAVBAR MONICA EVENT LISTENERS
    $('.nav-link.monica').on('click', function (e) {
        e.preventDefault();
        $('.nav-link.monica').removeClass('active');
        $(this).addClass('active');
        const target = $(this).attr('href');
        $('.tab-content').hide();
        $(target).show();
    });

    //TODO: remove this!!!
    $('#todaysDatePicker').on('changeDate', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.todaysDate = $(this).datepicker('getUTCDate');
        project.saveToLocalStorage();
        
    });

    $('#todaysDatePicker').on('focusout', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.todaysDate = $(this).datepicker('getUTCDate');
        project.saveToLocalStorage();
        
    });


    var advancedMode = false;
    $('.advanced').hide();
    $('#toggle-advanced-mode').on('click', function () {
        console.log()
        // Toggle the advancedMode variable
        advancedMode = !advancedMode;
    
        // Show or hide elements based on advancedMode
        if (advancedMode) {
            $('.advanced').show(); 
            $(this).text('Switch to Simple Mode'); 
        } else {
            $('.advanced').hide(); 
            $(this).text('Switch to Advanced Mode'); 
        } 
        console.log('Advanced mode:', advancedMode); // Log the current mode
    });




    // TAB GENERAL EVENT LISTENERS
    $('#id_longitude').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        console.log("EvenLister id_longitude change", project)
        project.longitude = $(this).val();
        project.saveToLocalStorage();
    });

    $('#id_latitude').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        console.log("EvenLister id_latitude change", project)
        project.latitude = $(this).val();
        project.saveToLocalStorage();    
    });


    $('#id_longitude').on('focusout', function () {
        const project = MonicaProject.loadFromLocalStorage();
        console.log("EvenLister id_longitude change", project)
        project.longitude = $(this).val();
        project.saveToLocalStorage();
    });

    $('#id_latitude').on('focusout', function () {
        const project = MonicaProject.loadFromLocalStorage();
        console.log("EvenLister id_latitude change", project)
        project.latitude = $(this).val();
        project.saveToLocalStorage();    
    });

    $('#monicaStartDatePicker').on('changeDate', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.startDate = $(this).datepicker('getUTCDate');
        project.saveToLocalStorage();      
    });

    $('#monicaEndDatePicker').on('changeDate', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.endDate = $(this).datepicker('getUTCDate');
        project.saveToLocalStorage();       
    });

    $('#monicaStartDatePicker').on('focusout', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.startDate = $(this).datepicker('getUTCDate');
        project.saveToLocalStorage();      
    });

    $('#monicaEndDatePicker').on('focusout', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.endDate = $(this).datepicker('getUTCDate');
        project.saveToLocalStorage();       
    });

    // TAB CROP ROTATION EVENT LISTENERS
    $('#addRotationButton').on('click', () => {
        const project = MonicaProject.loadFromLocalStorage();
        project.addRotation();        
        addRotationToGui(project.rotation.length - 1);
        project.saveToLocalStorage();
    });

    $('#removeRotationButton').on('click', () => {
        if (project.rotation.length > 1) {
            project.rotation.pop();
            $('#cropRotation').children().last().remove();
        } else {
            handleAlerts({'success': false, 'message': 'You cannot have less than 1 rotation'});
        }
    });


    // TAB CROP ROTATION EVENT LISTENERS
    $('#cropRotation').on('click', (event) => {
        const rotationIndex = event.target.closest('.rotation').getAttribute('rotation-index');
        const project = MonicaProject.loadFromLocalStorage();
        console.log("EvenLister cropRotation click", project)
        if (event.target.classList.contains('add-workstep-button')) {
            
            const workstepType = event.target.closest('.rotation').querySelector('.workstep-type-select').value;
            project.addWorkstep(workstepType, rotationIndex);
            addWorkstepToGui(workstepType, rotationIndex, project.rotation[rotationIndex].workstepIndex, event.target.closest('.rotation').querySelector('.card-body'));
            
            // project.saveToLocalStorage();
        } else if (event.target.classList.contains('delete-rotation-button')) {
            
            console.log('IMPLEMENT delete rotation');
            project.saveToLocalStorage();
        } else if (event.target.classList.contains('delete-workstep-button')) {
            
            const workstepIndex = event.target.closest('form').getAttribute('workstep-index');
            const workstepType = event.target.closest('form').getAttribute('workstep-type');
            console.log('delete-workstep', rotationIndex, workstepIndex, workstepType);
            project.rotation[rotationIndex][workstepType] = project.rotation[rotationIndex][workstepType].filter(workstep => workstep.workstepIndex != workstepIndex);
            event.target.closest('.card').remove();
            project.saveToLocalStorage();

        } else if (event.target.classList.contains('modify-parameters')) {
            console.log('modify-parameters clicked');
            const targetClass = event.target.classList[3];
            const value = event.target.closest('.rotation').querySelector('.select-parameters.' + targetClass).value;
            const params = {
                'parameters': targetClass,
                'parameters_id': value,
                'rotation_index': rotationIndex
            }
            // const endpoint = '/monica/' + targetClass + '/' + value + '/' + rotationIndex + '/';
            if (value != '') {
                fetchModalContent(params);
                $('#formModal').modal('show');

            } else {
                // should be impossible to reach this
                event.preventDefault();
                handleAlerts({'success': false, 'message': 'Please select a parameter to modify'});
            }
        }
        
    });

    $('#cropRotation').on('change', (event) => {
        console.log("EvenLister cropRotation change")
        const rotationIndex = event.target.closest('.rotation').getAttribute('rotation-index');
        const project = MonicaProject.loadFromLocalStorage();

        if (event.target.classList.contains('select-parameters')) {
            const workstepIndex = event.target.getAttribute('workstep-index');
            const workstepType = event.target.getAttribute('workstep-type');
            console.log('select-parameters', rotationIndex, workstepIndex, workstepType);
            var workstep = project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex);
        
            const cultivarSelector = event.target.closest('.rotation').querySelector('.select-parameters.cultivar-parameters');
            const residueSelector = event.target.closest('.rotation').querySelector('.select-parameters.crop-residue-parameters');
                
            
            if (event.target.classList.contains('species-parameters')) {
                console.log('if species-parameters', workstep)
                workstep.options.species = event.target.value;
                if (event.target.value != '') {
                    fetch('/monica/get_options/cultivar-parameters/' + event.target.value + '/')
                    .then(response => response.json())
                    .then(data => {
                        cultivarSelector.innerHTML = '';  // Clear current options
                        data.options.forEach(option => {
                            const optionElement = document.createElement('option');
                            optionElement.value = option.id;
                            optionElement.text = option.name;
                            cultivarSelector.appendChild(optionElement);                     
                        });  
                        console.log('cultivarSelector', cultivarSelector.value)
                        console.log('workstep.options.cultivar', workstep.options.cultivar)
                        workstep.options['cultivar'] = cultivarSelector.value        
                        project.saveToLocalStorage();
                    });
                

                
                    fetch('/monica/get_options/crop-residue-parameters/' + event.target.value + '/')
                        .then(response => response.json())
                        .then(data => {
                            residueSelector.innerHTML = '';
                            data.options.forEach(option => {
                                const optionElement = document.createElement('option');
                                optionElement.value = option.id;
                                optionElement.text = option.name;
                                residueSelector.appendChild(optionElement);
                            });
                            workstep.options['residue'] = residueSelector.value;
                            project.saveToLocalStorage();
                        });
                    };
                
            } else if (event.target.classList.contains('cultivar-parameters')) {
                console.log('if cultivar-parameters', workstep)
                workstep.options.cultivar = event.target.value;
                project.saveToLocalStorage();
            } else if (event.target.classList.contains('crop-residue-parameters')) {
                workstep.options.residue = event.target.value;
                project.saveToLocalStorage();
            } else if (event.target.classList.contains('organic-fertiliser-parameters')) {
                workstep.options.organicFertiliser = event.target.value;
                project.saveToLocalStorage();
           
            } else if (event.target.classList.contains('mineral-fertiliser-parameters')) {
                workstep.options.mineralFertiliser = event.target.value;
                project.saveToLocalStorage();
            } else if (event.target.classList.contains('organic-fertiliser-amount')) {
                workstep.options.amount = event.target.value;
                project.saveToLocalStorage();
            } else if (event.target.classList.contains('mineral-fertiliser-amount')) {
                workstep.options.amount = event.target.value;
                project.saveToLocalStorage();
            } else if (event.target.classList.contains('irrigation-amount')) {
                workstep.options.amount = event.target.value; 
                project.saveToLocalStorage();
            } else {
                ;
            }
            
            
        }
        
            
    });


    

    


    //TAB SOIL EVENT LISTENERS
    $('#id_soil_moisture').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.userSoilMoistureParametersId = $(this).val();
        project.saveToLocalStorage();
    });
    $('#id_soil_organic').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.userSoilOrganicParametersId = $(this).val();
        project.saveToLocalStorage();
    });
    $('#id_soil_temperature').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.userSoilTemperatureParametersId = $(this).val();
        project.saveToLocalStorage();
    });
    $('#id_soil_transport').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.userSoilTransportParametersId = $(this).val();
        project.saveToLocalStorage();
    });

    $('#tabSoil').on('click', (event) => {
        if (event.target.classList.contains('modify-parameters')) {
            const targetClass = event.target.classList[3];
            const value = $('.form-select.' + targetClass).val();
            
            const params = {
                'parameters': targetClass,
                'parameters_id': value,
            }
            fetchModalContent(params);
        } else if (event.target.classList.contains('show-soil-parameters')) {
            const params = {
                'parameters': 'soil-profile',
                'lon': project.longitude,
                'lat': project.latitude
            }
            
            fetchModalContent(params);
        } else if (event.target.classList.contains('manually-select-soil-parameters')) {
            const params = {
                'parameters': 'select-soil-profile',
                'lon': project.longitude,
                'lat': project.latitude
            }
            
            fetchModalContent(params);
        }
    });

    // TAB PROJECT EVENT LISTENERS
    const loadProjectFromDB = (project_id) => {
        console.log('loadProjectFromDB', project_id);
        fetch('load-project/' + project_id + '/')
            .then(response => response.json())
            .then(data => {
                console.log('loadProjectFromDB', data);
                if (data.message.success) {
                    handleAlerts(data.message)
                    const project = new MonicaProject(data.project);
                    loadProjectToGui(data.project)
                    project.saveToLocalStorage();
                };
                handleAlerts(data.message)

            })
            .catch(error => console.error('Error:', error));
    };



    $('#tabProject').on('click', (event) => {
        if (event.target.classList.contains('modify-parameters')) {
            const targetClass = event.target.classList[3];
            const value = $('.form-select.' + targetClass).val();
            
                const params = {
                    'parameters': targetClass,
                    'parameters_id': value,
                }
                fetchModalContent(params);          
        } else if (event.target.classList.contains('monica-project')) {
            const projectId = $('#id_monica_project').val(); 
            const selecteprojectName = $('#id_monica_project option:selected').text()
            if (event.target.classList.contains('load-project')) {
                console.log('LOAD PROJECT')
                loadProjectFromDB(projectId);
            }else if (event.target.classList.contains('new-project')) {
                console.log('NEW PROJECT')
                projectModalForm.reset();
                $('#monicaProjectModal').modal('show');
            } else if (event.target.classList.contains('delete-project')) {
                console.log('delete project')
                
                const modal = new bootstrap.Modal(document.getElementById('deleteProjectModal'), {});
                $('#deleteProjectModal').find('.modal-title').text('Delete project ' + selecteprojectName + '?');
                $('#delete_project_id').val(projectId);
                modal.show();
            }
        }
    });


    $('#btnConfirmDeleteProject').on('click', () => {
        const projectId = $('#delete_project_id').val();
        console.log('Delete confirmed')
        fetch('/monica/delete-project/' + projectId + '/',
                {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
                    }
                }
            )
            .then(response => response.json())
            .then(data => {
                console.log('deleteProject', data);
                if (data.message.success) {
                    handleAlerts(data.message);
                    updateDropdown('monica-project', '', '');
                } else {
                    handleAlerts(data.message);
                }
            })
            .catch(error => console.error('Error:', error));

            $('#deleteProjectModal').modal('hide');
    });
    const projectModalForm = document.getElementById('projectModalForm');
    // project modal save project
    $('#saveProjectButton').on('click', () => {
        console.log('saveProjectButton clicked');
        // const formData = new FormData(projectModalForm);
        // TODO test if this is obsolete ----
        // in case it is a SWN project, longitude and latidude are provided from user field centroid
        const project = new MonicaProject();
        try {
            const longitude = $('#id_longitude').val();
            const latitude = $('#id_latitude').val();
            
            project.longitude = longitude;
            project.latitude = latitude;
        }
        catch {
            ;
        }

        try {
            const userField = $('#userFieldSelect').val();
            project.userField = userField;
        }
        catch {
            ;
        }

        project.name = $('#id_project_name').val();
        project.description = $('#id_project_description').val();
        project.startDate = $('#id_project_start_date').datepicker('getUTCDate');
        project.modelSetup = $('#id_project_model_setup').val();

        project.saveToLocalStorage();
        // obsolete ??? --------

        // this works for monica and swn
        var saveUrl = 'save-project/';
        fetch(saveUrl, {
            method: 'POST',
            body: JSON.stringify(project),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('data', data);
            if (data.message.success) {
                project.id = data.project_id;
                $('#project-info').find('.card-title').text('Project '+ data.project_name);
                updateDropdown('monica-project','', data.project_id)
                handleAlerts(data.message);
                
                projectModalForm.reset();
                
                $('#monicaProjectModal').modal('hide');
                project.saveToLocalStorage();
            } else {
                handleAlerts(data.message);
            }
            
        })
    });

    $('#projectName').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.name = $(this).val();
        project.saveToLocalStorage();
    });
    $('#projectDescription').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.description = $(this).val();
        project.saveToLocalStorage();
    });
    $('#id_user_environment').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.userEnvironmentParametersId = $(this).val();
        project.saveToLocalStorage();
    });
    $('#id_user_crop_parameters').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.userCropParametersId = $(this).val();
        project.saveToLocalStorage();
    });
    $('#id_user_simulation_settings').on('change', function () {
        const project = MonicaProject.loadFromLocalStorage();
        project.userSimulationSettingsId = $(this).val();
        project.saveToLocalStorage();
    });




    $('.dropdown-item').on('click', function (e) {
        e.preventDefault();
        $('.dropdown-item').removeClass('active');
        $(this).addClass('active');
        const target = $(this).attr('href');
        $('.tab-content').hide();
        $(target).show();
    });

    $('.tab-content').hide();

    const tabs = document.querySelectorAll('.monica.nav-link');

    $('#nextButton').on('click', () => {
        const activeTab = document.querySelector('.nav-link.active');
        const activeIndex = Array.from(tabs).indexOf(activeTab);
        const nextIndex = (activeIndex + 1) % tabs.length;
        tabs[nextIndex].click();
    });

    $('#previousButton').on('click', () => {
        const activeTab = document.querySelector('.nav-link.active');
        const activeIndex = Array.from(tabs).indexOf(activeTab);
        const previousIndex = ((activeIndex + tabs.length) - 1) % tabs.length;
        tabs[previousIndex].click();
    });

    $('#runSimulationButton').on('click', () => {
        const project = MonicaProject.loadFromLocalStorage();
        console.log('runSimulationButton clicked');
        try {
            project.longitude = $('#id_longitude').val();
            project.latitude = $('#id_latitude').val();
        } catch { 
            try { 
                // project.userField = $('#userFieldSelect').val();
                console.log("No userField selected!")
            } catch {;}
   
        }


        if (validateProject(project)) {
            runSimulation(project);
        }
        
    });

    tabs[1].click();
    
    let project = new MonicaProject()
    project.saveToLocalStorage();
    
    loadProjectToGui(project);
});

