// import { endpoint, chartDiv, crop, getChart } from "./chart_page.js";

// Function to retrieve the CSRF token from the cookies
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(cookie => cookie.startsWith('csrftoken='));
    const csrfToken = cookieValue ? cookieValue.split('=')[1] : null;
    return csrfToken;
}


const formatDatePicker = function(startDate, endDate) {
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
    $('#monicaStartDatePicker').datepicker('update', startDate);

    // Configure the end date picker
    $('#monicaEndDatePicker').datepicker('setStartDate', '02.01.2007');
    $('#monicaEndDatePicker').datepicker('setEndDate', endDate);
    $('#monicaEndDatePicker').datepicker('update', endDate);

    // Show the datepicker container
    $('#monicaDatepicker').show();
};


document.addEventListener('DOMContentLoaded', function() {
    // console.log('userFieldId', userFieldId);
    // select boxes for soil profile
    const landUsageField = document.getElementById('id_land_usage');
    const soilProfileField = document.getElementById('id_soil_profile');
    const horizonsField = document.getElementById('div_id_horizons');
    const areaPercenteageField = document.getElementById('id_area_percentage');
    const systemUnitField = document.getElementById('id_system_unit');
    // const profileText = document.getElementById('id_profile');
    const table = document.getElementById('tableHorizons');
    // const headerRow = document.getElementById('tableHorizonsHeader');

    const cropField = document.getElementById("id_Feldfrucht")
    const speciesParameters = document.getElementById('id_species_parameters');
    const cultivarParameters = document.getElementById('id_cultivar_parameters');
    const monicaStartDatePicker = document.getElementById('monicaStartDatePicker');
    const monicaEndDatePicker = document.getElementById('monicaEndDatePicker');
    formatDatePicker(startDate, endDate);

    var selectedSoilProfile = 0;

    console.log('systemUnitJson\n', systemUnitJson);
    
    

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
            headerCellHorizon.textContent = 'Horizont ' + horizon;
            
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




    // monica chart
    // const btnMonicaCalculate = document.getElementById("btnMonicaCalculate");

    // btnMonicaCalculate.addEventListener("click", function () {
    //     // project = new swnProject();
    //     getChart(soilProfileField.value, cropField.value);
    //     chartCard.classList.remove("d-none");
    //   });

    const btnMonicaCalculateDB = document.getElementById("btnMonicaCalculateDB");

    const chartDiv2 = document.getElementById("chartDiv2")
    

    btnMonicaCalculateDB.addEventListener("click", function () {
        btnMonicaCalculateDB.disabled = true;
        btnMonicaCalculateDB.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span>...wird berechnet</span>';
        
        // project = new swnProject();
        var soilProfileId = soilProfileField.value;
        var speciesId = speciesParameters.value;
        var cultivarId = cultivarParameters.value;
        var startDate = monicaStartDatePicker.value;
        var endDate = monicaEndDatePicker.value;
        var startDate = $('#monicaStartDatePicker').datepicker('getDate');
        var endDate = $('#monicaEndDatePicker').datepicker('getDate');
        var startDateStr = startDate.toLocaleDateString();
        var endDateStr = endDate.toLocaleDateString();
        
        console.log("startDate.toLocaleDateString()", startDate.toLocaleDateString());
        
        
        var requestParams = {
            userFieldId: userFieldId,
            soilProfileId: soilProfileId,
            speciesId: speciesId,
            cultivarId: cultivarId,
            startDate: startDateStr,
            endDate: endDateStr,
        };
        fetch('/monica/monica_calc_w_params_from_db/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify(requestParams),
      })
      .then(response => response.json())
      .then(data => {
        console.log(data);
        if (data.result == "success") {
            const dailyData = data.msg.daily;
            chartDiv2.innerHTML = '<canvas id="Chart"></canvas>'
            const ctx = document.getElementById("Chart")
            console.log("CHART data: ", dailyData.Mois_1)
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
            btnMonicaCalculateDB.disabled = false;
            btnMonicaCalculateDB.textContent = "Berechnen";
            console.log("CHART: ", chart);
        }
        
    });
        // const monicaCard = document.getElementById("monicaCard");
        // monicaCard.classList.remove("d-none");
        // const monicaCardText = document.getElementById("monicaCardText");
        // monicaCardText.textContent = data.message;


    });

});



