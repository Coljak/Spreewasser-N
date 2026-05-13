
import {MonicaCalculation, MonicaProject, Rotation, Workstep } from '/static/monica/monica_model.js';
import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, populateDropdown } from '/static/shared/utils.js';
import { getOrCreateLegendList, htmlLegendPlugin, htmlMonicaLegendPlugin } from '/static/vendor/chartjs/chartjs-html-legend.js';

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
    if (project.siteId) {$('#id_site').val(project.siteId)};
    // if (project.site_name) {$('#id_site_name').text(project.site_name)};
    if (project.altitude) {$('#id_altitude').val(project.altitude)};
    if (project.slope) {$('#id_slope').val(project.slope)};
    if (project.n_deposition) {$('#id_n_deposition').val(project.n_deposition)};
    $('#userFieldSelect').val(project.userField);
    if (project.soilProfileType === 'buekSoilProfile') {
        getSoilProfileFormsetHtml({profileType: 'buek', profileId: project.soilProfileId, originalProfile: false});
    } else if (project.soilProfileType === 'userSoilProfile') {
        getSoilProfileFormsetHtml({profileType: 'buek', profileId: project.soilProfileId, originalProfile: true});
    };

    
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
    'LAI': 'LAI, Überblattungsindex',
    'PASW': 'Pflanzenverfügbares Wasser',
    'PASW_AVG': 'Pflanzenverfügbares Wasser ∅',
    'PASW_1': 'Pflanzenverfügbares Wasser 0-10cm',
    'PASW_2': 'Pflanzenverfügbares Wasser 10-20cm',
    'PASW_3': 'Pflanzenverfügbares Wasser 20-30cm',
    'PASW_4': 'Pflanzenverfügbares Wasser 30-40cm',
    'PASW_5': 'Pflanzenverfügbares Wasser 40-50cm',
    'PASW_6': 'Pflanzenverfügbares Wasser 50-60cm',
    'PASW_7': 'Pflanzenverfügbares Wasser 60-70cm',
    'PASW_8': 'Pflanzenverfügbares Wasser 70-80cm',
    'PASW_9': 'Pflanzenverfügbares Wasser 80-90cm',
    'PASW_10': 'Pflanzenverfügbares Wasser 90-100cm',
    'PASW_11': 'Pflanzenverfügbares Wasser 100-110cm',
    'PASW_12': 'Pflanzenverfügbares Wasser 110-120cm',
    'PASW_13': 'Pflanzenverfügbares Wasser 120-130cm',
    'PASW_14': 'Pflanzenverfügbares Wasser 130-140cm',
    'PASW_15': 'Pflanzenverfügbares Wasser 140-150cm',
    'PASW_16': 'Pflanzenverfügbares Wasser 150-160cm',
    'PASW_17': 'Pflanzenverfügbares Wasser 160-170cm',
    'PASW_18': 'Pflanzenverfügbares Wasser 170-180cm',
    'PASW_19': 'Pflanzenverfügbares Wasser 180-190cm',
    'PASW_20': 'Pflanzenverfügbares Wasser 190-200cm',
    'Mois': 'Bodenfeuchte',
    'Mois_AVG': 'Bodenfeuchte ∅',
    'Mois_1': 'Bodenfeuchte 0-10cm',
    'Mois_2': 'Bodenfeuchte 10-20cm',
    'Mois_3': 'Bodenfeuchte 20-30cm',
    'Mois_4': 'Bodenfeuchte 30-40cm',
    'Mois_5': 'Bodenfeuchte 40-50cm',
    'Mois_6': 'Bodenfeuchte 50-60cm',
    'Mois_7': 'Bodenfeuchte 60-70cm',
    'Mois_8': 'Bodenfeuchte 70-80cm',
    'Mois_9': 'Bodenfeuchte 80-90cm',
    'Mois_10': 'Bodenfeuchte 90-100cm',
    'Mois_11': 'Bodenfeuchte 100-110cm',
    'Mois_12': 'Bodenfeuchte 110-120cm',
    'Mois_13': 'Bodenfeuchte 120-130cm',
    'Mois_14': 'Bodenfeuchte 130-140cm',
    'Mois_15': 'Bodenfeuchte 140-150cm',
    'Mois_16': 'Bodenfeuchte 150-160cm',
    'Mois_17': 'Bodenfeuchte 160-170cm',
    'Mois_18': 'Bodenfeuchte 170-180cm',
    'Mois_19': 'Bodenfeuchte 180-190cm',
    'Mois_20': 'Bodenfeuchte 190-200cm',
    'SOC': 'organischer Kohlenstoff',
    'SOC_AVG': 'organischer Kohlenstoff ∅',
    'SOC_1': 'organischer Kohlenstoff 0-10cm',
    'SOC_2': 'organischer Kohlenstoff 10-20cm',
    'SOC_3': 'organischer Kohlenstoff 20-30cm',
    'SOC_4': 'organischer Kohlenstoff 30-40cm',
    'SOC_5': 'organischer Kohlenstoff 40-50cm',
    'SOC_6': 'organischer Kohlenstoff 50-60cm',
    'SOC_7': 'organischer Kohlenstoff 60-70cm',
    'SOC_8': 'organischer Kohlenstoff 70-80cm',
    'SOC_9': 'organischer Kohlenstoff 80-90cm',
    'SOC_10': 'organischer Kohlenstoff 90-100cm',
    'SOC_11': 'organischer Kohlenstoff 100-110cm',
    'SOC_12': 'organischer Kohlenstoff 110-120cm',
    'SOC_13': 'organischer Kohlenstoff 120-130cm',
    'SOC_14': 'organischer Kohlenstoff 130-140cm',
    'SOC_15': 'organischer Kohlenstoff 140-150cm',
    'SOC_16': 'organischer Kohlenstoff 150-160cm',
    'SOC_17': 'organischer Kohlenstoff 160-170cm',
    'SOC_18': 'organischer Kohlenstoff 170-180cm',
    'SOC_19': 'organischer Kohlenstoff 180-190cm',
    'SOC_20': 'organischer Kohlenstoff 190-200cm',

};


