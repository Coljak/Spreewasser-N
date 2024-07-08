// Date Picker
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

var rotations = [];

class Rotation {
    constructor() {
        this.cultivar = null;
        this.sowingWorkstep = null;
        this.harvestWorkstep = [];
        this.tillageWorkstep = [];
        this.fertilizationWorkstep = [];
    }
};


document.addEventListener('DOMContentLoaded', function() {
    // //Crop and cultivar selection
    // var speciesParameters = document.getElementById('id_species_parameters');
    // var cultivarParameters = document.getElementById('id_cultivar_parameters');
    // speciesParameters.addEventListener('change', function() {
    //     var speciesId = this.value;
    //     if (speciesId) {
    //         // TODO write speciesId to cookie
    //         fetch('/monica/get_cultivar_parameters/' + speciesId + '/')
    //             .then(response => response.json())
    //             .then(data => {
    //                 console.log("DATA: ", data)
    //                 var cultivarParameters = document.getElementById('id_cultivar_parameters');
    //                 cultivarParameters.innerHTML = '';
    //                 for (var i = 0; i < data.cultivars.length; i++) {
    //                     var cultivar = data.cultivars[i];
    //                     var option = document.createElement('option');
    //                     option.value = cultivar.id;
    //                     option.textContent = cultivar.name;
    //                     cultivarParameters.appendChild(option);
    //                 }
    //             });
    
    //     } else {
    //         var cultivarParameters = document.getElementById('id_cultivar_parameters');
    //         cultivarParameters.innerHTML = '';
    //     }
    // });

    document.querySelectorAll('.add-formset').forEach(function(button) {
        button.addEventListener('click', function() {
            var prefix = this.getAttribute('data-formset-prefix');
            console.log('id_' + prefix + '-TOTAL_FORMS')
            var formCount = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
            var formCountValue = parseInt(formCount.value);
            var newForm = document.getElementById(prefix + '-empty-form').cloneNode(true);
            newForm.setAttribute('class', 'formset-row');
            newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formCountValue);
            document.querySelectorAll('.' + prefix + '-formset').appendChild(newForm);
            formCount.value = formCountValue + 1;

            $(newForm).find('.datepicker').datepicker({
                language: 'de-DE',
                format: "dd.mm.yyyy",
                weekStart: 1,
                immediateUpdates: true,
                startView: 1,
                maxViewMode: 3,
                clearBtn: true, 
                autoclose: true,
            })
            }

            )
        });

        var speciesParameters = document.getElementById('id_sowing-species');
        speciesParameters.addEventListener('change', function() {
        var speciesId = this.value;
        if (speciesId) {
            // TODO write speciesId to cookie
            fetch('/monica/get_cultivar_parameters/' + speciesId + '/')
                .then(response => response.json())
                .then(data => {
                    console.log("DATA: ", data)
                    var cultivarParameters = document.getElementById('id_sowing-cultivar');
                    cultivarParameters.innerHTML = '';
                    for (var i = 0; i < data.cultivars.length; i++) {
                        var cultivar = data.cultivars[i];
                        var option = document.createElement('option');
                        option.value = cultivar.id;
                        option.textContent = cultivar.name;
                        cultivarParameters.appendChild(option);
                    }
                    var plantDensity = document.getElementById('id_sowing-plant_density');
                    plantDensity.value = data.plant_density;
                });
    
        } else {
            var cultivarParameters = document.getElementById('id_cultivar_parameters');
            cultivarParameters.innerHTML = '';
        }
    });

        // Initialize datepicker for existing forms
        $('.datepicker').datepicker({
        format: 'dd.mm.yyyy',
        autoclose: true,
        language: 'de'
    });

    
    formatDatePicker(startDate, endDate, setStartDate, setEndDate);

    });





