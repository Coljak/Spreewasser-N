// Utility functions
const alertBox = document.getElementById("alert-box");

const handleAlerts = (type, msg) => {
    alertBox.innerHTML = `
            <div class="alert alert-${type} alert-dismissible " role="alert">
                    ${msg}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">
            </div>`;
    alertBox.classList.remove("d-none");
    setTimeout(() => {
        alertBox.classList.add("d-none");
    }, 5000);
};

const getCsrfToken = () => {
    return document.cookie.split("; ").find(row => row.startsWith("csrftoken=")).split("=")[1];
};

function formatDateToISO(date) {
    return date.toISOString().split('T')[0];
}

const saveToLocalStorage = (project) => {
    console.log("Saving entire project to localStorage", project);
    localStorage.setItem('project', JSON.stringify(project));
};




// // Proxy creation functions
// const createArrayProxy = (array, project) => {
//     return new Proxy(array, {
//         set: (target, property, value) => {
//             console.log('createArrayProxy set called:', target, property, value);
//             if (typeof value === 'object' && value !== null) {
//                 value = createProxy(value, project);
//             }
//             target[property] = value;
//             saveToLocalStorage(project);
//             return true;
//         }
//     });
// };

// const createProxy = (object, project) => {
//     if (Array.isArray(object)) {
//         return createArrayProxy(object, project);
//     }
//     return new Proxy(object, {
//         set: (target, property, value) => {
//             console.log('createProxy set called:', target, property, value);
//             if (value instanceof Date) {
//                 target[property] = value;
//             } else if (typeof value === 'object' && value !== null) {
//                 value = createProxy(value, project);
//             } else {
//                 target[property] = value;
//             }           
//             saveToLocalStorage(project);
//             return true;
//         }
//     });
// };

// Classes
class MonicaProject {
    constructor() {
        this.name = null;
        this.description = null;
        this.longitude = null;
        this.latitude = null;
        this.startDate = null;
        this.endDate = null;
        // this.rotation = createArrayProxy([], this);
        this.rotation = [];
    }
}