const parameterColors = {
    Yield: '#ff9800',
    AbBiom: '#4caf50',
    PASW: '#2196f3',
    Mois: '#9c27b0',
    SOC: '#795548',
    LAI: '#009688',
    Irrig: '#09dbdbff',
    Precip: '#1976d2'
};

const resultLineStyles = [
    [],
    [10, 5],
    [2, 4]
];
const axisGroups = {
    Irrig: 'y1',
    Precip: 'y1',

    Yield: 'y2',
    AbBiom: 'y2',
    LAI: 'y3',
    Mois: 'y4',
    SOC: 'y5',
    PASW: 'y6',
    organ: 'y7'
};

const axisUnits = {
    y1: 'mm',

    y2: 't/ha',
    y3: '%',
    y4: 'm²/m²',
    y5: '%',
    y6: '%',
    y7: ''
};

// the reverse of axisGroups to assign the right parameters to the right axis in the chart options


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


export function createChartDataset() {
    let listOfResults = JSON.parse(localStorage.getItem('monicaResults'));
    let outputSettings = JSON.parse(localStorage.getItem('outputSettings'));
    console.log('outputSettings', outputSettings);

    let resultOutput = outputSettings.resultOutput;
    // all parameters present in the result
    let parameters = [];
    Object.entries(resultOutput).forEach(([key, value]) => {
        if (value) {
            parameters.push(key);
        }
    });
    function getBaseParam(p) {
        return p.split('_')[0];
    }
    // all base parameters (no layer number or avg)
    const base_parameters = [
        ...new Set(
            parameters.map(p => getBaseParam(p))
        )
    ];

    let axisMapping = {};
    Object.entries(axisGroups).forEach(([key, value]) => {
        if (base_parameters.includes(key)) {
            if (!axisMapping[value]) {
                axisMapping[value] = [];
            }
            axisMapping[value].push(key);
        }
    });

    // axis
    let axisTitles = {};
    let axisExtents = {};
    Object.entries(axisMapping).forEach(([axis, base_ps]) => {
        // title of each axis
        const axisTitle = base_ps.map(p => resultTranslation[p]).join(', ') + ` (${axisUnits[axis]})`; 
        // translates them and joins them with a comma
        axisTitles[axis] = axisTitle;

        // extends of each axis, finding min and max
        if (!axisExtents[axis]) {
            axisExtents[axis] = {
                min: Infinity,
                max: -Infinity
            };
        }
        base_ps.forEach(base_p => {
            let all_vals = [];
            listOfResults.forEach(result => {
                const daily = result.daily;
                Object.entries(daily).forEach(([key, value]) => {
                    if (key.startsWith(base_p)) {
                        all_vals = all_vals.concat(Object.values(value).filter(v => !isNaN(v)));
                    }
                });

                if (all_vals.length) {
                    const minVal = Math.min(...all_vals);
                    const maxVal = Math.max(...all_vals);

                // Update global min/max
                axisExtents[axis].min = Math.min(axisExtents[axis].min, minVal);
                axisExtents[axis].max = Math.max(axisExtents[axis].max, maxVal);
                //     }
                }
            });
        });
    });

    /// NEW /////
    let scales = {};
    Object.entries(axisMapping).forEach(([axis, base_ps]) => {
        scales[axis] = {
            type: 'linear',
            position: axis === 'y1' ? 'right' : 'left',
            title: { display: true, text: axisTitles[axis] },
            beginAtZero: true,
            min: axisExtents[axis].min,
            max: axisExtents[axis].max * 1.1,
               
        };
    });

    // creating the list of datasets
    // get Precip only once
    let dates = listOfResults[0].daily.Date;
    let datasets = [];
    if (resultOutput.Precip) {
        datasets.push({
            type: 'bar',  // Specifies the type as bar for precipitation
            yAxisID: axisGroups.Precip,  
            label: resultTranslation.Precip,
            data: listOfResults[0].daily.Precip,
            backgroundColor: parameterColors.Precip,  
            borderColor: parameterColors.Precip,
            borderWidth: 1,
        })
    }
    const simulationLabels = {
        0: 'Baseline',
        1: 'Bewässert 1',
        2: 'Bewässert 2'
    };

    for (let i = 0; i < listOfResults.length; i++) {
        console.log(i);
        var msg = listOfResults[i].daily
        parameters.forEach(p => {
            if (p !== 'Precip' && msg[p]) {
                 // Irrigation should be on the same y-axis as Precip
                let base_p = getBaseParam(p);
                let axis = axisGroups[base_p];
                let ds = {
                    type: base_p === 'Irrig' ? 'bar' : 'line',  // Use bar for irrigation, line for others
                    yAxisID: axis,
                    label: `${resultTranslation[p]}`,
                    data: msg[p],
                    borderWidth: 2,
                    borderColor: parameterColors[base_p],
                    borderDash: resultLineStyles[i % resultLineStyles.length], // in case there should ever be more than 3 runs in one
                    pointHitRadius: 10,
                    simulationIndex: i,
                    simulationLabel: simulationLabels[i],
                    parameter: p,
                    base_parameter: base_p,
                }
                datasets.push(ds);
            }
        });
        
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
        plugins: [htmlMonicaLegendPlugin],
        options: {
            scales: scales,
            
            elements: {
                point: {
                radius: 0,
                },
            },
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                htmlLegend: {
                    containerID: 'chartLegend',
                },
                legend: {
                    display: false 
                },
                zoom: {
                    zoom: {
                    wheel: {
                        enabled: true,
                    },
                    pinch: {
                        enabled: true
                    },
                    mode: 'x',
                    }
                }
            },    
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

        if (!validateSoilProfileFormset()) {
            valid = false;
            handleAlerts({'success': false, 'message': 'Please complete the soil profile!'});
            document.querySelector('a[href="#tabSite"]').click();  
            document.querySelector('#soilProfileFormset')?.focus();
        }

        

        handleAlerts({'success': false, 'message': 'Please complete the soil profile!'});
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


function validateSoilProfileFormset() {
    console.log('validateSoilProfileFormset')
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
        if (sand < 0 || sand > 100 || isNaN(sand) || sand === '') {
            valid = false;
            row.querySelector(`input[name="soil_horizons-${counter}-sand"]`).classList.add('is-invalid');
        }
        if (clay < 0 || clay > 100 || isNaN(clay) || clay === '') {
            valid = false;
            row.querySelector(`input[name="soil_horizons-${counter}-clay"]`).classList.add('is-invalid');
        }
        
        if (ph <0 || ph > 14 || isNaN(ph) || ph === '') {
            valid = false;
            row.querySelector(`input[name="soil_horizons-${counter}-ph"]`).classList.add('is-invalid');
        }
        if (c_n <= 0 || c_n > 15 || isNaN(c_n) || c_n === '') {
            valid = false;
            row.querySelector(`input[name="soil_horizons-${counter}-c_n"]`).classList.add('is-invalid');
        }
        if (!thickness || isNaN(thickness) || Number(thickness) <= 0 || thickness === '') {
            valid = false;
            row.querySelector(`input[name="soil_horizons-${counter}-thickness"]`).classList.add('is-invalid');
        }
        if (raw_density <= 0 || isNaN(raw_density) || raw_density === '') {
            valid = false;
            row.querySelector(`input[name="soil_horizons-${counter}-raw_density"]`).classList.add('is-invalid');
        }
        if (corg < 0 || corg > 100 || isNaN(corg) || corg === '') {
            valid = false;
            row.querySelector(`input[name="soil_horizons-${counter}-organic_carbon"]`).classList.add('is-invalid');
        }
        counter += 1;
    });
    if (totalThickness <= 0) { valid = false; }
    
    return valid;
};




