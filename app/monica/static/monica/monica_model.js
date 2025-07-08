import { MonicaCalculation, MonicaProject, Rotation, Workstep,  loadProjectFromDB, loadProjectToGui, handleDateChange, addWorkstepToGui, addRotationToGui } from '/static/monica/monica.js';
import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown, populateDropdown,  setLanguage, addToDropdown } from '/static/shared/utils.js';

function formatDateToISO(date) {
    return date.toISOString().split('T')[0];
}


function createChartDataset() {

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
            backgroundColor: 'rgba(0, 0, 255, 0.5)',  // Semi-transparent blue
            borderColor: 'rgba(0, 0, 255, 0.7)',
            borderWidth: 1,
        })
    }
    for (let i = 0; i < listOfResults.length; i++) {
        console.log(i);
        var msg = listOfResults[i].daily
        
        if (resultOutput.Yield) {
            datasets.push({
                yAxisID: 'y2',
                label: `${resultTranslation.Yield} ${i}`,
                data: msg.Yield,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.AbBiom) {
            datasets.push({
                yAxisID: 'y2',
                label: `${resultTranslation.AbBiom} ${i}`,
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
                label: `${resultTranslation.Irrig} ${i}`,
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
                label: `${resultTranslation.organ} ${i}`,
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
                label: `${resultTranslation.PASW_AVG} ${i}`,
                data: msg.PASW_AVG,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        // if (resultOutput.PASW_2) {
        //     datasets.push({
        //         yAxisID: 'y4',
        //         label: `${resultTranslation.PASW_2} ${i}`,
        //         data: msg.PASW_2,
        //         borderWidth: 2,
        //         borderColor: colors[i],
        //         pointHitRadius: 10,
        //     });
        // };
        // if (resultOutput.PASW_3) {
        //     datasets.push({
        //         yAxisID: 'y4',
        //         label: `${resultTranslation.PASW_3} ${i}`,
        //         data: msg.PASW_3,
        //         borderWidth: 2,
        //         borderColor: colors[i],
        //         pointHitRadius: 10,
        //     });
        // };
        // if (resultOutput.PASW_4) {
        //     datasets.push({
        //         yAxisID: 'y4',
        //         label: `${resultTranslation.PASW_4} ${i}`,
        //         data: msg.PASW_4,
        //         borderWidth: 2,
        //         borderColor: colors[i],
        //         pointHitRadius: 10,
        //     });
        // };
        // if (resultOutput.PASW_5) {
        //     datasets.push({
        //         yAxisID: 'y4',
        //         label: `${resultTranslation.PASW_5} ${i}`,
        //         data: msg.PASW_5,
        //         borderWidth: 2,
        //         borderColor: colors[i],
        //         pointHitRadius: 10,
        //     });
        // };
        if (resultOutput.Mois_1) {
            datasets.push({
                yAxisID: 'y3',
                label: `${resultTranslation.Mois_1} ${i}`,
                data: msg.Mois_1,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.Mois_2) {
            datasets.push({
                yAxisID: 'y3',
                label: `${resultTranslation.Mois_2} ${i}`,
                data: msg.Mois_2,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.Mois_3) {
            datasets.push({
                yAxisID: 'y3',
                label: `${resultTranslation.Mois_3} ${i}`,
                data: msg.Mois_3,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.SOC_1) {
            datasets.push({
                yAxisID: 'y4',
                label: `${resultTranslation.SOC_1} ${i}`,
                data: msg.SOC_1,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.SOC_2) {
            datasets.push({
                yAxisID: 'y4',
                label: `${resultTranslation.SOC_2} ${i}`,
                data: msg.SOC_2,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.SOC_3) {
            datasets.push({
                yAxisID: 'y4',
                label: `${resultTranslation.SOC_3} ${i}`,
                data: msg.SOC_3,
                borderWidth: 2,
                borderColor: colors[i],
                pointHitRadius: 10,
            });
        };
        if (resultOutput.LAI) {
            datasets.push({
                yAxisID: 'y5',
                label: `${resultTranslation.LAI} ${i}`,
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
return datasets;
}


const runSimulation = (monicaProject) => {   
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
            $('#runSimulationButton').text('Run Simulation');

        } else {
            handleAlerts(data.message);
            $('#runSimulationButton').prop('disabled', false);
            $('#runSimulationButton').text('Run Simulation');
        }    
    })
    .then(() => {
        //TODO: check if this is needed
        $('#resultTab').removeClass('disabled').addClass('active').trigger('click');
    });
};

window.isLoading = false;




// creates the rotation divs and adds the worksteps from the project






// Parameters Modal
const bindModalEventListeners = (parameters) => {
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
    } else if (parameters === 'recommended-soil-profile') {
        console.log("bindModalEventListeners recommended-soil-profile");
        $('#btnSelectPreselectedSoilProfile').on('click', function (e) {
            const project = MonicaProject.loadFromLocalStorage();
            project.soilProfileId = e.target.getAttribute('data-soil-profile-id');
            project.soilProfileType = "buekSoilProfile";
            project.saveToLocalStorage();
        });
    }
};

// TODO addToDropdown instead of updateDropdown
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

const submitModalForm = (modalForm, modalAction) => {
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

let modalInitialized = false;


// TODO refactor initiaizeSoilModal
// TODO implement getSoilProfiles for swn - all poygon ids
// const initializeSoilModal = function (polygonIds, userFieldId, systemUnitJson, landusageChoices) {
//     console.log('initializeSoilModal',   systemUnitJson, landusageChoices);
//     if (modalInitialized) return;
//     modalInitialized = true;
//     const landUsageField = document.getElementById('id_land_usage');
//     const soilProfileField = document.getElementById('id_soil_profile');
//     const horizonsField = document.getElementById('div_id_horizons');
//     const areaPercenteageField = document.getElementById('id_area_percentage');
//     const systemUnitField = document.getElementById('id_system_unit');
//     const table = document.getElementById('tableHorizons');

//     let selectedSoilProfile = 0;

//     soilProfileField.addEventListener('change', function() {
        
//         const selectedLandUsage = landUsageField.value;
//         const selectedSystemUnit = systemUnitField.value;
//         const selectedAreaPercenteage = areaPercenteageField.value;
//         selectedSoilProfile = soilProfileField.value;
        
        
//         const horizons = systemUnitJson[selectedLandUsage][selectedSystemUnit]['soil_profiles'][selectedAreaPercenteage][selectedSoilProfile]['horizons'];
//         horizonsField.innerHTML = '<p class="text-start">Landuse: ' + selectedLandUsage + '</br>System unit: ' + selectedSystemUnit + '</br>Area percentage: ' + selectedAreaPercenteage + '</br>Soil profile: ' + selectedSoilProfile + '</p>';
//         table.innerHTML = '';
//         const headerRow = table.insertRow();
//         headerRow.classList.add("table-dark")
//         const headerCell = headerRow.insertCell();
        
//         headerCell.textContent = 'Horizonte';
//         for (let horizon in horizons) {
//             const headerCellHorizon = headerRow.insertCell();
//             headerCellHorizon.textContent = horizon;
//         }
//         for (let key in horizons[1]) {
//             const dataRow = table.insertRow();
//             const dataRowHeaderCell  = dataRow.insertCell();
//             dataRowHeaderCell.classList.add("table-dark")
//             for (let horizon in horizons) {
//                 dataRowHeaderCell.textContent = key;
//                 const dataRowDataCell  = dataRow.insertCell();
//                 let value = horizons[horizon][key];
//                 if (typeof(value) === 'number') {
//                     value = value.toFixed(2);
//                 }
//                 dataRowDataCell.textContent = value;   
//             } 
//         }
//     });

//     // Populate soil profile and area percenteage when land usage changes
//     areaPercenteageField.addEventListener('change', function() {
//         console.log('areaPercenteageField change event')
//         const selectedLandUsage = landUsageField.value;
//         const selectedSystemUnit = systemUnitField.value;
//         const selectedAreaPercenteage = areaPercenteageField.value;

//         const selectableSoilProfiles =  systemUnitJson[selectedLandUsage][selectedSystemUnit]['soil_profiles'][selectedAreaPercenteage];
//         console.log('selectableSoilProfiles', selectableSoilProfiles);

//         const profileOptions = new Object();
//         let profileNo = 1;
//         for (let soilprofile_id in selectableSoilProfiles) {
            
//             profileOptions[soilprofile_id] = 'Profil ' + profileNo;
//             profileNo++;
//         };
//         // console.log('profileOptions', profileOptions);
//         soilProfileField.innerHTML = '';
//         for (const key in profileOptions) {
//             const option = document.createElement('option');
//             option.value = key;
//             option.text = profileOptions[key];
//             soilProfileField.appendChild(option);
//         };
//         soilProfileField.dispatchEvent(new Event('change'));
    
//     });

//     systemUnitField.addEventListener('change', function() {
//         console.log('systemUnitField change event');
//         const selectedLandUsage = landUsageField.value;
//         const selectedSystemUnit = systemUnitField.value;
//         const selectableAreaPercentages =  systemUnitJson[selectedLandUsage][selectedSystemUnit]['area_percentages'].reverse();
//         areaPercenteageField.innerHTML = '';
//         selectableAreaPercentages.forEach(item => {
//             areaPercenteageField.appendChild(new Option(item));
//         });
//         areaPercenteageField.dispatchEvent(new Event('change'));
//     });

//     landUsageField.addEventListener('change', function(){
//         console.log('landUsageField change event')
//         const selectedLandUsage = landUsageField.value;
        
//         const selectableSystemUnits =  new Array()
//         for (let [key, value] of Object.entries(systemUnitJson[selectedLandUsage])){
//             if (!selectableSystemUnits.includes(key)){
//                 selectableSystemUnits.push(key);
//             }}
//             selectableSystemUnits.sort();
//         systemUnitField.innerHTML = '';
//         selectableSystemUnits.forEach(item => {
//             systemUnitField.appendChild(new Option(item));
//         });
//         // trigger change event to update system unit
//         systemUnitField.dispatchEvent(new Event('change'));
//         // console.log('selectableSystemUnits', selectableSystemUnits.sort());
//     });

//     landUsageField.innerHTML = ''; // Clear existing options

//     for (const key in landusageChoices) {
//         const option = document.createElement('option');
//         option.value = key;
//         option.text = landusageChoices[key];
//         landUsageField.appendChild(option);
//     }
    
//     landUsageField.dispatchEvent(new Event('change'));

//     const btnSelectSoilProfile = document.getElementById("btnSelectSoilProfile");
//     btnSelectSoilProfile.addEventListener("click", function () {      
//         const project = MonicaProject.loadFromLocalStorage();
//         project.soilProfileType = "buekSoilProfile";
//         project.soilProfileId = soilProfileField.value;
//         // console.log('project.soilProfileId', project.soilProfileId);
//         project.saveToLocalStorage();
//     });

// };

const initializeSoilModal = function (polygonIds, userFieldId, systemUnitJson, landusageChoices) {
    console.log('initializeSoilModal',   systemUnitJson, landusageChoices);
    if (modalInitialized) return;
    modalInitialized = true;
    const landUsageField = document.getElementById('id_land_usage');
    const soilProfileField = document.getElementById('id_soil_profile');
    const horizonsField = document.getElementById('div_id_horizons');
    const areaPercenteageField = document.getElementById('id_area_percentage');
    const systemUnitField = document.getElementById('id_system_unit');
    const table = document.getElementById('tableHorizons');

    let selectedSoilProfile = 0;

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
        // console.log('profileOptions', profileOptions);
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
        const selectableAreaPercentages =  systemUnitJson[selectedLandUsage][selectedSystemUnit]['area_percentages'].reverse();
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
        // console.log('selectableSystemUnits', selectableSystemUnits.sort());
    });

    landUsageField.innerHTML = ''; // Clear existing options

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
        project.soilProfileType = "buekSoilProfile";
        project.soilProfileId = soilProfileField.value;
        // console.log('project.soilProfileId', project.soilProfileId);
        project.saveToLocalStorage();
    });

};


const createModal = (params) => {
    console.log('create modal', params)
    try {

        let url = '/monica/' + params.parameters + '/';
        if (params.parameters_id) {
            url += params.parameters_id + '/';
        }
        if (params.rotation_index) {
            url += params.rotation_index + '/';
        }
        if (params.parameters === 'recommended-soil-profile') {
            if (window.location.pathname.endsWith('/drought/')) {
                url = `/drought/${params.parameters}/${params.profile_landusage}/${params.user_field}/`;
                console.log(url)
            } else {
                url = `/monica/${params.parameters}/${params.profile_landusage}/`;
            }
        }
        else if (params.parameters === 'select-soil-profile') {
            if (window.location.pathname.endsWith('/drought/')) {
                url = `/drought/${params.parameters}/${params.user_field}/`;
                console.log(url)
            } else {
                url = `/monica/${params.parameters}/${params.lat}/${params.lon}/`;
            }
        }
        else if (params.lon) {
            url += params.lat + '/' + params.lon + '/';
        }

        // Fetch the content
   

        if (params.parameters === 'select-soil-profile') {
            fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('createModal select-soil-profile', data);
                
                const polygonIds = data.polygon_ids;
                const systemUnitJson = JSON.parse(data.system_unit_json);
                const landUsageChoices = JSON.parse(data.landusage_choices);
                initializeSoilModal(polygonIds, null, systemUnitJson, landUsageChoices);
                $('#modalManualSoilSelection').modal('show');
                $('#modalManualSoilSelection').on('hidden.bs.modal', function () {
                    modalInitialized = false;
                });
 
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
                $('#formModal').modal('show'); 
            })
            .catch(error => console.error('Error:', error));
        }   

         
    } catch (error) {
        console.error('Error:', error);
    }
};




const validateProject = (project) => {
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
                document.querySelector('#projectName').focus()
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
// var project = new MonicaProject();
// Event listeners
var language = 'de-DE'
document.addEventListener('DOMContentLoaded', () => {
    setLanguage(language);
    
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
            'Precip': true,
            'Yield': true,
            'Irrig': true,
            // 'organ': false,
            'AbBiom': true,
            'PASW_AVG': true,
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

    document.getElementById('btnOutputSettingsApply').addEventListener('click', function () {
        // the selection of output parameters got changed so the graph needs to be reloaded
        createChartDataset();
    });
    

    $('#todaysDatePicker').datepicker('update', new Date());
    $('#todaysDatePicker').trigger('focusout'); // saving the todays date to the project
    document.getElementById('monica-project-save').addEventListener('click', function () {
        console.log('monica-project-save clicked');
        const project = MonicaProject.loadFromLocalStorage();
        if (validateProject(project)) {
            saveProject(project);
        } 
      });

    const calculateDaysInRotation = function() {
        var startDate = project.startDate;
        var endDate = project.endDate;  

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
        $('.tab-pane').hide();
        $(target).show();
    });


    
    
    // Attach both events to both elements
    $('#monicaStartDatePicker, #monicaEndDatePicker').on('changeDate focusout', handleDateChange);
  


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
            
            project.addWorkstep(workstepType, null, rotationIndex);
            // addWorkstepToGui(workstepType, rotationIndex, project.rotation[rotationIndex].workstepIndex, event.target.closest('.rotation').querySelector('.card-body'));
            addWorkstepToGui(workstepType, rotationIndex, project.rotation[rotationIndex].workstepIndex);
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
        if (!window.isLoading) {
        console.log("EvenLister cropRotation change")
        const rotationIndex = event.target.closest('.rotation').getAttribute('rotation-index');
        
        const workstepIndex = event.target.getAttribute('workstep-index');
        const workstepType = event.target.getAttribute('workstep-type');
        const name = event.target.getAttribute('name');
        console.log('crop rotation change', rotationIndex, workstepIndex, workstepType);

        const project = MonicaProject.loadFromLocalStorage();
        var workstep = project.rotation[rotationIndex][workstepType].find(workstep => workstep.workstepIndex == workstepIndex);
        
        console.log('workstep...on change:', rotationIndex, workstepIndex, workstepType, name);

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

    $('#tabSoil').on('click', (event) => {
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
        } else if (event.target.classList.contains('recommended-soil-profile')) {
            const project = MonicaProject.loadFromLocalStorage();
            if (window.location.pathname.endsWith('/drought/') && project.userField) {
                try {
                params = {
                    'parameters': 'recommended-soil-profile',
                    'profile_landusage': 'general',
                    'user_field': project.userField,
                    
                }
                createModal(params);
                // $('#formModal').modal('show');
                } catch {
                    handleAlerts({'success': false, 'message': 'Please provide a valid location'});
                }
            } else if (window.location.pathname.endsWith('/monica/')) {
                try {
                    params = {
                        'parameters': 'recommended-soil-profile',
                        'profile_landusage': 'general',
                        'lon': project.longitude,
                        'lat': project.latitude
                    }
                    
                    createModal(params);
                    // $('#formModal').modal('show');
                } catch {
                    handleAlerts({'success': false, 'message': 'Please provide a valid location'});
                }

            }

        

        } else if (event.target.classList.contains('manually-select-soil-parameters')) {
            const project = MonicaProject.loadFromLocalStorage();
            try {
                params = {
                'parameters': 'select-soil-profile',
                'user_field': project.userField,
                'lon': project.longitude,
                'lat': project.latitude
            }
            
            createModal(params);
            } catch {
                handleAlerts({'success': false, 'message': 'Please provide a valid location'});
            }
            
        }
    });

    // TAB PROJECT EVENT LISTENERS




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
                projectModalForm.reset();
                $('#monicaProjectModal').find('.modal-title').text('Create new project');
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
  

    $('#saveProjectButton').on('click', () => {
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
                project.id = data.project_id;
                $('#project-info').find('.card-title').text('Project '+ data.project_name);
                updateDropdown('monica-project', '', data.project_id);
                handleAlerts(data.message);
                
                projectModalForm.reset();
                
                $('#monicaProjectModal').modal('hide');
                project.saveToLocalStorage();
            } else {
                handleAlerts(data.message);
            }
        });
    });
    

    $('#projectName').on('change', function () {
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

    $('.tab-pane').hide();

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
    
    // const getDefaultProject = () => {

    // };

    let project = new MonicaProject(defaultProject);
    project.saveToLocalStorage();
    
    loadProjectToGui(project);
});