class Rotation {
    constructor(rotationIndex, project) {
        this.rotationIndex = rotationIndex;
        this.workstepIndex = 0;
        // this.sowingWorkstep = createArrayProxy([], project);
        // this.harvestWorkstep = createArrayProxy([], project);
        // this.tillageWorkstep = createArrayProxy([], project);
        // this.mineralFertilisationWorkstep = createArrayProxy([], project);
        // this.organicFertilisationWorkstep = createArrayProxy([], project);
        // this.irrigationWorkstep = createArrayProxy([], project);
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
var setStartDate = '01.01.2021';
var setEndDate = '31.12.2023';
var endDate = '31.12.2023';

const setLanguage =  (language_code)=>{
    $('.datepicker').datepicker({
        language: language_code,
        autoclose: true
    })
};


const calculateDaysInRotation = function() {
    var startDate = $('#monicaStartDatePicker').datepicker('getDate');
    var endDate = $('#monicaEndDatePicker').datepicker('getDate');
    var daysInRotation = (endDate - startDate) / (1000 * 60 * 60 * 24);
    var yearsInRotation = Math.ceil(daysInRotation / 365);
    return [daysInRotation, yearsInRotation];
}

var daysInRotation = 0;




function submitSimulationSettingsForm(action) {
    // Save the simulation settings from General Parameters tab
    var formData = new FormData(document.getElementById('simulationSettingsForm'));
    formData.append('action', action);

    fetch(saveSimulationSettingsUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
        .then(response => response.json())
        .then(data => {
            handleAlerts(data.success ? 'success' : 'warning', data.message);
            console.log('data', data);
        })
        .catch(error => console.error('Error:', error));
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
        console.log('data', data.success);
        if (data.success) {
            console.log('SUCCESS')
            $('#runSimulationButton').prop('disabled', true);
            $('#runSimulationButton').text("...Simulation running");
            // Remove 'active' class from all nav links
            $('.nav-link.monica').removeClass('active');

            $('#resultTab').removeClass('disabled').addClass('active').trigger('click');
            const dailyData = data.message.daily;
            chartDiv2.innerHTML = '<canvas id="Chart"></canvas>'
            const ctx = document.getElementById("Chart")
            console.log("CHART data: ", dailyData.Precip)
            const chart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: dailyData.Date,
                    datasets: [{
                            yAxisID: 'y',
                            label: "Bodenfeuchte 1",
                            data: dailyData.Mois_1,
                            borderColor: "#aa8800",
                            borderWidth: 2,
                        },
                        {
                            yAxisID: 'y',
                            label: "Bodenfeuchte 2",
                            data: dailyData.Mois_2,
                            borderColor: "#ccaa00",
                            borderWidth: 2,
                        },
                        {
                            yAxisID: 'y',
                            label: "Bodenfeuchte 3",
                            data: dailyData.Mois_3,
                            borderColor: "#ffcc00",
                            borderWidth: 2,
                        },
                        {
                            yAxisID: 'y1',
                            label: "LAI",
                            data: dailyData.LAI,
                            borderWidth: 2,
                            borderColor: "#00cc22",
                        },
                        {
                            type: "bar",  // Specifies the type as bar for precipitation
                            yAxisID: 'y2',  // Optional: Add a separate y-axis if needed
                            label: "Precipitation",
                            data: dailyData.Precip,
                            backgroundColor: "rgba(0, 0, 255, 0.5)",  // Semi-transparent blue
                            borderColor: "rgba(0, 0, 255, 0.7)",
                            borderWidth: 1,
                        },
                        {
                            type: "bar",  // Specifies the type as bar for precipitation
                            yAxisID: 'y2',  // Optional: Add a separate y-axis if needed
                            label: "Irrigation",
                            data: dailyData.Irrig,
                            backgroundColor: "rgba(0, 100, 255, 0.5)",  // Semi-transparent blue
                            borderColor: "rgba(0, 100, 255, 0.7)",
                            borderWidth: 1,
                        }
                    ],
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
            chartCard.classList.remove("d-none");
            chart.update();
            $('#runSimulationButton').prop('disabled', false);
            $('#runSimulationButton').text("Run Simulation");
            console.log("CHART: ", chart);
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

    const rotationTemplate = document.getElementById('rotationTemplate').innerHTML;
    const newRotation = document.createElement('div');
    newRotation.classList.add('card', 'mb-3', 'rotation');
    newRotation.setAttribute('rotation-index', rotationIndex);

    const cardBody = document.createElement('div');
    cardBody.classList.add('card-body');
    cardBody.innerHTML = `<h5 class="card-title">Rotation ${rotationIndex + 1}</h5>` + rotationTemplate;

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

const bindModalEventListeners = () => {
    try {
        const modalForm = document.getElementById('modalForm');
        document.getElementById('saveModalParameters').addEventListener('click', () => {
            submitModalForm(modalForm, false);
        });

        document.getElementById('saveAsNewModalParameters').addEventListener('click', () => {

            const nameInputModal = new bootstrap.Modal(document.getElementById('nameInputModal'));
            nameInputModal.show();


            // submitModalForm(modalForm, true);
        });
    } catch {
        console.log('no modal save buttons found');
    }
};

const updateDropdown = (parameterType, newId) => {
    fetch('get_options/' + parameterType + '/')
        .then(response => response.json())
        .then(data => {
            const select = document.querySelector('.form-select.' + parameterType);
            select.innerHTML = '';
            data.options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.id;
                optionElement.text = option.name;
                select.appendChild(optionElement);
            });
            select.value = newId;
        })
        .catch(error => console.log('Error in updateDropdown', error));
};

const submitModalForm = (modalForm, isSaveAsNew) => {
    const actionUrl = modalForm.getAttribute('data-action-url');
    const formData = new FormData(modalForm);
    if (isSaveAsNew) {
        formData.append('save_as_new', true);
    }

    fetch(actionUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#formModal').modal('hide');
                //TODO: deal with it
                alert('Form saved successfully!');
                if (isSaveAsNew) {
                    updateDropdown(actionUrl.split('/')[0], data.new_id);
                }
            } else {
                alert('Error saving form: ' + data.errors);
            }
        })
        .catch(error => console.error('Error:', error));
};

const fetchModalContent = (url) => {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
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
        handleAlerts('warning', 'Please provide a valid location');
    } else if (project.startDate === null || project.endDate === null) {
        valid = false;
        handleAlerts('warning', 'Please provide a valid date range');
    } else if (project.rotation.length === 0) {
        valid = false;
        handleAlerts('warning', 'Please provide a crop rotation');
    } else if (project.rotation.some(rotation => rotation.sowingWorkstep.some(sowingWorkstep => sowingWorkstep.date == null))) {
        valid = false;
        handleAlerts('warning', 'Please provide a sowing date for each crop');
    } else if (project.rotation.some(rotation => rotation.sowingWorkstep.some(sowingWorkstep => new Date(sowingWorkstep.date) < new Date(project.startDate) || new Date(sowingWorkstep.date) > new Date(project.endDate)))) {
        valid = false;
        handleAlerts('warning', 'Please provide a sowing date for each crop that is within your selected timeframe');
    } else if (project.rotation.some(rotation => rotation.sowingWorkstep.some(sowingWorkstep => sowingWorkstep.options.species == null))) {
        valid = false;
        handleAlerts('warning', 'Please provide a crop for each sowing workstep!');
    }
    return valid;
};

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    setLanguage('de-DE');
    $('#monicaStartDatePicker').datepicker({
        startDate: startDate,
        endDate: endDate,
    });
    $('#monicaStartDatePicker').datepicker('update', setStartDate);
    $('#monicaEndDatePicker').datepicker('update', setEndDate);


    let project = new MonicaProject();
    project.startDate = $('#monicaStartDatePicker').datepicker('getUTCDate');
    project.endDate = $('#monicaEndDatePicker').datepicker('getUTCDate');
    project.latitude = $('#id_latitude').val();
    project.longitude = $('#id_longitude').val();
    saveToLocalStorage(project);
    // project = createProxy(project, project);
    // project = loadProject(project);
    $('#toggle-mode').on('click', () => {
        $('.advanced').each(function () {
            $(this).toggle();
            $('#toggle-mode').text($(this).is(':visible') ? 'Switch to Simple Mode' : 'Switch to Advanced Mode');
        });
    });

    $('#tabGeneralParameters').on('change', function(e) {
        if (e.target.classList.contains('user-simulation-settings')) {
            project.userSimulationSettings = e.target.value;
            saveToLocalStorage(project);
        }
    });




    $('#projectName').on('change', function () {
        project.name = $(this).val();
        saveToLocalStorage(project);
    });

    $('#projectDescription').on('change', function () {
        project.description = $(this).val();
        saveToLocalStorage(project);
    });

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

    $('#btnSimulationSettingsSave').on('click', () => {
        submitSimulationSettingsForm('save');
    });

    $('#btnSimulationSettingsSaveAs').on('click', () => {
        submitSimulationSettingsForm('save_as_new');
    });

    $("#id_use_automatic_irrigation").on("change", function (event) {
        $('#automatic_irrigation_params').toggle(event.target.checked);
    });

    $("#id_use_n_min_mineral_fertilising_method").on("change", function (event) {
        $('#n_min_fertilisation_params').toggle(event.target.checked);
    });

    $('#addRotationButton').on('click', () => {
        addRotation(project);
    });

    $('#removeRotationButton').on('click', () => {
        if (project.rotation.length > 1) {
            project.rotation.pop();
            $('#cropRotation').children().last().remove();
        } else {
            handleAlerts('warning', 'You cannot have less than 1 rotation');
        }
    });

    $('#id_soil_moisture').on('change', function () {
        project.soilMoistureParameters = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_soil_organic').on('change', function () {
        project.soilOrganicParameters = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_soil_temperature').on('change', function () {
        project.soilTemperatureParameters = $(this).val();
        saveToLocalStorage(project);
    });
    $('#id_soil_temperature').on('change', function () {
        project.soilTemperatureParameters = $(this).val();
        saveToLocalStorage(project);
    });

    const cropRotationDiv = document.getElementById('cropRotation');

    cropRotationDiv.addEventListener('click', (event) => {
        const rotationIndex = event.target.closest('.rotation').getAttribute('rotation-index');
        if (event.target.classList.contains('add-workstep-button')) {
            const workstepType = event.target.closest('.rotation').querySelector('.workstep-type-select').value;
            addWorkstep(workstepType, rotationIndex, event.target.closest('.rotation').querySelector('.card-body'), project);
        } else if (event.target.classList.contains('delete-rotation-button')) {
            console.log('IMPLEMENT delete rotation');
        } else if (event.target.classList.contains('delete-workstep-button')) {
            console.log('IMPLEMENT delete workstep');
        } else if (event.target.classList.contains('modify-parameters')) {
            const targetClass = event.target.classList[3];
            const value = event.target.closest('.rotation').querySelector('.select-parameters.' + targetClass).value;
            const endpoint = '/monica/model/' + targetClass + '/' + value + '/';
            if (value != "") {
                fetchModalContent(endpoint);
                $('#formModal').modal('show');
            } else {
                event.preventDefault();
                handleAlerts('warning', 'Please select a parameter to modify');
            }
        }
        saveToLocalStorage(project);
    });

    cropRotationDiv.addEventListener('change', (event) => {
        const rotationIndex = event.target.closest('.rotation').getAttribute('rotation-index');
        
        if (event.target.classList.contains('select-parameters')) {
            const workstepIndex = event.target.getAttribute('workstep-index');
            const workstepType = event.target.getAttribute('workstep-type');
            var workstep = project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex);
        
            console.log('if select-parameters')
            const cultivarSelector = event.target.closest('.rotation').querySelector('.select-parameters.cultivar-parameters');
            const residueSelector = event.target.closest('.rotation').querySelector('.select-parameters.crop-residue-parameters');
                
            
            if (event.target.classList.contains('species-parameters')) {
                console.log('if species-parameters')
                workstep.options.species = event.target.value;
                if (event.target.value != "") {
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
                        saveToLocalStorage(project);                 

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
                            saveToLocalStorage(project);
                        });
                    };
                
            } else if (event.target.classList.contains('cultivar-parameters')) {
                console.log('cultivar-parameters changed')
                workstep.options.cultivar = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('crop-residue-parameters')) {
                console.log('crop-residue-parameters changed')
                workstep.options.cropResidue = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('organic-fertiliser-parameters')) {
                console.log('organic-fertiliser-parameters changed')
                workstep.options.organicFertiliser = event.target.value;
                // saveToLocalStorage(project);
           
            } else if (event.target.classList.contains('mineral-fertiliser-parameters')) {
                console.log('mineral-fertiliser-parameters changed')
                workstep.options.mineralFertiliser = event.target.value;
                // saveToLocalStorage(project);
            
            } else if (event.target.classList.contains('organic-fertiliser-amount')) {
                console.log('organic-fertiliser-amount changed')
                workstep.options.amount = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('mineral-fertiliser-amount')) {
                console.log('mineral-fertiliser-amount changed')
                workstep.options.amount = event.target.value;
                // saveToLocalStorage(project);
            } else if (event.target.classList.contains('irrigation-amount')) {
                console.log('irrigation-parameters changed')
                workstep.options.amount = event.target.value;
                // saveToLocalStorage(project);   
            } else {
                ;
            }
            
            console.log('Project parameters-select ', project)
            saveToLocalStorage(project);
            }
            
        
    });

    const soilDiv = document.getElementById('tabSoil');

    soilDiv.addEventListener('click', (event) => {
        if (event.target.classList.contains('modify-parameters')) {
            const targetClass = event.target.classList[3];
            const value = $('.form-select.' + targetClass).val();
            const endpoint = '/monica/model/' + targetClass + '/' + value + '/';
            fetchModalContent(endpoint);
        } else if (event.target.classList.contains('show-soil-parameters')) {
            const lon = project.longitude;
            const lat = project.latitude;
            const endpoint = '/monica/model/soil-profile/' + [lat, lon].join('/') + '/';
            fetchModalContent(endpoint);
        }
    });

    $('.nav-link.monica').on('click', function (e) {
        e.preventDefault();
        $('.nav-link.monica').removeClass('active');
        $(this).addClass('active');
        const target = $(this).attr('href');
        $('.tab-content').hide();
        $(target).show();
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
        project.longitude = $('#id_longitude').val();
        project.latitude = $('#id_latitude').val();
        project.startDate = $('#monicaStartDatePicker').datepicker('getUTCDate');
        project.endDate = $('#monicaEndDatePicker').datepicker('getUTCDate');

        if (validateProject(project)) {
            runSimulation(project);
        }
        
    });

    tabs[1].click();
    addRotation(project);
    addRotation(project);
});