function loadRecommendedSoilProfile(project, lat, lon) {
    fetch(`/monica/get-recommended-soil-profile-id/${lat}/${lon}/`, {
                })
                .then(response => response.json())
                .then(data => {
                    
                    if (data.success) {
                        console.log('success', data)
                        project.soilProfileId = data.soil_profile_id;
                        console.log('Recommended soil profile id response:', data);
                        project.saveToLocalStorage();
                        getSoilProfileFormsetHtml({profileType: 'buek', profileId: project.soilProfileId, originalProfile: false});
                    } else handleAlerts(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    handleAlerts({'success': false, 'message': 'An error occurred while fetching the soil profile. Please try again.'});
                });
}

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

    // function getAltitude(lat, lon) {
    //     fetch(`https://api.open-meteo.com/v1/elevation?latitude=${lat}&longitude=${lon}`)
    //             .then(response => response.json())
    //             .then(data => {
    //                 if (data && data.elevation) {
    //                     const project = MonicaProject.loadFromLocalStorage();
    //                     project.altitude = data.elevation[0];
    //                     project.saveToLocalStorage();
    //                     $('#id_altitude').val(data.elevation[0]);
    //                 } else {
    //                     handleAlerts({'success': false, 'message': 'Could not fetch altitude for the given location.'});
    //                 }
    //             })
    //             .catch(error => {
    //                 console.error('Error fetching altitude:', error);
    //                 handleAlerts({'success': false, 'message': 'An error occurred while fetching altitude. Please try again.'});
    //             });
        
    // };

    function getAltitude(lat, lon) {
        fetch(`/monica/get-altitude/${lat}/${lon}`)
                .then(response => response.json())
                .then(data => {
                    if (data && data.altitude) {
                        const project = MonicaProject.loadFromLocalStorage();
                        project.altitude = data.altitude;
                        project.saveToLocalStorage();
                        $('#id_altitude').val(data.altitude);
                    } else {
                        handleAlerts({'success': false, 'message': 'Could not fetch altitude for the given location.'});
                    }
                })
                .catch(error => {
                    console.error('Error fetching altitude:', error);
                    handleAlerts({'success': false, 'message': 'An error occurred while fetching altitude. Please try again.'});
                });
        
    };

    function getSlope(lat, lon) {
        fetch(`/monica/get-slope/${lat}/${lon}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const project = MonicaProject.loadFromLocalStorage();
                    project.slope = data.slope;
                    project.saveToLocalStorage();
                    $('#id_slope').val(data.slope);
                } else {
                    handleAlerts({'success': false, 'message': 'Could not fetch slope for the given location.'});
                }
            })
            .catch(error => {
                console.error('Error fetching slope:', error);
                handleAlerts({'success': false, 'message': 'An error occurred while fetching slope. Please try again.'});
            });
    };

    function getNDeposition(lat, lon) {
        fetch(`/monica/get-n-deposition/${lat}/${lon}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const project = MonicaProject.loadFromLocalStorage();
                    project.n_deposition = data.n_deposition;
                    project.saveToLocalStorage();
                    $('#id_n_deposition').val(data.n_deposition);
                } else {
                    handleAlerts({'success': false, 'message': 'Could not fetch nitrogen deposition for the given location.'});
                }
            })
            .catch(error => {
                console.error('Error fetching nitrogen deposition:', error);
                handleAlerts({'success': false, 'message': 'An error occurred while fetching nitrogen deposition. Please try again.'});
            });
    };


    $('#tabSite').on('click', (event) => {
        console.log('tabSite Click')
        let params = {};
        const btnModifyParameters = event.target.closest('.modify-parameters');
        if (btnModifyParameters) {
            console.log('tabSite modify-parameters clicked');
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
                                $('#id_land_usage').append(new Option(soilProfile.landusage, soilProfile.landusage, true, true)).prop('disabled', true);
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
            conole.log('add horizon')
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

            validateSoilProfileFormset();
            markSaveNecessary(true);
        } else if (event.target.classList.contains('delete-horizon-button')) {
            console.log('delete horizon')
            markSaveNecessary(true);
            const table = $("#soil-layers-table");    
            let totalForms;
            if ($("#id_soilhorizon_set-TOTAL_FORMS").length > 0) {
                totalForms = $("#id_soilhorizon_set-TOTAL_FORMS")
            } else {totalForms = $("#id_soil_horizons-TOTAL_FORMS")};
            const currentCount = parseInt(totalForms.val(), 0);
            
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
            console.log('advanced soil parameters toggle')
            $('.advanced-soil-parameters').toggleClass('d-none');
        } else if (event.target.classList.contains('reset-soil-form-button')) {
            console.log('reset soil form button')
            const profileType = event.target.dataset.profileType;
            const profileId = event.target.dataset.profileId;
            const originalProfile = event.target.dataset.originalProfile === 'true';
            getSoilProfileFormsetHtml({profileType: profileType, profileId: profileId, originalProfile: originalProfile});
        } else if (event.target.classList.contains('save-soil-profile-button')) {
            console.log('save soil profile button')
            saveSoilProfileFormset();
        } else if (event.target.closest('button') && event.target.closest('button').classList.contains('get-auto-altitude')) {
            console.log('get auto altitude')
            const project = MonicaProject.loadFromLocalStorage();
            getAltitude(project.latitude, project.longitude);
        } else if (event.target.closest('button') && event.target.closest('button').classList.contains('get-auto-slope')) {
            console.log('get auto slope')
            const project = MonicaProject.loadFromLocalStorage();
            getSlope(project.latitude, project.longitude);
        } else if (event.target.closest('button') && event.target.closest('button').classList.contains('get-auto-n_deposition')) {
            console.log('get auto n deposition')
            const project = MonicaProject.loadFromLocalStorage();
            getNDeposition(project.latitude, project.longitude);
        } else if (event.target.closest('input') && event.target.closest('input').name === 'profile_source') {
            console.log('profile source changed')
            const project = MonicaProject.loadFromLocalStorage();
            project.profile_source = event.target.value;
            project.saveToLocalStorage();
            if (project.profile_source === 'recommended') {
                loadRecommendedSoilProfile(project, project.latitude, project.longitude);
            }
        }
        else {
            console.log('tabSite clicked but no button', event.target)
        }
    }); 
    
    $('#siteForm').on('change', (event) => {
        const project = MonicaProject.loadFromLocalStorage();
        const param = event.target.getAttribute('name');
        console.log('param', param)
        project[param] = event.target.value;
        project.saveToLocalStorage();

        if (event.target.id === 'id_latitude' || event.target.id === 'id_longitude') {
            const lat = $('#id_latitude').val();
            const lon = $('#id_longitude').val();
            if (lat && lon && project.profile_source === 'recommended') {
                loadRecommendedSoilProfile(project, lat, lon);
            }

            getAltitude(lat, lon);
            getSlope(lat, lon);
            getNDeposition(lat, lon);
        }

    });


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
        formData.append('project', JSON.stringify(project));
        console.log('Formdata ', formData)
        
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
                project.soilProfileType = 'userSoilProfile';
                project.soilProfileId = data.soil_profile_id;
                $('#id_soil_profile_name').val(data.soil_profile_name);
                $('#id_user_soil_profile_selector').empty();
                data.options.forEach(option => {
                    $('#id_user_soil_profile_selector').append(new Option(option[1], option[0], option[0] === data.soil_profile_id, option[0] === data.soil_profile_id));
                });
                $('#id_profile_source_user').prop('checked', true);
                project.profile_source = 'user';
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
        
        // try {
        //     project.longitude = $('#id_longitude').val();
        //     project.latitude = $('#id_latitude').val();
        // } catch (e) {
        //     console.log('Longitude/Latitude not found');
        // }
    
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
        // TODO should be obsolete
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
            $('.nav-link.monica').removeClass('active');
            $('#resultTab').removeClass('disabled').addClass('active').trigger('click');
            runSimulation(project);
        }  
    });

    $('#monicaStartDatePicker, #monicaEndDatePicker').on('changeDate focusout', handleDateChange);
};

