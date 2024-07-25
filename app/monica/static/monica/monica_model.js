
class MonicaProject {
    constructor() {
        this.name = null;
        this.description = null;
        this.longitude = null;
        this.latitude = null;
        this.startDate = null;
        this.endDate = null;
        this.rotationLength = 1;
        this.rotation = [];
    }
};

class Rotation {
    constructor(cultivar, sowingWorkstep, harvestWorkstep, tillageWorkstep, fertilizationWorkstep) {
        this.cultivar = cultivar;
        this.sowingWorkstep = sowingWorkstep;
        this.harvestWorkstep = harvestWorkstep;
        this.tillageWorkstep = tillageWorkstep;
        this.fertilizationWorkstep = fertilizationWorkstep;
    }
};

class Workstep {
    constructor(workstep, date) {
        this.workstep = workstep;
        this.date = date;
        this.options = {};
    }
};

// Date Picker
var startDate = '01.01.2007';
var setStartDate = '01.01.2007';
var endDate = '31.12.2023';

const startDatePicker = $('#monicaStartDatePicker');
const endDatePicker = $('#monicaEndDatePicker');
const longitudePicker = $('#id_longitude');
const latitudePicker = $('#id_latitude');

const formatDatePicker = function(startDate, endDate, setStartDate, setEndDate) {
    $('.input-daterange').datepicker({
        language: 'de-DE',
        format: "dd.mm.yyyy",
        startDate: startDate,
        endDate: endDate,
        weekStart: 1,
        immediateUpdates: true,
        startView: 1,
        maxViewMode: 3,
        clearBtn: true, 
        autoclose: true,
    })
    // Configure the start date picker
    $('#monicaStartDatePicker').datepicker('setStartDate', '01.01.2007');
    $('#monicaStartDatePicker').datepicker('setEndDate', endDate);
    $('#monicaStartDatePicker').datepicker('update', setStartDate);

    // Configure the end date picker
    $('#monicaEndDatePicker').datepicker('setStartDate', '02.01.2007');
    $('#monicaEndDatePicker').datepicker('setEndDate', endDate);
    $('#monicaEndDatePicker').datepicker('update', endDate);

    // Show the datepicker container
    $('#monicaDatepicker').show();
};

formatDatePicker(startDate, endDate, setStartDate, endDate);

calculateDaysInRotation = function() {
    var startDate = startDatePicker.datepicker('getDate');
    var endDate = endDatePicker.datepicker('getDate');
    var daysInRotation = (endDate - startDate) / (1000 * 60 * 60 * 24);
    var yearsInRotation = Math.ceil(daysInRotation / 365);
    return [daysInRotation, yearsInRotation];
}

