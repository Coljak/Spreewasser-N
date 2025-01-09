// Utility functions
const alertBox = document.getElementById('alert-box');

const handleAlerts = (message) => {
    console.log('handleAlerts', message);
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

const saveToLocalStorage = (project) => {
    console.log('Saving entire project to localStorage', project);
    localStorage.setItem('project', JSON.stringify(project));
};

// Classes
class MonicaProject {
    constructor() {
        this.id = null;
        this.name = null;
        this.description = null;
        this.longitude = null;
        this.latitude = null;
        this.userField = null;
        this.startDate = null;
        this.endDate = null;
        this.rotation = [];
        // settings
        this.userSimulationSettings = null;
        this.userEnvironmentParameters = null;
        this.userCropParameters = null;

        this.userSoilTemperatureParameters = null;
        this.userSoilTransportParameters = null;
        this.userSoilOrganicParameters = null;
        this.userSoilMoistureParameters = null;

        // this.soilProfileId = null;
    }
};

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

class Rotation {
    constructor(rotationIndex, project) {
        this.rotationIndex = rotationIndex;
        this.workstepIndex = 0;
        this.sowingWorkstep = [];
        this.harvestWorkstep = [];
        this.tillageWorkstep = [];
        this.mineralFertilisationWorkstep = [];
        this.organicFertilisationWorkstep = [];
        this.irrigationWorkstep = [];
    }
}

class Workstep {
    constructor(workstep, date, workstepIndex, options) {
        this.workstep = workstep;
        this.date = date;
        this.workstepIndex = workstepIndex;
        this.options = options;
    }
}

// Date Picker
var startDate = '01.01.2007';
var setStartDate = '01.01.2024';
var setEndDate = '26.11.2024';
var endDate = '26.11.2024';

const setLanguage =  (language_code)=>{
    $('.datepicker').datepicker({
        language: language_code,
        autoclose: true
    })
};





const runSimulation = (monicaProject) => {   
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
               
                'Yield': true,
                'Irrig': true,
                'organ': false,
                'AbBiom': true,
                'Mois_1': false,
                'Mois_2': false,
                'Mois_3': false,
                'SOC_1': false,
                'SOC_2': false,
                'SOC_3': false,
                'LAI': true,

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
                        label: `Moisture 0-10cm ${i}`,
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
            chartDiv.innerHTML = '<canvas id="Chart" height="80"></canvas>'
            const ctx = document.getElementById('Chart')
            // console.log('CHART data: ', dailyData.PrecipdailyData)
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
                }
            });

            // chartCard.classList.remove('d-none');
            chart.update();
            const createToggleButton = (label, datasetKey) => {
                const button = document.createElement('button');
                button.textContent = label;
                button.classList.add('btn', 'btn-secondary', 'm-1');
                button.onclick = () => {
                    const dataset = chart.data.datasets.find(ds => ds.label.includes(datasetKey));
                    if (dataset) {
                        dataset.hidden = !dataset.hidden;
                        chart.update();
                    }
                };
                return button;
            };
            
            const buttonContainer = document.createElement('div');
            Object.keys(resultOutput).forEach(key => {
                const button = createToggleButton(`Toggle ${key}`, key);
                buttonContainer.appendChild(button);
            });
            
            document.querySelector('#chartDiv').prepend(buttonContainer);


            $('#runSimulationButton').prop('disabled', false);
            $('#runSimulationButton').text('Run Simulation');
            console.log('CHART: ', chart);
        } else {
            handleAlerts('warning', data.message);
        }    
    })
    .then(() => {
        $('#resultTab').removeClass('disabled').addClass('active').trigger('click');
    });
};

const loadProject = (project) => {
    console.log('loadProject', project);
    $('#projectName').val(project.name);
    $('#projectDescription').val(project.description);
    $('#id_longitude').val(project.longitude);
    $('#id_latitude').val(project.latitude);
    $('#monicaStartDatePicker').datepicker('update', project.startDate);
    $('#monicaEndDatePicker').datepicker('update', project.endDate);
    console.log('project in loadProject', project);
    return project;
};

const addRotation = (project) => {
    const rotationIndex = project.rotation.length;
    project.rotation.push(new Rotation(rotationIndex, project));

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
    addWorkstep('sowingWorkstep', rotationIndex, cardBody, project);
    addWorkstep('harvestWorkstep', rotationIndex, cardBody, project);
    $('#cropRotation').append(newRotation);
    saveToLocalStorage(project);
};