function runSimulation(monicaProject) {   
    console.log('runSimulation', monicaProject);

    const spinner = $('#tabResultOverlay');
    spinner.removeClass('d-none');
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
    .finally(() => {
        //TODO: check if this is needed
        spinner.addClass('d-none');
        $('#downloadTab').removeClass('disabled');
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

function clearSoilInfoTables() {
    $('#correctedSoilProfileTableBody').empty();
    $('#originalSoilProfileTableBody').empty();
    $('#correctedSoilProfile').addClass('d-none');
}


function clearSoilModal() {
    console.log('Clear Soil Modal')
    $('#id_land_usage').empty().prop('disabled', false);
    $('#id_area_percentage').empty().prop('disabled', false);
    $('#id_system_unit').empty().prop('disabled', false);
    $('#id_soil_profile').empty();
    
    $('#div_id_soil_profile').prop('hidden', false);
    clearSoilInfoTables();
};



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
                $('#soil-profile-info-card').removeClass('d-none');
                markSaveNecessary(false);
                document
                .getElementById('soil-profile-formset-container')
                // .scrollIntoView({ behavior: 'smooth', block: 'start' });

                const isAdvanced = $('.advanced').is(':visible');
    
                if (isAdvanced) {
                    $('.advanced').show(); 
                } else {
                    $('.advanced').hide(); 
                } 
            }
            else handleAlerts(data.message);
        })
        .then(() => {
            const validProfile = validateSoilProfileFormset();
            markSaveNecessary(!validProfile);
        
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
        project.soilProfileId = $('#id_soil_profile').val();
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
    clearSoilInfoTables();
    let horizon_no = 1;
    if (soilProfile.SoilProfileParameters.length !== soilProfile.OriginalSoilProfileParameters.length) {
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
