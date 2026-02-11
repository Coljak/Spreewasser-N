
import {MonicaCalculation, MonicaProject, Rotation, Workstep } from '/static/monica/monica_model.js';
import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, populateDropdown } from '/static/shared/utils.js';


//TODO fix select dropdown for project. It does not load
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

export function loadProjectToGui(project) {
    // console.log('loadProjectToGui', project);
    console.log("Project is loading..", project)
    window.isLoading = true;
    document.querySelector('#cropRotation').innerHTML = '';
    if (window.location.pathname.endsWith('/drought/')) {
        console.log('in drought selected project of uf', project.userField);
        const listEl = document.querySelector(`li[user-field-id="${project.userField}"]`);
        if (listEl) {
            listEl.dispatchEvent(new MouseEvent("click", { bubbles: true }));
        } else {
            console.warn(`No list element found for user-field-id=${project.userField}`);
        }
    };
    
    
    project.name ? $('#monica-project-name').text(project.name) : $('#monica-project-name').text('Kein Projekt geladen');
    $('#projectDescription').val(project.description);
    $('#id_longitude').val(project.longitude);
    $('#id_latitude').val(project.latitude);
    $('#userFieldSelect').val(project.userField);
    
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

export function addRotationToGui(rotationIndex, rotation=null) {

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

export function addWorkstepToGui(workstepType, rotationIndex, workstepIndex, workstep=null) {
    console.log("addWorkstepToGui", workstepType, rotationIndex, workstepIndex, workstep);
    // load and modify the according workstep template
    const formTemplate = document.getElementById(workstepType + '-template');
    const newForm = formTemplate.cloneNode(true);
    newForm.removeAttribute('id');

    newForm.querySelectorAll('*[id]').forEach(element => {
       
        const newId = `${element.id}_${workstepType}_${rotationIndex}_${workstepIndex}`;
        // newForm.querySelector(`label[for="${element.id}"]`).htmlFor = newId;
        element.id = newId;
        element.setAttribute('workstep-index', workstepIndex);
        element.setAttribute('workstep-type', workstepType);
        
    });

    newForm.querySelectorAll('label').forEach(label => {
        const forId = label.getAttribute('for');
        if (forId) {
            const newId = `${forId}_${workstepType}_${rotationIndex}_${workstepIndex}`;
            label.setAttribute('for', newId);
        }
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

    // $(newForm).find('input').each(function() {
    //     $(this).trigger('change');
    // });

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

const resultTranslation = {
    'AbBiom': 'Biomasse gesamt',
    'Yield': 'Ertrag',
    'Irrig': 'Bewässerung',
    'Date': 'Datum',
    'Precip': 'Niederschlag',
    'LAI': 'LAI',
    'PASW_AVG': 'Pflanzenverfügbares Wasser 0-10cm',
    // 'PASW_2': 'Pflanzenverfügbares Wasser 10-20cm',
    // 'PASW_3': 'Pflanzenverfügbares Wasser 20-30cm',
    // 'PASW_4': 'Pflanzenverfügbares Wasser 30-40cm',
    // 'PASW_5': 'Pflanzenverfügbares Wasser 40-50cm',
    'Mois_1': 'Bodenfeuchte 0-10cm',
    'Mois_2': 'Bodenfeuchte 10-20cm',
    'Mois_3': 'Bodenfeuchte 20-30cm',
    'SOC_1': 'organischer Kohlenstoff 0-10cm',
    'SOC_2': 'organischer Kohlenstoff 10-20cm',
    'SOC_3': 'organischer Kohlenstoff 20-30cm',
};

export function createChartDataset() {

    let outputSettings = JSON.parse(localStorage.getItem('outputSettings'));
    console.log('outputSettings', outputSettings);
    let colors = outputSettings.colors;
    let resultOutput = outputSettings.resultOutput;

    let listOfResults = JSON.parse(localStorage.getItem('monicaResults'));
    let dates = listOfResults[0].daily.Date;
    let datasets = [];
    if (resultOutput.Precip) {
        datasets.push({
            type: 'bar',  // Specifies the type as bar for precipitation
            yAxisID: 'y1',  // Optional: Add a separate y-axis if needed
            label: resultTranslation.Precip,
            data: listOfResults[0].daily.Precip,
            backgroundColor: 'rgba(0, 0, 255, 0.8)',  // Semi-transparent blue
            borderColor: 'rgba(0, 0, 255, 0.7)',
            borderWidth: 1,
        })
    }

    let minMaxDatasets = {};
    const parameters = [
        'Yield', 'AbBiom', 'Irrig', 'organ', 
        'PASW_AVG', 'Mois_1', 'Mois_2', 'Mois_3', 
        'SOC_1', 'SOC_2', 'SOC_3', 'LAI'
    ];
    parameters.forEach(p => {
        minMaxDatasets[p] = { min: Infinity, max: -Infinity };
    });
    listOfResults.forEach(result => {
        const daily = result.daily;

        parameters.forEach(p => {
            if (daily[p]) {
                const values = Object.values(daily[p]).filter(v => !isNaN(v));
                if (values.length) {
                    const minVal = Math.min(...values);
                    const maxVal = Math.max(...values);

                    // Update global min/max
                    minMaxDatasets[p].min = Math.min(minMaxDatasets[p].min, minVal);
                    minMaxDatasets[p].max = Math.max(minMaxDatasets[p].max, maxVal);
                }
            }
        });
    });
    minMaxDatasets['Mois'] = {'min': Infinity, 'max': -Infinity};
    minMaxDatasets['SOC'] = {'min': Infinity, 'max': -Infinity};
    minMaxDatasets['Irrig'] = {'min': Infinity, 'max': -Infinity};
    minMaxDatasets['Mois']['min'] = Math.min(minMaxDatasets['Mois_1'].min, minMaxDatasets['Mois_2'].min, minMaxDatasets['Mois_3'].min);
    minMaxDatasets['Mois']['max'] = Math.max(minMaxDatasets['Mois_1'].max, minMaxDatasets['Mois_2'].max, minMaxDatasets['Mois_3'].max);
    minMaxDatasets['SOC']['min'] = Math.min(minMaxDatasets['SOC_1'].min, minMaxDatasets['SOC_2'].min, minMaxDatasets['SOC_3'].min);
    minMaxDatasets['SOC']['max'] = Math.max(minMaxDatasets['SOC_1'].max, minMaxDatasets['SOC_2'].max, minMaxDatasets['SOC_3'].max);
    minMaxDatasets['Irrig']['min'] = Math.min(Math.min(...listOfResults[0].daily.Precip), minMaxDatasets['Irrig']['min']);
    minMaxDatasets['Irrig']['max'] = Math.max(Math.max(...listOfResults[0].daily.Precip), minMaxDatasets['Irrig']['max']);
    console.log('minMaxDatasets', minMaxDatasets);

    for (let i = 0; i < listOfResults.length; i++) {
        console.log(i);
        var msg = listOfResults[i].daily
        
        if (resultOutput.Yield) {
            datasets.push({
                yAxisID: 'y2',
                label: `${i} ${resultTranslation.Yield}`,
                data: msg.Yield,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.AbBiom) {
            datasets.push({
                yAxisID: 'y5',
                label: `${i} ${resultTranslation.AbBiom}`,
                data: msg.AbBiom,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };

        if (resultOutput.Irrig){
            datasets.push({
                type: 'bar',  
                yAxisID: 'y1',  
                label: ` ${i} ${resultTranslation.Irrig}`,
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
                label: ` ${i} ${resultTranslation.organ}`,
                data: msg.Stage,
                backgroundColor: colors[i],  // Semi-transparent blue
                borderColor: colors[i],
                borderWidth: 1,
                pointHitRadius: 10,
            });
        };
        if (resultOutput.PASW_AVG) {
            datasets.push({
                yAxisID: 'y4',
                label: ` ${i} ${resultTranslation.PASW_AVG}`,
                data: msg.PASW_AVG,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        // if (resultOutput.PASW_2) {
        //     datasets.push({
        //         yAxisID: 'y4',
        //         label: ` ${i} ${resultTranslation.PASW_2}`,
        //         data: msg.PASW_2,
        //         borderWidth: 2,
        //         borderColor: colors[i],
        //         pointHitRadius: 10,
        //     });
        // };
        // if (resultOutput.PASW_3) {
        //     datasets.push({
        //         yAxisID: 'y4',
        //         label: ` ${i} ${resultTranslation.PASW_3}`,
        //         data: msg.PASW_3,
        //         borderWidth: 2,
        //         borderColor: colors[i],
        //         pointHitRadius: 10,
        //     });
        // };
        // if (resultOutput.PASW_4) {
        //     datasets.push({
        //         yAxisID: 'y4',
        //         label: ` ${i} ${resultTranslation.PASW_4}`,
        //         data: msg.PASW_4,
        //         borderWidth: 2,
        //         borderColor: colors[i],
        //         pointHitRadius: 10,
        //     });
        // };
        // if (resultOutput.PASW_5) {
        //     datasets.push({
        //         yAxisID: 'y4',
        //         label: `${i} ${resultTranslation.PASW_5}`,
        //         data: msg.PASW_5,
        //         borderWidth: 2,
        //         borderColor: colors[i],
        //         pointHitRadius: 10,
        //     });
        // };
        if (resultOutput.Mois_1) {
            datasets.push({
                yAxisID: 'y3',
                label: `${i} ${resultTranslation.Mois_1}`,
                data: msg.Mois_1,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.Mois_2) {
            datasets.push({
                yAxisID: 'y3',
                label: `${i} ${resultTranslation.Mois_2}`,
                data: msg.Mois_2,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.Mois_3) {
            datasets.push({
                yAxisID: 'y3',
                label: `${i} ${resultTranslation.Mois_3}`,
                data: msg.Mois_3,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.SOC_1) {
            datasets.push({
                yAxisID: 'y4',
                label: `${i} ${resultTranslation.SOC_1}`,
                data: msg.SOC_1,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.SOC_2) {
            datasets.push({
                yAxisID: 'y4',
                label: `${i} ${resultTranslation.SOC_2}`,
                data: msg.SOC_2,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.SOC_3) {
            datasets.push({
                yAxisID: 'y4',
                label: `${i} ${resultTranslation.SOC_3}`,
                data: msg.SOC_3,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.LAI) {
            datasets.push({
                yAxisID: 'y5',
                label: `${i} ${resultTranslation.LAI}`,
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

    chartDiv.innerHTML = '<canvas id="Chart"></canvas>'
    const ctx = document.getElementById('Chart')
    const chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: dates,
            datasets: datasets,
        },
        options: {
            scales: {
                y1: {
                    type: 'linear',
                    position: 'right',
                    title: 'Precipitation / Irrigation (mm)',
                    beginAtZero: true,
                    min: 0,
                    max: minMaxDatasets['Irrig'].max * 1.1,
                },
                y2: {
                    type: 'linear',
                    position: 'left',
                    title: 'Ertrag (t/ha)',
                    beginAtZero: true,
                    min: 0,
                    max: Math.ceil(minMaxDatasets['Yield'].max * 1.3),
                },
                y3: {
                    type: 'linear',
                    position: 'right',
                    title: 'Soil Moisture (%)',
                    beginAtZero: true,
                    min: 0,
                    max: Math.ceil(minMaxDatasets['Mois'].max * 1.1),
                },
                y4: {
                    type: 'linear',
                    position: 'left',
                    title: 'pflanzenverfügbares Wasser',
                    beginAtZero: true,
                    min: 0,
                    max: Math.ceil(minMaxDatasets['PASW_AVG'].max * 1.1),
                },
                y5: {
                    type: 'linear',
                    position: 'left',
                    title: 'Biomasse (t/ha)',
                    beginAtZero: true,
                    min: 0,
                    max: Math.ceil(minMaxDatasets['AbBiom'].max * 1.1),
                },
            },
            elements: {
                point: {
                radius: 0,
                },
            },
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
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
return datasets;
};

function validateProject(project) {
    var valid = true;
    
    if (window.location.pathname.endsWith('/drought/') && project.userField === null) {
        valid = false;
        handleAlerts({'success': false, 'message': 'Please select a userfield'});
    } else if (window.location.pathname.endsWith('/monica/') && (project.longitude === null || project.latitude === null)) {
        valid = false;
        handleAlerts({'success': false, 'message': 'Please provide a valid location'});

    } else if (project.startDate === null || project.endDate === null || new Date(project.startDate) > new Date(project.endDate)) {
        valid = false;
        document.querySelector('a[href="#tabGeneralParameters"]').click();
        document.querySelector('#monicaStartDatePicker').focus()
        handleAlerts({'success': false, 'message': 'Please provide a valid date range'});
    } else if (project.rotation.length === 0) {
        valid = false;
        document.querySelector('a[href="#tabRotation"]').click();        
        // Focus on the crop rotation input field (if it has an ID or class)
        document.querySelector('#cropRotationInput')?.focus();

        handleAlerts({'success': false, 'message': 'Please provide a crop rotation'});
    } else if (project.soilProfileId === null) {
        valid = false;
        document.querySelector('a[href="#tabSite"]').click();        
        // Focus on the crop rotation input field (if it has an ID or class)
        const $emptySandInputs = $('td.sand input, td.clay input, td.ph input, td.raw-density input').filter(function () {
            return $(this).val() === '';
        });

        if ($emptySandInputs.length) {
            $emptySandInputs
                .addClass('is-invalid');      // Bootstrap red border

            $emptySandInputs
                .first()
                .focus();                     // focus first invalid field
        }

        

        handleAlerts({'success': false, 'message': 'Please provide a crop rotation'});
    } else {
        let found = false; // To stop after first invalid field
    
        project.rotation.forEach((rotation, rotationIndex) => {
            rotation.sowingWorkstep.forEach((sowingWorkstep) => {
                if (!found && sowingWorkstep.date == null) {
                    valid = false;
                    document.querySelector('a[href="#tabRotation"]').click();
    
                    // Focus on the corresponding sowing date input field
                    document.querySelector(`#sowingDate-${rotationIndex}-${sowingWorkstep.workstepIndex}`)?.focus();
                    found = true;
                    handleAlerts({'success': false, 'message': 'Please provide a sowing date for each crop'});
    
                } else if (!found && (new Date(sowingWorkstep.date) < new Date(project.startDate) || new Date(sowingWorkstep.date) > new Date(project.endDate))) {
                    valid = false;
                    document.querySelector('a[href="#tabRotation"]').click();
    
                    document.querySelector(`#id_date_sowingWorkstep_${rotationIndex}_${sowingWorkstep.workstepIndex}`)?.focus();
                    found = true;
                    handleAlerts({'success': false, 'message': 'Please provide a sowing date for each crop that is within your selected timeframe'});
    
                } else if (!found && (!sowingWorkstep.options.species || sowingWorkstep.options.species === '')) {
                    valid = false;
                    document.querySelector('a[href="#tabRotation"]').click();
    
                    document.querySelector(`#id_species_sowingWorkstep_${rotationIndex}_${sowingWorkstep.workstepIndex}`)?.focus();
                    found = true;
                    handleAlerts({'success': false, 'message': 'Please provide a crop for each sowing workstep!'});
    
                }
            });
            rotation.harvestWorkstep.forEach((harvestWorkstep) => {
                if (!found && rotation.harvestWorkstep.length > 0 && new Date(rotation.harvestWorkstep[0]?.date) < new Date(rotation.sowingWorkstep[0]?.date)) {
                    valid = false;
                    document.querySelector('a[href="#tabRotation"]').click();
                    document.querySelector(`#id_date_harvestWorkstep_${rotationIndex}_${harvestWorkstep.workstepIndex}`)?.focus();
                    found = true;
                    handleAlerts({'success': false, 'message': 'Please make sure that the harvest dates are after the sowing dates!'});
                }
            });

            rotation.tillageWorkstep.forEach((tillageWorkstep) => {
                
                if (!found && (rotation.tillageWorkstep.some(tillageWorkstep => tillageWorkstep.date == null ))) {
                    valid = false;
                    document.querySelector('a[href="#tabRotation"]').click();
                    document.querySelector(`#id_date_tillageWorkstep_${rotationIndex}_${tillageWorkstep.workstepIndex}`)?.focus();
                    found = true;
                    handleAlerts({'success': false, 'message': 'Please input a tillage Date !'});
                } else if (!found && (new Date(tillageWorkstep.date) < new Date(project.startDate) || new Date(tillageWorkstep.date) > new Date(project.endDate))) {
                    valid = false;
                    document.querySelector('a[href="#tabRotation"]').click();
    
                    document.querySelector(`#id_date_tillageWorkstep_${rotationIndex}_${tillageWorkstep.workstepIndex}`)?.focus();
                    found = true;
                    handleAlerts({'success': false, 'message': 'Please provide a tillage date that is within your selected timeframe'});
     
                } else if (!found && tillageWorkstep.options.tillage_depth == '' ) {
                    valid = false;
                    document.querySelector('a[href="#tabRotation"]').click();
                    document.querySelector(`#id_tillage_depth_tillageWorkstep_${rotationIndex}_${tillageWorkstep.workstepIndex}`)?.focus();
                    found = true;
                    handleAlerts({'success': false, 'message': 'Please input a valid tillage depth !'});
                }
            });

        rotation.mineralFertilisationWorkstep.forEach((mineralFertilisationWorkstep) => {
            if (!found && mineralFertilisationWorkstep.date == null) {
                valid = false;
                document.querySelector('a[href="#tabRotation"]').click();

                // Focus on the corresponding sowing date input field
                document.querySelector(`#sowingDate-${rotationIndex}-${mineralFertilisationWorkstep.workstepIndex}`)?.focus();
                found = true;
                handleAlerts({'success': false, 'message': 'Please provide a fertilisation date!'});

            } else if (!found && (new Date(mineralFertilisationWorkstep.date) < new Date(project.startDate) || new Date(mineralFertilisationWorkstep.date) > new Date(project.endDate))) {
                valid = false;
                document.querySelector('a[href="#tabRotation"]').click();

                document.querySelector(`#id_date_mineralFertilisationWorkstep_${rotationIndex}_${mineralFertilisationWorkstep.workstepIndex}`)?.focus();
                found = true;
                handleAlerts({'success': false, 'message': 'Please provide a fertilisation date that is within your selected timeframe'});

            } else if (!found && (!mineralFertilisationWorkstep.options.mineral_fertiliser || mineralFertilisationWorkstep.options.mineral_fertiliser === '')) {
                valid = false;
                document.querySelector('a[href="#tabRotation"]').click();

                document.querySelector(`#id_mineral_fertiliser_mineralFertilisationWorkstep_${rotationIndex}_${mineralFertilisationWorkstep.workstepIndex}`)?.focus();
                found = true;
                handleAlerts({'success': false, 'message': 'Please choose a fertiliser!'});

            } else if (!found && (!mineralFertilisationWorkstep.options.amount || mineralFertilisationWorkstep.options.amount === '')) {
                valid = false;
                document.querySelector('a[href="#tabRotation"]').click();

                document.querySelector(`#id_amount_mineralFertilisationWorkstep_${rotationIndex}_${mineralFertilisationWorkstep.workstepIndex}`)?.focus();
                found = true;
                handleAlerts({'success': false, 'message': 'Please choose a fertiliser!'});

            }
        });
        rotation.organicFertilisationWorkstep.forEach((organicFertilisationWorkstep) => {
            if (!found && organicFertilisationWorkstep.date == null) {
                valid = false;
                document.querySelector('a[href="#tabRotation"]').click();

                // Focus on the corresponding sowing date input field
                document.querySelector(`#sowingDate-${rotationIndex}-${organicFertilisationWorkstep.workstepIndex}`)?.focus();
                found = true;
                handleAlerts({'success': false, 'message': 'Please provide a fertilisation date!'});

            } else if (!found && (new Date(organicFertilisationWorkstep.date) < new Date(project.startDate) || new Date(organicFertilisationWorkstep.date) > new Date(project.endDate))) {
                valid = false;
                document.querySelector('a[href="#tabRotation"]').click();

                document.querySelector(`#id_date_organicFertilisationWorkstep_${rotationIndex}_${organicFertilisationWorkstep.workstepIndex}`)?.focus();
                found = true;
                handleAlerts({'success': false, 'message': 'Please provide a sowing date for each crop that is within your selected timeframe'});

            } else if (!found && (!organicFertilisationWorkstep.options.organic_fertiliser || organicFertilisationWorkstep.options.organic_fertiliser === '')) {
                valid = false;
                document.querySelector('a[href="#tabRotation"]').click();

                document.querySelector(`#id_organic_fertiliser_organicFertilisationWorkstep_${rotationIndex}_${organicFertilisationWorkstep.workstepIndex}`)?.focus();
                found = true;
                handleAlerts({'success': false, 'message': 'Please choose a fertiliser!'});

            } else if (!found && (!organicFertilisationWorkstep.options.amount || organicFertilisationWorkstep.options.amount === '')) {
                valid = false;
                document.querySelector('a[href="#tabRotation"]').click();

                document.querySelector(`#id_amount_organicFertilisationWorkstep_${rotationIndex}_${organicFertilisationWorkstep.workstepIndex}`)?.focus();
                found = true;
                handleAlerts({'success': false, 'message': 'Please choose a fertiliser!'});

            }
        });
        });
    }
    

    if (valid && project.id === null) {
        let modal = document.getElementById('saveProjectDialog')
        let saveProjectDialog = new bootstrap.Modal(modal);
        saveProjectDialog.show();

        const btnSave = document.getElementById('btnSaveMonicaProjectModalDialog');
        btnSave.addEventListener('click', function () {
            if (project.name) {
                saveProject(project);
                // saveProjectDialog.hide();
            } else {
                $('#monicaNewProjectModal').find('.modal-title').text('Neues Projekt erstellen');
                $('#monicaNewProjectModal').modal('show');
                document.querySelector('.monica-project-name').focus()
                handleAlerts({'success': false, 'message': 'Please provide a project name'});
            }
        });

        const btnDontSaveAndRun = document.getElementById('btnDontSaveAndRun');
        btnDontSaveAndRun.addEventListener('click', function () {
            ;
        });

    } 
    console.log("validateProject", valid, project)
    return valid;
};

function createModal(params) {
    console.log('create modal', params)
    try {

        let url = '/monica/' + params.parameters + '/';
        if (params.parameters_id) {
            url += params.parameters_id + '/';
        }
        if (params.rotation_index) {
            url += params.rotation_index + '/';
        }
        else if (params.lon) {
            url += params.lat + '/' + params.lon + '/';
        }

        // Fetch the content
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
            $('#formModal').modal('show'); 
        })
        .catch(error => console.error('Error:', error));
  
    } catch (error) {
        console.error('Error:', error);
    }
};

export function setOutputSettings() {
    localStorage.setItem(
        'outputSettings',
        JSON.stringify({
        colors: [
            'rgba(255, 200, 0, 0.7)', 
            'rgba(0, 150, 200, 0.7)', 
            'rgba(0, 200, 255, 0.7)', 
            'rgba(0, 255, 200, 0.7)',
            'rgba(0, 255, 100, 0.7)'],
    
        resultOutput: {
            'Precip': false,
            'Yield': true,
            'Irrig': false,
            // 'organ': false,
            'AbBiom': false,
            'PASW_AVG': false,
            // 'PASW_2': true,
            // 'PASW_3': true,
            // 'PASW_4': true,
            // 'PASW_5': true,
            'Mois_1': false,
            'Mois_2': false,
            'Mois_3': false,
            'SOC_1': false,
            'SOC_2': false,
            'SOC_3': false,
            'LAI': false,
        }
    }));
};




export function addMonicaEvents() {
     document.getElementById('btnOpenOutputSettings').addEventListener('click', function () {    
        const modalHtml = document.getElementById('outputSettingsModal');
        if (!modalHtml) {
            console.error("Modal element not found!");
            return;
        }
    
        let outputSettings = JSON.parse(localStorage.getItem('outputSettings'));
        console.log("Check 1 ")
    
        if (outputSettings && outputSettings.resultOutput) {
            // Find the checkbox container inside the modal
            let container = modalHtml.querySelector("#outputSettingsCheckboxDiv");
            if (!container) {
                console.error("Checkbox container not found inside the modal!");
                return;
            }
    
            // Clear old checkboxes before adding new ones
            container.innerHTML = '';
    
            // Create checkboxes dynamically
            Object.entries(outputSettings.resultOutput).forEach(([key, value]) => {
                let div = document.createElement("div");
                div.classList.add("form-check");  // Bootstrap styling
    
                let checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.id = key;
                checkbox.name = key;
                checkbox.checked = value;
                checkbox.classList.add("form-check-input");
    
                let label = document.createElement("label");
                label.htmlFor = key;
                label.textContent = resultTranslation[key];
                label.classList.add("form-check-label");

                checkbox.addEventListener("change", function () {

                    outputSettings.resultOutput[key] = this.checked;
                    localStorage.setItem('outputSettings', JSON.stringify(outputSettings));
                    console.log("Updated outputSettings:", outputSettings);
                });
    
                div.appendChild(checkbox);
                div.appendChild(label);
                container.appendChild(div);
                console.log('div', div);
            });
        } else {
            console.warn("No outputSettings found in localStorage!");
        }
    
        // Show the modal
        const modal = new bootstrap.Modal(modalHtml);
        modal.show();
    });

    // TODO: when translation is implemented, remove toggle-advanced-mode-de
    $('#toggle-advanced-mode').on('click', function () {
        const isAdvanced = $('.advanced').is(':visible');
    
        if (!isAdvanced) {
            $('.advanced').show(); 
            $(this).text('Switch to Simple Mode'); 
        } else {
            $('.advanced').hide(); 
            $(this).text('Switch to Advanced Mode'); 
        } 

    });

    $('#toggle-advanced-mode-de').on('click', function () {
        const isAdvanced = $('.advanced').is(':visible');
    
        if (!isAdvanced) {
            $('.advanced').show(); 
            $(this).text('Einfache Ansicht'); 
        } else {
            $('.advanced').hide(); 
            $(this).text('Erweiterte Ansicht'); 
        } 
        console.log('Advanced mode:', isAdvanced); // Log the current mode
    });

        // TAB CROP ROTATION EVENT LISTENERS
    $('#addRotationButton').on('click', () => {
        const project = MonicaProject.loadFromLocalStorage();
        const rotationIndex = project.rotation.length;
        project.addRotation();    
         
        addRotationToGui(rotationIndex, project.rotation[rotationIndex]);
        project.saveToLocalStorage();
    });

    $('#removeRotationButton').on('click', () => {
        const project = MonicaProject.loadFromLocalStorage();
        if (project.rotation.length > 1) {
            project.rotation.pop();
            project.saveToLocalStorage();
            $('#cropRotation').children().last().remove();
        } else {
            handleAlerts({'success': false, 'message': 'You cannot have less than 1 rotation'});
        }
    });

    // TAB CROP ROTATION EVENT LISTENERS
    $('#cropRotation').on('click', (event) => {
        const btnModifyParameters = event.target.closest('.modify-parameters');
        const rotationIndex = event.target.closest('.rotation').getAttribute('rotation-index');
        const project = MonicaProject.loadFromLocalStorage();
        console.log("EvenLister cropRotation click", project)
        if (event.target.classList.contains('add-workstep-button')) {
            
            const workstepType = event.target.closest('.rotation').querySelector('.workstep-type-select').value;
            
            const workstep = project.addWorkstep(workstepType, null, rotationIndex);
            console.log('added workstep ', workstep)
            // addWorkstepToGui(workstepType, rotationIndex, project.rotation[rotationIndex].workstepIndex, event.target.closest('.rotation').querySelector('.card-body'));
            addWorkstepToGui(workstepType, rotationIndex, workstep.workstepIndex, workstep);
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

        } else if (btnModifyParameters) {
            console.log('modify-parameters clicked');
            const parameters = btnModifyParameters.dataset.parameters;
            console.log('parameters', parameters);
            const value = btnModifyParameters.closest('.rotation').querySelector('.select-parameters.' + parameters).value;
            const params = {
                'parameters': parameters,
                'parameters_id': value,
                'rotation_index': rotationIndex
            }
            if (value != '') {
                createModal(params);
                // $('#formModal').modal('show');

            } else {
                event.preventDefault();
                handleAlerts({'success': false, 'message': 'Please select a parameter to modify'});
            }
        }
        
    });

    $('#cropRotation').on('change', (event) => {
        if (!window.isLoading && !$(event.target).hasClass('workstep-type-select')) {
        console.log("EvenLister cropRotation change")
        const rotationIndex = event.target.closest('.rotation').getAttribute('rotation-index');
        
        const workstepIndex = Number(event.target.getAttribute('workstep-index'));
        const workstepType = event.target.getAttribute('workstep-type');
        const name = event.target.getAttribute('name');
        console.log('crop rotation change', rotationIndex, workstepIndex, workstepType);

        const project = MonicaProject.loadFromLocalStorage();
        console.log('workstep...on change:', rotationIndex, workstepIndex, workstepType, name);
        var workstep = project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex);
        console.log('project.rotation[rotationIndex]', project.rotation[rotationIndex])
        console.log('project.rotation[rotationIndex][workstepType]', project.rotation[rotationIndex][workstepType])
        

        if (event.target.closest('.species-parameters')) {
            console.log('if species-parameters', workstep)
            workstep.options.species = event.target.value;
            const cultivarSelector = event.target.closest('.rotation').querySelector('.select-parameters.cultivar-parameters');
            const residueSelector = event.target.closest('.rotation').querySelector('.select-parameters.crop-residue-parameters');
            console.log('species-parameters', event.target.value)
            if (event.target.value != '') {
                console.log("species-parameters != ''", event.target.value)
               
                fetch('/monica/get_options/cultivar-parameters/' + event.target.value + '/')
                .then(response => response.json())
                .then(data => {
                    populateDropdown(data, cultivarSelector); 
                        workstep.options['cultivar'] = cultivarSelector.value                     
                        project.saveToLocalStorage();
                });
            
                console.log("FROM     THE SPECIES")
            
                fetch('/monica/get_options/crop-residue-parameters/' + event.target.value + '/')
                    .then(response => response.json())
                    .then(data => {
                        populateDropdown(data, residueSelector);
                                workstep.options['residue'] = residueSelector.value;
                                project.saveToLocalStorage();              
                    })
            } 
        
        } else if (event.target.type === 'checkbox') {
                workstep.options[name] = event.target.checked;
                project.saveToLocalStorage();
        } else if (event.target.classList.contains('workstep-datepicker')) {
                console.log(event.target.id)
                console.log($(`#${event.target.id}`).datepicker('getUTCDate').toISOString().split('T')[0])
                console.log('workstep', workstep)
                workstep.date = $(`#${event.target.id}`).datepicker('getUTCDate').toISOString().split('T')[0];
                project.saveToLocalStorage();
        }else {
                workstep.options[name] = event.target.value;
                project.saveToLocalStorage();
        };
        
    } 
    });
  
    //TAB SOIL EVENT LISTENERS
    $('#id_soil_moisture').on('change', function () {
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.userSoilMoistureParametersId = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#id_soil_organic').on('change', function () {
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.userSoilOrganicParametersId = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#id_soil_temperature').on('change', function () {
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.userSoilTemperatureParametersId = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#id_soil_transport').on('change', function () {
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.userSoilTransportParametersId = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#tabSite').on('click', (event) => {
        let params = {};
        const btnModifyParameters = event.target.closest('.modify-parameters');
        if (btnModifyParameters) {
            
            const parameters = btnModifyParameters.dataset.parameters;
            const value = $('.form-select.' + parameters).val();
            
            params = {
                'parameters': parameters,
                'parameters_id': value,
            }
            createModal(params);
            // $('#formModal').modal('show');    

            
        }  else if (event.target.classList.contains('show-soil-profile-modal')) {
            /*
             soil profiles are fetched for display and selection in the modal
             */
            console.log('Soil Button')
            const project = MonicaProject.loadFromLocalStorage();
            project.profile_source = $('input[name="profile_source"]:checked').val();
            project.saveToLocalStorage();
                if (project.profile_source === 'recommended') {
                    fetch('/monica/get-recommended-soil-profile/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken(),
                        },
                        body: JSON.stringify(project)
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Recommended soil profile response:', data);
                        if (data.success) {
                            console.log('success')
                            const soilProfile = data.soil_profile
                            clearSoilModal();
                                // all selectors are locked
                                $('#id_land_usage').append(new Option(soilProfile.landusage, soilProfile.landusage, true, true)).prop('disabled', true);;
                                $('#id_area_percentage').append(new Option(soilProfile.area_percentage, soilProfile.area_percentage, true, true)).prop('disabled', true);;
                                $('#id_system_unit').append(new Option(soilProfile.system_unit, soilProfile.system_unit, true, true)).prop('disabled', true);;
                                $('#id_soil_profile').append(new Option(soilProfile.id, soilProfile.id))
                                $('#div_id_soil_profile').prop('hidden', true);
                                
                                addSoilProfileToModal(soilProfile)

                                
                                $('#modalSoilSelection').modal('show');
                                // bindSoilModalEventListeners();

                        } else handleAlerts(data);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        handleAlerts({'success': false, 'message': 'An error occurred while fetching the soil profile. Please try again.'});
                    });
                } else if (project.profile_source === 'buek'){
                    fetch('get-soil-profile-landusage-choices/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken(),
                        },
                        body: JSON.stringify(project)
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('BUEK soil profile landusage choices response:', data);
                        if (data.success) {
                            clearSoilModal();
                            const landUsageChoices = data.land_usage_choices;
                            project.soilProfileBuekPolygons = data.buek_polygons;
                            project.saveToLocalStorage();
                            console.log('landusage choices', landUsageChoices)
                            const landUsageSelector = $('#id_land_usage');
                            // bindSoilModalEventListeners();
                            Object.entries(landUsageChoices).forEach(([value, name]) => {
                                landUsageSelector.append(new Option(name, value));
                            });
                            landUsageSelector.trigger('change'); // Trigger change to load the corresponding soil profiles
                            $('#modalSoilSelection').modal('show');

                            
                        } else handleAlerts(data);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        handleAlerts({'success': false, 'message': 'An error occurred while fetching the land usage choices. Please try again.'});
                    });
                } else if (project.profile_source === 'user') {
                    project.soilProfileType = 'userSoilProfile';
                    project.soilProfileId = $('#id_user_soil_profile_selector').val();
                    project.saveToLocalStorage();
                    getSoilProfileFormsetHtml({profileType: 'user', profileId: project.soilProfileId, originalProfile: true});
                } else if (project.profile_source === 'scratch') {
                    project.soilProfileType = 'userSoilProfile';
                    project.soilProfileId = null;
                    project.saveToLocalStorage();
                    getSoilProfileFormsetHtml({profileType: 'scratch', profileId: null, originalProfile: null});
                }
            
        } else if (event.target.classList.contains('add-horizon-button')) {
            markSaveNecessary(true);
            const table = document.querySelector("#soil-layers-table tbody");
            const totalForms = document.querySelector("#id_soil_horizons-TOTAL_FORMS");

            const currentCount = parseInt(totalForms.value);
            const newRow = table.children[0].cloneNode(true);

            newRow.querySelectorAll("input, select").forEach(input => {
                input.name = input.name.replace(/-\d+-/, `-${currentCount}-`);
                input.id = input.id.replace(/-\d+-/, `-${currentCount}-`);
                if (input.name.endsWith("horizon_no")) {
                
                    input.value = currentCount + 1;
                } else {
                    input.value = "";
                }
            });
            newRow.dataset.horizonNo = currentCount + 1;
            newRow.querySelector(".horizon-count").textContent = currentCount + 1;
            table.appendChild(newRow);
            totalForms.value = currentCount + 1;
        } else if (event.target.classList.contains('delete-horizon-button')) {
            markSaveNecessary(true);
            const table = $("#soil-layers-table");    
            const totalForms = $("#id_soilhorizon_set-TOTAL_FORMS");
            const currentCount = parseInt(totalForms.val(), 111);
            

            if (currentCount < 1)  {
                handleAlerts({'success': false, 'message': 'At least one soil horizon is required.'});
                return;
            }
            $(event.target).closest("tr").remove();

            const rows = table.find("tbody tr.soil-layer-row");
            
                rows.each(function (index) {
                    const horizonNo = index + 1;
                    const row = $(this);

                    // data attribute
                    row.attr("data-horizon-no", horizonNo);

                    // visible number
                    row.find(".horizon-count").text(horizonNo);

                    // inputs & selects
                    row.find("input, select").each(function () {
                        if (this.name) {
                            this.name = this.name.replace(/-\d+-/, `-${index}-`);
                        }
                        if (this.id) {
                            this.id = this.id.replace(/-\d+-/, `-${index}-`);
                        }
                        if (this.name && this.name.endsWith("horizon_no")) {
                            this.value = horizonNo;
                        }
                    });
                });

                // Update formset count
                totalForms.val(rows.length);
        } else if (event.target.classList.contains('advanced-soil-parameters-toggle')) {
            $('.advanced-soil-parameters').toggleClass('d-none');
        } else if (event.target.classList.contains('reset-soil-form-button')) {
            const project = MonicaProject.loadFromLocalStorage();
            const soilProfile = {
                'soilProfileId': project.soilProfileId,
                'soilProfileType': project.soilProfileType,
            }
            getSoilProfileFormsetHtml(project);
        } else if (event.target.classList.contains('save-soil-profile-button')) {
  
            saveSoilProfileFormset();
        }
    });   


    function validateSoilProfileFormset() {
        const rows = document.querySelectorAll("#soil-layers-table tbody tr.soil-layer-row");
        let valid = true;
        let counter = 0;
        let totalThickness = 0;
        rows.forEach(row => {
            
            const thickness = row.querySelector(`input[name="soil_horizons-${counter}-thickness"]`).value;
            totalThickness += Number(thickness);
            const sand = row.querySelector(`input[name="soil_horizons-${counter}-sand"]`).value;
            const clay = row.querySelector(`input[name="soil_horizons-${counter}-clay"]`).value;
            const ph = row.querySelector(`input[name="soil_horizons-${counter}-ph"]`).value;
            const c_n = row.querySelector(`input[name="soil_horizons-${counter}-c_n"]`).value;
            const raw_density = row.querySelector(`input[name="soil_horizons-${counter}-raw_density"]`).value;
            const corg = row.querySelector(`input[name="soil_horizons-${counter}-organic_carbon"]`).value;
            
            if ((Number(sand) + Number(clay)) > 100) {
                valid = false;
                row.querySelector(`input[name="soil_horizons-${counter}-sand"]`).classList.add('is-invalid');
                row.querySelector(`input[name="soil_horizons-${counter}-clay"]`).classList.add('is-invalid');
            } else {
                row.querySelector(`input[name="soil_horizons-${counter}-sand"]`).classList.remove('is-invalid');
                row.querySelector(`input[name="soil_horizons-${counter}-clay"]`).classList.remove('is-invalid');
            }
            if (sand < 0 || sand > 100 || isNaN(sand)) {
                valid = false;
                row.querySelector(`input[name="soil_horizons-${counter}-sand"]`).classList.add('is-invalid');
            }
            if (clay < 0 || clay > 100 || isNaN(clay)) {
                valid = false;
                row.querySelector(`input[name="soil_horizons-${counter}-clay"]`).classList.add('is-invalid');
            }
            
            if (ph <0 || ph > 14 || isNaN(ph)) {
                valid = false;
                row.querySelector(`input[name="soil_horizons-${counter}-ph"]`).classList.add('is-invalid');
            }
            if (c_n <= 0 || c_n > 15 || isNaN(c_n)) {
                valid = false;
                row.querySelector(`input[name="soil_horizons-${counter}-c_n"]`).classList.add('is-invalid');
            }
            if (!thickness || isNaN(thickness) || Number(thickness) <= 0) {
                valid = false;
                row.querySelector(`input[name="soil_horizons-${counter}-thickness"]`).classList.add('is-invalid');
            }
            if (raw_density <= 0 || isNaN(raw_density)) {
                valid = false;
                row.querySelector(`input[name="soil_horizons-${counter}-raw_density"]`).classList.add('is-invalid');
            }
            if (corg < 0 || corg > 100 || isNaN(corg)) {
                valid = false;
                row.querySelector(`input[name="soil_horizons-${counter}-organic_carbon"]`).classList.add('is-invalid');
            }
            counter += 1;
        });
        if (totalThickness < 2.0) { valid = false; }
        return valid;
    };

    $('#soil-profile-formset-container').on('change', (event) => {
        // for changes in of the actual soil profile form
        if (window.isLoading) return;
        event.target.classList.remove('is-invalid');
        validateSoilProfileFormset();
        markSaveNecessary(true);
    });


    function saveSoilProfileFormset() {
        const project = MonicaProject.loadFromLocalStorage();
        const form = document.getElementById('soil-profile-formset');
        const formData = new FormData(form);
        const data = {
            formData: formData,
            project: project,
        }
        fetch('/monica/save-soil-profile/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken(),
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('saveSoilProfileFormset', data);
            if (data.message.success) {
                handleAlerts(data.message);
                project.soilProfileId = data.soil_profile_id;
                $('#soilProfileName').text(data.profile_name);
                project.saveToLocalStorage();
                markSaveNecessary(false);
            } else {
                handleAlerts(data.message);
            }
        })
        .catch(error => console.error('Error:', error));

    }



    // TAB PROJECT EVENT LISTENERS
    $('#monicaNewProjectModal').on('hidden.bs.modal', function () {
        // Reset the form inside the modal
        $('#newProjectForm')[0].reset();
    });

    $('#tabProject').on('click', (event) => {
        const btnModifyParameters = event.target.closest('.modify-parameters');
        if (btnModifyParameters) {
            
            const parameters = btnModifyParameters.dataset.parameters;
            const value = $('.form-select.' + parameters).val();
            
                const params = {
                    'parameters': parameters,
                    'parameters_id': value,
                }
                console.log('Create Modal', params)
                createModal(params);      
                // $('#formModal').modal('show');    
        } else if (event.target.classList.contains('monica-project')) {
            const projectId = $('#id_monica_project').val(); 
            const selecteprojectName = $('#id_monica_project option:selected').text()
            if (event.target.classList.contains('load-project')) {
                console.log('LOAD PROJECT')
                loadProjectFromDB(projectId)
                .then(project => {
                    loadProjectToGui(project);
                    
                });
            } else if (event.target.classList.contains('new-project')) {
                console.log('NEW PROJECT')
                // $('#newProjectForm')[0].reset();

                $('#monicaNewProjectModal').find('.modal-title').text('Create new project');
                $('#monicaNewProjectModal').modal('show');
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
    
    $('.save-new-project').on('click', (e) => {
        const $button = $(e.target);
       
        console.log('saveProjectButton clicked');
        
        
        // Get the project name field
        const projectNameInput = $('#id_project_name');
        const projectName = projectNameInput.val().trim();
    
        // Check if the project name is empty
        if (!projectName) {
            projectNameInput.addClass('is-invalid'); // Bootstrap class for red highlight
            projectNameInput.focus();
            return; // Stop execution if validation fails
        } else {
            projectNameInput.removeClass('is-invalid'); // Remove error class if fixed
        }
    
        const project = new MonicaProject();
        
        try {
            project.longitude = $('#id_longitude').val();
            project.latitude = $('#id_latitude').val();
        } catch (e) {
            console.log('Longitude/Latitude not found');
        }
    
        try {
            // project.userField = $('#userFieldSelect').val();
            let userField = localStorage.getItem('userFieldId');
            project.userField = userField ? userField : null;
        } catch (e) {
            console.log('UserField not found');
        }
    
        project.name = projectName;
        project.description = $('#id_project_description').val();
        project.startDate = $('#id_project_start_date').datepicker('getUTCDate');
        project.modelSetupId = $('#id_project_model_setup').val();
    
        project.saveToLocalStorage();
        $('#monica-project-name').text(project.name);
    
        fetch('save-project/', {
            method: 'POST',
            body: JSON.stringify(project),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('data', data);
            if (data.message.success) {
                $('#monicaNewProjectModal').modal('hide');
                document.getElementById('newProjectForm').reset();
                
                project.id = data.project_id;
                $('#project-info').find('.card-title').text('Project '+ data.project_name);
                updateDropdown('monica-project', '', data.project_id);
                handleAlerts(data.message);
                
                // $('.new-project-modal-form')[0].reset();

                
                $('#monicaProjectModal').modal('hide');
                project.saveToLocalStorage();
            } else {
                handleAlerts(data.message);
            }
        });
    });
    
    $('#projectName').on('change', function () {
        // TODO obsolete!!??
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.name = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#projectDescription').on('change', function () {
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.description = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#id_user_environment').on('change', function () {
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.userEnvironmentParametersId = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#id_user_crop_parameters').on('change', function () {
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.userCropParametersId = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#id_user_simulation_settings').on('change', function () {
        if (!window.isLoading) {
            const project = MonicaProject.loadFromLocalStorage();
            project.userSimulationSettingsId = $(this).val();
            project.saveToLocalStorage();
        }
    });

    $('#btnOutputSettingsApply').on('click', function () {
        // the selection of output parameters got changed so the graph needs to be reloaded
        createChartDataset();
    });

    $('#todaysDatePicker').datepicker('update', new Date());
    $('#todaysDatePicker').trigger('focusout'); // saving the todays date to the project

    $('#monica-project-save').on('click', function () {
        console.log('monica-project-save clicked');
        const project = MonicaProject.loadFromLocalStorage();
        if (validateProject(project)) {
            saveProject(project);
        } 
      });

    $('.nav-link.monica').on('click', function (e) {
        e.preventDefault();
        $('.nav-link.monica').removeClass('active');
        $(this).addClass('active');
        const target = $(this).attr('href');
        $('.tab-pane').hide();
        $(target).show();
    });

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

    $('#monicaStartDatePicker, #monicaEndDatePicker').on('changeDate focusout', handleDateChange);
};

function runSimulation(monicaProject) {   
    console.log('runSimulation', monicaProject);
    fetch(runSimulationUrl, {
        method: 'POST',
        body: JSON.stringify(monicaProject),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('data', data.message.success);
        if (data.message.success) {
            // console.log('SUCCESS', data.message)
            $('#runSimulationButton').prop('disabled', true);
            $('#runSimulationButton').text('...Simulation running');
            // Remove 'active' class from all nav links
            $('.nav-link.monica').removeClass('active');

            $('#resultTab').removeClass('disabled').addClass('active').trigger('click');

            let listOfResults = data.message.message
            console.log('ListofResults: ', data);
            localStorage.setItem('monicaResults', JSON.stringify(listOfResults));
            createChartDataset();
            
            $('#runSimulationButton').prop('disabled', false);
            $('#runSimulationButton').text('Simulation starten');

        } else {
            handleAlerts(data.message);
            $('#runSimulationButton').prop('disabled', false);
            $('#runSimulationButton').text('Simulation starten');
        }    
    })
    .then(() => {
        //TODO: check if this is needed
        $('#resultTab').removeClass('disabled').addClass('active').trigger('click');
    });
};


export function bindModalEventListeners(parameters) {
    console.log('bindModalEventListeners', parameters);
    // bind the save/save as new/delete buttons in the modal for monica parameters
    try {
        const modalForm = document.getElementById('modalForm');
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
            if (modalClose) {
                
                $('#formModal').modal('hide');
            }
        });

        document.getElementById('saveAsNewModalParameters').addEventListener('click', () => {
            console.log("bindModalEventListeners saveAsNewModalParameters clicked");
            const modalForm = document.getElementById('modalForm');

            const modalAction = 'save_as_new'

            const modalClose = submitModalForm(modalForm, modalAction);
            if (modalClose) {
                $('#formModal').modal('hide');
            }
        });

        document.getElementById('deleteParameters').addEventListener('click', () => {
            console.log("bindModalEventListeners deleteParameters clicked");
            const modalForm = document.getElementById('modalForm');
            const modalAction = 'delete'
            const modalClose = submitModalForm(modalForm, modalAction);
            if (modalClose) {
                $('#formModal').modal('hide');
            }
        });
    } catch {
        console.log('no modal save buttons found');
    }
    // user-simulation-settings is mainly the same as all monica parameters, but with two unfoldable subdivisions
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



// Soil matters
function clearSoilModal() {
    console.log('Clear Soil Modal')
    $('#id_land_usage').empty().prop('disabled', false);
    $('#id_area_percentage').empty().prop('disabled', false);
    $('#id_system_unit').empty().prop('disabled', false);
    $('#id_soil_profile').empty();
    
    $('#div_id_soil_profile').prop('hidden', false);
    $('#correctedSoilProfileTableBody').empty();
    $('#correctedSoilProfile').addClass('d-none');
    $('#originalSoilProfileTableBody').empty();
}

function createSoilProfileTableRow(horizon, horizon_no) {
    // creates a row in the soil form table
    const $tr = $('<tr>');
    $tr.append($('<td>').text(horizon_no));
    Object.values(horizon).forEach((value, index) => {
        const $td = $('<td>').text(value);
        $tr.append($td);
    });
    return $tr;
};

export function getSoilProfileFormsetHtml(profile) {
    // the given soil profile is loaded into a form (not the soil modal)
    console.log('getSoilProfileFormsetHtml', profile);
    fetch('/monica/get-soil-profile-form/', {
            method: 'POST',
            body: JSON.stringify(profile),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if(data.message.success) {
                $('#soil-profile-formset-container').html(data.message.html);
                markSaveNecessary(false);
                document
                .getElementById('soil-profile-formset-container')
                .scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            else handleAlerts(data.message);
        })
        .catch(error => console.error('Error:', error));
};

function markSaveNecessary(needsToBeSaved) {
  $("#saveProfileIndicator").toggleClass("d-none", !needsToBeSaved);
}


function handleLandUsageChange(clcCode) {
    // handles the landusage selector in the soil modal
    console.log('id_land_usage changed', clcCode)
    const project = MonicaProject.loadFromLocalStorage();
    project.soilProfileLandusage = clcCode;
    project.saveToLocalStorage();
    fetch('/monica/get-soil-profile-area-percentage-choices/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(project)
    })
    .then(response => response.json())
    .then(data => {
        console.log('System unit choices response:', data);
        if (data.success) {
            const areaPercentageSelector = $('#id_area_percentage');
            areaPercentageSelector.empty();
            Object.entries(data.area_percentage_choices).forEach(([value, name]) => {
                areaPercentageSelector.append(new Option(name, value));
            });
            areaPercentageSelector.trigger('change');
            
        } else handleAlerts(data);
    });
};

function handleAreaPercentageChange(areaPercentage){
    // handles the area percentage selector in the soil modal
    const project = MonicaProject.loadFromLocalStorage();
     project.soilProfileAreaPercentage = areaPercentage;
    project.saveToLocalStorage();
        fetch('/monica/get-soil-profile-system-unit-choices/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(project)
    })
    .then(response => response.json())
    .then(data => {
        console.log('System unit choices response:', data);
        if (data.success) {
            const systemUnitSelector = $('#id_system_unit');
            systemUnitSelector.empty();
            Object.entries(data.system_unit_choices).forEach(([value, name]) => {
                systemUnitSelector.append(new Option(name, value));
            });
            systemUnitSelector.trigger('change');
        } else handleAlerts(data);
    });
};

function handleSystemUnitChange(systemUnit) {
    // handles the system units selector in the soil modal
    const project = MonicaProject.loadFromLocalStorage();
    project.soilProfileSystemUnit = systemUnit;
    project.saveToLocalStorage();
    fetch('/monica/get-soil-profile-choices/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(project)
    })
    .then(response => response.json())
    .then(data => {
        console.log('System unit choices response:', data);
        if (data.success) {
            const soilProfileSelector = $('#id_soil_profile');
            soilProfileSelector.empty();
            Object.entries(data.soil_profile_choices).forEach(([value, name]) => {
                soilProfileSelector.append(new Option(name, value));
            });
            soilProfileSelector.trigger('change');
        } else handleAlerts(data);
    });
};

function handleSoilProfileChange(soilProfileId) {
    // handles the soil profile selector in the soil modal
    fetch(`/monica/get-soil-profile-info/${soilProfileId}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Soil profile info response:', data);
        if (data.success) {
            const soilProfile = data.soil_profile;
            addSoilProfileToModal(soilProfile)
        } else handleAlerts(data);
    });
};


export function bindSoilModalEventListeners() {
// The soil modal's eventlisteners
    $('#btnCorrectedSoilProfile').on('click', function (e) {
        console.log('btnCorrectedSoilProfile clicked');
        const project = MonicaProject.loadFromLocalStorage();
        project.soilProfileType = "buekSoilProfile";
        project.soilProfileId = $('#id_soil_profile').val();
        project.saveToLocalStorage();
        console.log('get-soil-profile', JSON.stringify(project));
        getSoilProfileFormsetHtml({profileType: 'buek', profileId: $('#id_soil_profile').val(), originalProfile: false});
    });

    $('#btnOriginalSoilProfile').on('click', function (e) {        
        const project = MonicaProject.loadFromLocalStorage();
        project.soilProfileType = "buekSoilProfile";
        project.soilProfileId =  $('#id_soil_profile').val();
        project.saveToLocalStorage();
        getSoilProfileFormsetHtml({profileType: 'buek', profileId: $('#id_soil_profile').val(), originalProfile: true});
    });

    $('#buekSoilSelection').on('change', function (event) {
        console.log('Soil Modal change event', event.target.id, event.target.value);
        const project = MonicaProject.loadFromLocalStorage();
        if(event.target.id === 'id_land_usage') {
           handleLandUsageChange(event.target.value);
        } else if(event.target.id === 'id_area_percentage') {
           handleAreaPercentageChange(event.target.value);
        } else if (event.target.id === 'id_system_unit') {
            handleSystemUnitChange(event.target.value);
        } else if (event.target.id === 'id_soil_profile') {
            handleSoilProfileChange(event.target.value);
        };
    });
};


function addSoilProfileToModal(soilProfile) {
    $('#correctedSoilProfileTableBody').empty();
    $('#originalSoilProfileTableBody').empty();
    let horizon_no = 1;
    if (soilProfile.SoilProfileParameters.length > 0) {
        $('#btnOriginalSoilProfile').attr('data-complete-profile', 'false');
        soilProfile.SoilProfileParameters.forEach(horizon => {
        $('#correctedSoilProfileTableBody').append(createSoilProfileTableRow(horizon, horizon_no));
        horizon_no++;
    });

    $('#correctedSoilProfile').removeClass('d-none');
    } else {
        $('#btnOriginalSoilProfile').attr('data-complete-profile', 'true');
    };

    horizon_no = 1;
    soilProfile.OriginalSoilProfileParameters.forEach(horizon => {    
        $('#originalSoilProfileTableBody').append(createSoilProfileTableRow(horizon, horizon_no));
        horizon_no++;
    });
};

// TODO addToDropdown instead of updateDropdown
export function updateDropdown(parameterType, rotationIndex, newId) {
    console.log('updateDropdown', parameterType, rotationIndex, newId);
    // the absolute path is needed for swn, because most options are exclusively from /monica
    let baseUrl = '/monica/get_options/';
    // save project differs in monica and swn, therefore:
    if (parameterType === 'monica-project') {
        console.log('updateDropdown saveProject');
        baseUrl = 'get_options/';
    }
    console.log('updateDropdown baseUrl', baseUrl);
    var select = document.querySelector('.form-select.' + parameterType); 
    fetch(baseUrl + parameterType + '/')
        .then(response => response.json())
        .then(data => {
            if (rotationIndex != '') {
                const rotationDiv = document.querySelector(`div[rotation-index='${rotationIndex}']`);
                select = rotationDiv.querySelector('.select-parameters.' + parameterType);
            } 
            populateDropdown(data, select);
        })
        .then(() => {
            if (newId != '') {
                select.value = newId
            }
            $(select).trigger('change');
        })
        .catch(error => console.log('Error in updateDropdown', error));
};


function submitModalForm(modalForm, modalAction) {
    console.log('submitModalForm', modalForm, modalAction);
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
        if (data.message.success) {
            $('#formModal').modal('hide');
            //TODO: deal with it
            handleAlerts(data.message);
            const parameterType = actionUrl.split('/')[0];
            const rotationIndex = actionUrl.split('/')[2];
            if (modalAction === 'save_as_new') {
                // addToDropdown(data.new_id, document.querySelector('.form-select.' + parameterType));
                updateDropdown(parameterType, rotationIndex, data.new_id);
            } else if (modalAction === 'delete') {
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

function calculateDaysInRotation() {
        var startDate = project.startDate;
        var endDate = project.endDate;  

        var daysInRotation = (endDate - startDate) / (1000 * 60 * 60 * 24);
        var yearsInRotation = Math.ceil(daysInRotation / 365);
        return [daysInRotation, yearsInRotation];
    };

export function startMonica() {
    $('.advanced').hide();
    $('.tab-pane').hide();

    const tabs = document.querySelectorAll('.monica.nav-link');
    tabs[1].click();
}