var daysInRotation = 0;

  // Attach changeDate event listener using jQuery
  startDatePicker.on('changeDate', function() {
    console.log(calculateDaysInRotation()[0])
  });

  endDatePicker.on('changeDate', function() {
    console.log(calculateDaysInRotation()[1])
  });


  document.addEventListener('DOMContentLoaded', function() {

    var project = new MonicaProject();
    $('#projctName').on('change', function() {
        project.name = $(this).val();
    });

    $('#projctescription').on('change', function() {
        project.description = $(this).val();
    });

    $('#id_longitude').on('change', function() {
        project.longitude = $(this).val();
    });
    $('#id_latitude').on('change', function() {
        project.latitude = $(this).val();
    });
    $('#monicaStartDatePicker').on('changeDate', function() {
        project.startDate = $(this).datepicker('getDate');
    });
    $('#monicaEndDatePicker').on('changeDate', function() {
        project.endDate = $(this).datepicker('getDate');
    });
    $('#rotationLength').on('change', function() {
        project.rotationLength = $(this).val();
    });
    // General Settings
    // Advanced Settings:
    function toggleNMinFields() {
        var useNMin = document.getElementById("id_use_n_min_mineral_fertilising_method");
        var nMinFields = [
            "div_id_n_min_user_params_min",
            "div_id_n_min_user_params_max",
            "div_id_n_min_user_params_delay_in_days",
            "div_id_n_min_fertiliser_partition",
            "div_id_julian_day_automatic_fertilising",
        ];

        nMinFields.forEach(function(fieldId) {
            var field = document.getElementById(fieldId);
            if (useNMin.checked) {
                field.style.display = "";
            } else {
                field.style.display = "none";
            }
        });
    };
    

    document.getElementById("id_use_n_min_mineral_fertilising_method").addEventListener("change", toggleNMinFields);
    // toggleNMinFields(); 

    // Tab Rotation
    const cropRotationDiv = document.getElementById('cropRotation');

    function addRotationGui() {
        var length = project.rotation.length;
        const rotationTemplate = document.getElementById('rotationTemplate').innerHTML;
        
        const newRotation = document.createElement('div');
        newRotation.classList.add('card', 'mb-3', 'rotation');
        newRotation.setAttribute('data-rotation', (length - 1));

        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body');
        var title = 'Rotation ' + length;
        cardBody.innerHTML = `<h5 class="card-title">${title}</h5>` + rotationTemplate;
        newRotation.appendChild(cardBody);
        cropRotationDiv.appendChild(newRotation);
    };

    const addRotationButton = document.getElementById('addRotationButton');
    addRotationButton.addEventListener('click', function(){
        project.rotation.push(new Rotation());
        addRotationGui()
    });


    function addWorkstepForm(formId, addWorkstepDiv) {
        var formTemplate = document.getElementById(formId);
        var newForm = formTemplate.cloneNode(true);
        newForm.removeAttribute('id');
        if (addWorkstepDiv.parentNode) {
            addWorkstepDiv.parentNode.insertBefore(newForm, addWorkstepDiv);
        };
        newForm.scrollIntoView({behavior: 'smooth'});

    };


    // pick up all Crop Roatation related events


        // Function to bind event listeners to modal buttons
    function bindModalEventListeners() {
        console.log('bindModalEventListeners');
        const modalForm = document.getElementById('modalForm');

        document.getElementById('saveModalParameters').addEventListener('click', function () {
            submitModalForm(modalForm, false);
        });

        document.getElementById('saveAsNewModalParameters').addEventListener('click', function () {
            submitModalForm(modalForm, true);
        });
    };

    function updateDropdown(parameterType, newId){
        console.log('updateDropdown ', parameterType, newId)
        fetch('get_options/' + parameterType + '/')
        .then(response => response.json())
        .then(data =>
        {
            console.log("DATA:", data)
            var select = document.querySelector('.form-select.' + parameterType)
            select.innerHTML = ''
            data.options.forEach(option =>{
                var optionElement = document.createElement('option');
                optionElement.value = option.id;
                optionElement.text = option.name;
                select.appendChild(optionElement);
            });
            select.value =newId;

        })
        .catch(error => console.log('Error in updateDropdown', error))


    };

    function submitModalForm(modalForm, isSaveAsNew) {
        console.log('submitModalForm, isSaveAsNew:', isSaveAsNew);
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
            console.log('data', data);
            if (data.success) {
                
                $('#formModal').modal('hide')
                
                alert('Form saved successfully!');
                if (isSaveAsNew) {
                    console.log('action-url', actionUrl, data)
                    updateDropdown(actionUrl.split('/')[0], data.new_id)
                }
            } else {
                // Handle form errors (update form with error messages)
                alert('Error saving form: ' + data.errors);
            }
        })
        .catch(error => console.error('Error:', error));
    };

    // Example of how to open the modal and load content (adjust according to your specific needs)
    document.querySelectorAll('.modify-parameters-button').forEach(button => {
        button.addEventListener('click', function () {
            const url = button.getAttribute('data-url');
            loadModalContent(url);
        });
    });
    const rotationDiv = document.getElementById('cropRotation');
    // ----Rotation CLICK EVENTS ----
    rotationDiv.addEventListener('click', function(event) {
        var rotationIndex = event.target.closest('.rotation').getAttribute('data-rotation');
        // Add Workstep Button
        if (event.target.classList.contains('add-workstep-button')) {
            // var rotationIndex = event.target.closest('.rotation').getAttribute('data-rotation');
            var workstepType = event.target.closest('.rotation').querySelector('.workstep-type-select').value;
            console.log('rotationIndex', rotationIndex);
            console.log('workstepType', workstepType);
            addWorkstepForm(workstepType, event.target.closest('.rotation').querySelector('.add-workstep'));
        } else if (event.target.classList.contains('delete-rotation-button')) {
            console.log('IMPLEMENT delete rotation');
        } else if (event.target.classList.contains('delete-workstep-button')) {
            // todo implement delete workstep
        } else if (event.target.classList.contains('modify-species-parameters')) {
            var speciesId = event.target.closest('.rotation').querySelector('.species-selector').value;
            fetch('/monica/model/species_parameters/' + speciesId + '/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    document.getElementById('modalModifyParamsContent').innerHTML = data;
                    bindModalEventListeners();
                });
        } else if (event.target.classList.contains('modify-cultivar-parameters')) {
            var cultivarId = event.target.closest('.rotation').querySelector('.cultivar-selector').value;
            fetch('/monica/cultivar_parameters/' + cultivarId + '/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(data => {
                document.getElementById('modalModifyParamsContent').innerHTML = data;

            });
            console.log('cultivarId', cultivarId);
        } else if (event.target.classList.contains('modify-residue-parameters')) {
            var speciesId = event.target.closest('.rotation').querySelector('.species-selector').value;
            console.log('speciesId', speciesId);
            fetch('/monica/residue_parameters/' + speciesId + '/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(data => {
                document.getElementById('modalModifyParamsContent').innerHTML = data;
                bindModalEventListeners();
            });
        } 
    });
    // ----Rotation SELECT EVENTS ----
    rotationDiv.addEventListener('change', function(event) {
        var rotationIndex = event.target.closest('.rotation').getAttribute('data-rotation');
        //  Workstep Sowing Species and Cultivar selectors
        if (event.target.classList.contains('species-selector')) {
            var speciesId = event.target.value;
            const cultivarSelector = event.target.closest('.rotation').querySelector('.cultivar-selector');
            console.log('rotationIndex', rotationIndex);
            if (speciesId) {
                fetch('/monica/get_cultivar_parameters/' + speciesId + '/')
                    .then(response => response.json())
                    .then(data => {
                        console.log("DATA: ", data)
                        
                        cultivarSelector.innerHTML = '';
                        for (var i = 0; i < data.cultivars.length; i++) {
                            var cultivar = data.cultivars[i];
                            var option = document.createElement('option');
                            option.value = cultivar.id;
                            option.textContent = cultivar.name;
                            cultivarSelector.appendChild(option);
                        }
                    });
        
            } else {
                
                cultivarSelector.innerHTML = '';
                var option = document.createElement('option');
                option.textContent = 'No options available';
            }

        }
    });

    function fetchModalContent(url) {
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

                console.log("NEW FUNCTION USED")
            })
            .catch(error => console.error('Error:', error));
    };

    const soilDiv = document.getElementById('tabSoil');
    // ----Rotation CLICK EVENTS ----
    soilDiv.addEventListener('click', function(event) {
        if (event.target.classList.contains('modify-parameters')) {
            var targetClass = event.target.classList[3];
            var value = $('.form-select.' + targetClass).val();
            var endpoint = '/monica/model/' + targetClass + '/' + value + '/';
            fetchModalContent(endpoint);
        }
        else if (event.target.classList.contains('modify-soil-moisture-parameters')) {
            var value = $('#id_soil_moisture').val();
            fetch('/monica/model/user_soil_moisture_parameters/' + value + '/')
            .then(response => {
                console.log("Response", response)
                if(! response.ok) {
                    throw new Error('Network response was not ok');
                }
                console.log(response.text)
                return response.text();
            })
            .then(data => {
                document.getElementById('modalModifyParamsContent').innerHTML = data;
                bindModalEventListeners();
            })
        } else if (event.target.classList.contains('modify-soil-organic-parameters')) {
            var value = $('#id_soil_organic').val();
            fetch('/monica/model/user_soil_organic_parameters/' + value + '/')
            .then(response => {
                console.log("Response", response)
                if(! response.ok) {
                    throw new Error('Network response was not ok');
                }
                console.log(response.text)
                return response.text();
            })
            .then(data => {
                document.getElementById('modalModifyParamsContent').innerHTML = data;
                bindModalEventListeners();
            })
        } else if (event.target.classList.contains('modify-soil-temperature-parameters')) {
            var value = $('#id_soil_temperature').val();
            fetch('/monica/model/soil_temperature_module_parameters/' + value + '/')
            .then(response => {
                console.log("Response", response)
                if(! response.ok) {
                    throw new Error('Network response was not ok');
                }
                console.log(response.text)
                return response.text();
            })
            .then(data => {
                document.getElementById('modalModifyParamsContent').innerHTML = data;
                bindModalEventListeners();
            })
        } else if (event.target.classList.contains('modify-soil-transport-parameters')) {
            var value = $('#id_soil_transport').val();
            fetch('/monica/model/user_soil_transport_parameters/' + value + '/')
            .then(response => {
                if(! response.ok) {
                    throw new Error('Network response was not ok');
                }
                console.log(response.text)
                return response.text();
            })
            .then(data => {

                document.getElementById('modalModifyParamsContent').innerHTML = data;
                bindModalEventListeners();
            })
        } 
    });
    








  
    // ------------ NAVBAR END -----------

    $('.nav-link').on('click', function(e) {
        $('.tab-content').hide(); // Hide all tab content

        e.preventDefault();
        $('.nav-link').removeClass('active');
        $(this).addClass('active');
        
        var target = $(this).attr('href');
        $('.tab-content').hide();
        $(target).show();
    });
    

    $('.dropdown-item').on('click', function(e) {
        e.preventDefault();
        $('.dropdown-item').removeClass('active');
        $(this).addClass('active');
        
        var target = $(this).attr('href');
        $('.tab-content').hide();
        $(target).show();
    });

    $('.tab-content').hide();
    
    const nextButton = document.getElementById('nextButton');
    const previousButton = document.getElementById('previousButton');
    const tabs = document.querySelectorAll('.monica.nav-link');
    
    nextButton.addEventListener('click', function() {
        // Find the currently active tab
        const activeTab = document.querySelector('.nav-link.active');
        console.log('activeTab', activeTab);
        // Get the index of the currently active tab
        let activeIndex = Array.from(tabs).indexOf(activeTab);
        console.log('activeIndex', activeIndex);
        // Determine the index of the next tab
        let nextIndex = (activeIndex + 1) % tabs.length; // Wrap around to the first tab if at the last tab
        
        // Trigger a click on the next tab
        tabs[nextIndex].click();
    });
    previousButton.addEventListener('click', function() {
        // Find the currently active tab
        const activeTab = document.querySelector('.nav-link.active');
        console.log('activeTab', activeTab);
        // Get the index of the currently active tab
        let activeIndex = Array.from(tabs).indexOf(activeTab);
        console.log('activeIndex', activeIndex);
        // Determine the index of the next tab
        let previousIndex = ((activeIndex + tabs.length) - 1) % tabs.length; // Wrap around to the first tab if at the last tab
        console.log('previousIndex', previousIndex);
        
        // Trigger a click on the next tab
        tabs[previousIndex].click();
    });
    // ------------ NAVBAR END -----------



    var project = new MonicaProject(
        'Test Project', 
        startDatePicker.datepicker('getDate'), 
        endDatePicker.datepicker('getDate'), 
        null
    );
    project.longitude = longitudePicker.val();
    project.latitude = latitudePicker.val();
    project.startDate = startDatePicker.datepicker('getDate');
    project.endDate = endDatePicker.datepicker('getDate');
    console.log(project)

    tabs[1].click();

  });