const addWorkstep = (workstepType, rotationIndex, parentDiv, project) => {
    project.rotation[rotationIndex].workstepIndex += 1;
    const workstepIndex = project.rotation[rotationIndex].workstepIndex;
    const workstep = new Workstep(workstepType, null, workstepIndex, {});
    project.rotation[rotationIndex][workstepType].push(workstep);

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

    $(newForm).find('.workstep-datepicker').on('changeDate', function (e) {
        const rotationIndex = e.target.closest('.rotation').getAttribute('rotation-index');
        const workstepIndex = e.target.getAttribute('workstep-index');
        const workstepType = e.target.getAttribute('workstep-type');
        // const dateValue = null;
        try{
            const dateValue = $(this).datepicker('getUTCDate').toISOString().split('T')[0];
            project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex).date = dateValue;
            saveToLocalStorage(project);
        } catch {
            ;
        }    
    });

    $(newForm).find('.workstep-datepicker').on('focusout', function (e) {
        const rotationIndex = e.target.closest('.rotation').getAttribute('rotation-index');
        const workstepIndex = e.target.getAttribute('workstep-index');
        const workstepType = e.target.getAttribute('workstep-type');
        // const dateValue = null;
        try{
            const dateValue = $(this).datepicker('getUTCDate').toISOString().split('T')[0];
            project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex).date = dateValue;
        saveToLocalStorage(project);
        } catch {
            ;
        }
    });



    const addWorkstepDiv = parentDiv.querySelector('.add-workstep');
    parentDiv.insertBefore(newForm, addWorkstepDiv);
    saveToLocalStorage(project);
};

// Parameters Modal
const bindModalEventListeners = () => {

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

    try {
            // extra event listeners for the simulation settings modal
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

};

const updateDropdown = (parameterType,rotationIndex, newId) => {

    fetch('/monica/model/get_options/' + parameterType + '/')
        .then(response => response.json())
        .then(data => {
            console.log('updateDropdown', data);
            var select = document.querySelector('.form-select.' + parameterType); 
            if (rotationIndex != '') {
                const rotationDiv = document.querySelector(`div[rotation-index='${rotationIndex}']`);
                console.log('rotationDiv', `div[rotation-index='${rotationIndex}']`);
                select = rotationDiv.querySelector('.select-parameters.' + parameterType);
                console.log('select: ', select)
                console.log('updateDropdown IF');
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
    const absoluteUrl = '/monica/model/' + actionUrl;
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

const fetchModalContent = (params) => {
    const queryString = new URLSearchParams(params).toString();
    // var urlNew = `/monica/model/${params.parameters}/?${queryString}`;
    var url = '/monica/model/' + params.parameters + '/' 
    if (params.parameters_id) {
        url += params.parameters_id + '/';
    };
    if (params.rotation_index) {
        url += params.rotation_index + '/';
    };
    if (params.lon) {
        url += params.lat + '/';
        url += params.lon + '/';
    };

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok', response.text());
            }
            return response.text();
        })
        .then(data => {
            document.getElementById('modalModifyParamsContent').innerHTML = data;
            bindModalEventListeners();
        })
        .catch(error => console.error('Error:', error));
};

const validateProject = (project) => {
    var valid = true;
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

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    let project = new MonicaProject();
    if (window.location.href.split('/').includes('monica')) {
        project.swn_forecast = false;
    } else {
        project.swn_forecast = true;
    };

    setLanguage('de-DE');
    $('#monicaStartDatePicker').datepicker({
        startDate: startDate,
        endDate: endDate,
    });
    
    $('#monicaStartDatePicker').datepicker('update', setStartDate);
    $('#monicaEndDatePicker').datepicker('update', setEndDate);

    const calculateDaysInRotation = function() {
        var startDate = project.startDate;
        var endDate = project.endDate;  
        // var startDate = $('#monicaStartDatePicker').datepicker('getDate');
        // var endDate = $('#monicaEndDatePicker').datepicker('getDate');
        var daysInRotation = (endDate - startDate) / (1000 * 60 * 60 * 24);
        var yearsInRotation = Math.ceil(daysInRotation / 365);
        return [daysInRotation, yearsInRotation];
    };

    project.startDate = $('#monicaStartDatePicker').datepicker('getUTCDate');
    project.endDate = $('#monicaEndDatePicker').datepicker('getUTCDate');
    project.latitude = $('#id_latitude').val();
    project.longitude = $('#id_longitude').val();
    project.userSimulationSettings = $('#id_user_simulation_settings').val();
    project.userEnvironmentParameters = $('#id_user_environment').val();
    project.userCropParameters = $('#id_user_crop_parameters').val();
    project.userSoilTemperatureParameters = $('#id_soil_temperature').val();
    project.userSoilTransportParameters = $('#id_soil_transport').val();
    project.userSoilOrganicParameters = $('#id_soil_organic').val();
    project.userSoilMoistureParameters = $('#id_soil_moisture').val();
    project.todaysDate = $('#todaysDatePicker').datepicker('getUTCDate');
    project.name = $('#projectName').val();
    project.description = $('#projectDescription').val();
    project.userField = $('#userFieldSelect').val();


    saveToLocalStorage(project);


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
        project.todaysDate = $(this).datepicker('getUTCDate');
        saveToLocalStorage(project);
        
    });


    var advancedMode = false;
    $('.advanced').hide();
    $('#toggle-advanced-mode').on('click', function () {
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
        project.longitude = $(this).val();
        saveToLocalStorage(project);
    });

    $('#id_latitude').on('change', function () {
        project.latitude = $(this).val();
        saveToLocalStorage(project);
        
    });

    $('#monicaStartDatePicker').on('changeDate', function () {
        project.startDate = $(this).datepicker('getUTCDate');
        saveToLocalStorage(project);
        
    });

    $('#monicaEndDatePicker').on('changeDate', function () {
        project.endDate = $(this).datepicker('getUTCDate');
        saveToLocalStorage(project);
        
    });




    // TAB CROP ROTATION EVENT LISTENERS
    $('#addRotationButton').on('click', () => {
        addRotation(project);
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
        if (event.target.classList.contains('add-workstep-button')) {
            const workstepType = event.target.closest('.rotation').querySelector('.workstep-type-select').value;
            addWorkstep(workstepType, rotationIndex, event.target.closest('.rotation').querySelector('.card-body'), project);
            saveToLocalStorage(project);
        } else if (event.target.classList.contains('delete-rotation-button')) {
            console.log('IMPLEMENT delete rotation');
        } else if (event.target.classList.contains('delete-workstep-button')) {
            const workstepIndex = event.target.closest('form').getAttribute('workstep-index');
            const workstepType = event.target.closest('form').getAttribute('workstep-type');
            console.log('delete-workstep', rotationIndex, workstepIndex, workstepType);
            project.rotation[rotationIndex][workstepType] = project.rotation[rotationIndex][workstepType].filter(workstep => workstep.workstepIndex != workstepIndex);
            event.target.closest('.card').remove();
            saveToLocalStorage(project);

        } else if (event.target.classList.contains('modify-parameters')) {
            console.log('modify-parameters clicked');
            const targetClass = event.target.classList[3];
            const value = event.target.closest('.rotation').querySelector('.select-parameters.' + targetClass).value;
            const params = {
                'parameters': targetClass,
                'parameters_id': value,
                'rotation_index': rotationIndex
            }
            // const endpoint = '/monica/model/' + targetClass + '/' + value + '/' + rotationIndex + '/';
            if (value != '') {
                fetchModalContent(params);
                $('#formModal').modal('show');

            } else {
                event.preventDefault();
                handleAlerts({'success': false, 'message': 'Please select a parameter to modify'});
            }
        }
        
    });

    $('#cropRotation').on('change', (event) => {
        const rotationIndex = event.target.closest('.rotation').getAttribute('rotation-index');
        
        if (event.target.classList.contains('select-parameters')) {
            const workstepIndex = event.target.getAttribute('workstep-index');
            const workstepType = event.target.getAttribute('workstep-type');
            var workstep = project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex);
        
            const cultivarSelector = event.target.closest('.rotation').querySelector('.select-parameters.cultivar-parameters');
            const residueSelector = event.target.closest('.rotation').querySelector('.select-parameters.crop-residue-parameters');
                
            
            if (event.target.classList.contains('species-parameters')) {
                console.log('if species-parameters')
                workstep.options.species = event.target.value;
                if (event.target.value != '') {
                    fetch('/monica/model/get_options/cultivar-parameters/' + event.target.value + '/')
                    .then(response => response.json())
                    .then(data => {
                        cultivarSelector.innerHTML = '';  // Clear current options
                        data.options.forEach(option => {
                            const optionElement = document.createElement('option');
                            optionElement.value = option.id;
                            optionElement.text = option.name;
                            cultivarSelector.appendChild(optionElement);

                        
                        });  
                        workstep.options.cultivar = cultivarSelector.value
                        // saveToLocalStorage(project);                 

                    });
                

                
                    fetch('/monica/model/get_options/crop-residue-parameters/' + event.target.value + '/')
                        .then(response => response.json())
                        .then(data => {
                            residueSelector.innerHTML = '';
                            data.options.forEach(option => {
                                const optionElement = document.createElement('option');
                                optionElement.value = option.id;
                                optionElement.text = option.name;
                                residueSelector.appendChild(optionElement);
                            });
                            workstep.options.cropResidue = residueSelector.value;
                            // saveToLocalStorage(project);
                        });
                    };
                
            } else if (event.target.classList.contains('cultivar-parameters')) {
                workstep.options.cultivar = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('crop-residue-parameters')) {
                workstep.options.cropResidue = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('organic-fertiliser-parameters')) {
                workstep.options.organicFertiliser = event.target.value;
                // saveToLocalStorage(project);
           
            } else if (event.target.classList.contains('mineral-fertiliser-parameters')) {
                workstep.options.mineralFertiliser = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('organic-fertiliser-amount')) {
                workstep.options.amount = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('mineral-fertiliser-amount')) {
                workstep.options.amount = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('irrigation-amount')) {
                workstep.options.amount = event.target.value;
                // saveToLocalStorage(project);   
            } else {
                ;
            }
            console.log('Project parameters-select ', project)
            saveToLocalStorage(project);
            }
            
    });


    //TAB SOIL EVENT LISTENERS
    $('#id_soil_moisture').on('change', function () {
        project.userSoilMoistureParameters = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_soil_organic').on('change', function () {
        project.userSoilOrganicParameters = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_soil_temperature').on('change', function () {
        project.userSoilTemperatureParameters = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_soil_transport').on('change', function () {
        project.userSoilTransportParametersoilTransportParameters = $(this).val();
        saveToLocalStorage(project);
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
        }
    });

    // TAB PROJECT EVENT LISTENERS
    const loadProjectFromDB = (project_id) => {
        fetch('/monica/load-project/' + project_id + '/')
            .then(response => response.json())
            .then(data => {
                console.log('loadProjectFromDB', data);
                if (data.message.success) {
                    handleAlerts(data.message)
                    project = loadProject(data.project)
                } else {
                    handleAlerts(data.message)
                };
                // saveToLocalStorage(project);
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
    // project modal
    $('#saveProjectButton').on('click', () => {
        console.log('saveProjectButton clicked');
        // const formData = new FormData(projectModalForm);

        // in case it is a SWN project, longitude and latidude are provided from user field centroid
        try {
            project.longitude = $('#id_longitude').val();
            project.latitude = $('#id_latitude').val();
        }
        catch {
            ;
        }

        try {
            project.userField = $('#userFieldSelect').val();
        } catch {
            ;
        }

        project.name = $('#id_project_name').val();
        project.description = $('#id_project_description').val();
        project.startDate = $('#id_project_start_date').datepicker('getUTCDate');
        project.modelSetup = $('#id_project_model_setup').val();


        saveToLocalStorage(project);
        console.log('project', project);
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
                saveToLocalStorage(project);
            } else {
                handleAlerts(data.message);
            }
            
        })
    });

    $('#projectName').on('change', function () {
        project.name = $(this).val();
        saveToLocalStorage(project);
    });
    $('#projectDescription').on('change', function () {
        project.description = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_user_environment').on('change', function () {
        project.userEnvironmentParameters = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_user_crop_parameters').on('change', function () {
        project.userCropParameters = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_user_simulation_settings').on('change', function () {
        project.userSimulationSettings = $(this).val();
        saveToLocalStorage(project);
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
        console.log('runSimulationButton clicked');
        try {
            project.longitude = $('#id_longitude').val();
            project.latitude = $('#id_latitude').val();
        } catch { 
            try { 
                project.userField = $('#userFieldSelect').val();
            } catch {;}
   
        }

        project.startDate = $('#monicaStartDatePicker').datepicker('getUTCDate');
        project.endDate = $('#monicaEndDatePicker').datepicker('getUTCDate');
        project.userCropParameters = $('#id_user_crop_parameters').val();
        project.userEnvironmentParameters = $('#id_user_environment').val();
        project.userSimulationSettings = $('#id_user_simulation_settings').val();
        project.userSoilTemperatureParameters = $('#id_soil_temperature').val();
        project.userSoilTransportParameters = $('#id_soil_transport').val();
        project.userSoilOrganicParameters = $('#id_soil_organic').val();
        project.userSoilMoistureParameters = $('#id_soil_moisture').val();
        project.todaysDate = $('#todaysDatePicker').datepicker('getUTCDate');

        if (validateProject(project)) {
            runSimulation(project);
        }
        
    });

    tabs[1].click();
    addRotation(project);
});

