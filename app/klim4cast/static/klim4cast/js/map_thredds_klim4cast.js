/*
This script belongs to the timelapse page. It is using leaflet.timeDimension
https://github.com/socib/Leaflet.TimeDimension/blob/master/README.md#lcontroltimedimension
and the bootstrap datepicker https://bootstrap-datepicker.readthedocs.io/en/latest/

This javaScript is the derived from map_thredds....js in the django app swn
*/
const palettes = [ "default", "default-inv", "div-BrBG", "div-BrBG-inv", "div-BuRd", "div-BuRd-inv", "div-BuRd2", "div-BuRd2-inv", "div-PRGn", "div-PRGn-inv", "div-PiYG", "div-PiYG-inv", "div-PuOr", "div-PuOr-inv", "div-RdBu", "div-RdBu-inv", "div-RdGy", "div-RdGy-inv", "div-RdYlBu", "div-RdYlBu-inv", "div-RdYlGn", "div-RdYlGn-inv", "div-Spectral", "div-Spectral-inv", "psu-inferno", "psu-inferno-inv", "psu-magma", "psu-magma-inv", "psu-plasma", "psu-plasma-inv", "psu-viridis", "psu-viridis-inv", "seq-BkBu", "seq-BkBu-inv", "seq-BkGn", "seq-BkGn-inv", "seq-BkRd", "seq-BkRd-inv", "seq-BkYl", "seq-BkYl-inv", "seq-BlueHeat", "seq-BlueHeat-inv", "seq-Blues", "seq-Blues-inv", "seq-BuGn", "seq-BuGn-inv", "seq-BuPu", "seq-BuPu-inv", "seq-BuYl", "seq-BuYl-inv", "seq-GnBu", "seq-GnBu-inv", "seq-Greens", "seq-Greens-inv", "seq-Greys", "seq-Greys-inv", "seq-GreysRev", "seq-GreysRev-inv", "seq-Heat", "seq-Heat-inv", "seq-OrRd", "seq-OrRd-inv", "seq-Oranges", "seq-Oranges-inv", "seq-PuBu", "seq-PuBu-inv", "seq-PuBuGn", "seq-PuBuGn-inv", "seq-PuRd", "seq-PuRd-inv", "seq-Purples", "seq-Purples-inv", "seq-RdPu", "seq-RdPu-inv", "seq-Reds", "seq-Reds-inv", "seq-YlGn", "seq-YlGn-inv", "seq-YlGnBu", "seq-YlGnBu-inv", "seq-YlOrBr", "seq-YlOrBr-inv", "seq-YlOrRd", "seq-YlOrRd-inv", "seq-cubeYF", "seq-cubeYF-inv", "x-Ncview", "x-Ncview-inv", "x-Occam", "x-Occam-inv", "x-Rainbow", "x-Rainbow-inv", "x-Sst", "x-Sst-inv",]

// in this object, defaults are set for the color palette and the min and max values for the color scale. This can be moved to the thredds server metadata, but has to be modified theer for each dataset
const palette_and_min_max = {
    //  hurs is %
    'hurs': {
        'style': 'default-scalar/default-inv',
        'valueRange': '0, 100',
    },
    'pr': {
        'style': 'default-scalar/default-inv',
        'valueRange': '0, 200',
    },
    'rsds': {
        'style': 'default-scalar/seq-Heat-inv',
        'valueRange': '0, 10000',
    },
    'sfcWind': {
        'style': 'default-scalar/seq-Heat',
        'valueRange': '0, 30',
    },
    'tas': {
        'style': 'default-scalar/div-RdYlBu-inv',
        'valueRange': '-30, 30',
    },
    'tasmax': {
        'style': 'default-scalar/div-RdYlBu-inv',
        'valueRange': '-25, 42',
    },
    'tasmin': {
        'style': 'default-scalar/div-RdYlBu-inv',
        'valueRange': '-30, 40',
    },
    'AWD_0-40cm': {
        'style': 'default-scalar/div-BrBG',
        'valueRange': '-80, 80',
    },
    'AWD_0-100cm': {
        'style': 'default-scalar/div-BrBG',
        'valueRange': '-80, 80',
    },
    'AWD_0-200cm': {
        'style': 'default-scalar/div-BrBG',
        'valueRange': '-80, 80',
    },
    'AWP_0-40cm': {
        'style': 'default-scalar/seq-Heat-inv',
        'valueRange': '0, 100',
    },
    'AWP_0-100cm': {
        'style': 'default-scalar/seq-Heat-inv',
        'valueRange': '0, 100',
    },
    'AWP_0-200cm': {
        'style': 'default-scalar/seq-Heat-inv',
        'valueRange': '0, 100',
    },
    'AWR_0-40cm': {
        'style': 'default-scalar/div-BrBG',
        'valueRange': '0, 100',
    },
    'AWR_0-100cm': {
        'style': 'default-scalar/div-BrBG',
        'valueRange': '0, 100',
    },
    'AWR_0-200cm': {
        'style': 'default-scalar/div-BrBG',
        'valueRange': '0, 100',
    },
    'DFM10H': {
        'style': 'default-scalar/div-RdYlGn-inv',
        'valueRange': '0, 100',
    },
    'FWI_GenZ': {
        'style': 'default-scalar/div-RdYlBu-inv',
        'valueRange': '1, 6',
    },
    'HI': {
        'style': 'default-scalar/seq-Heat-inv',
        'valueRange': '0, 60',
    },    
    'UTCI': {
        'style': 'default-scalar/seq-Heat-inv',
        'valueRange': '0, 60',
    },
};


var ncmlMetadata;



// Format the yyyy-mm-dd date to dd/mm/yyyy as required for the bootstrap-datepicker
const dateFormatter = function(date) {
    var components = date.split('-');
    var formattedDate = components[2] + '/' + components[1] + '/' + components[0];
    console.log('Formatted Date: ', date, formattedDate)
    return formattedDate;
};

// initialize the datepickers with the start and end date of the dataset - datepicker runs with jQuery
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
    });
    $('#startDatePicker').datepicker('update', startDate);
    $('#endDatePicker').datepicker('update', endDate);
    $('#datepicker').show()
};


// Get selected parameters and load the netCDF file
loadNetCDFButton.addEventListener('click', function() {
    try {
        map.timeDimension.remove();}
    catch (error) {console.log('Deleting old time dimension items failed')  }
        
    $('.info').remove();
    var netCdf = datasetSelector.value;
    var startDate = $('#startDatePicker').datepicker('getDate');
    var endDate = $('#endDatePicker').datepicker('getDate');
    var variable = netcdfVariableSelector.value;
    console.log('startDate', startDate);
    console.log('endDate', endDate);
    let style = palette_and_min_max[variable].style;
    params = {
        'netCdf': netCdf,
        'variable': variable,
        'startDate': startDate,
        'endDate': endDate,
        'style': style,
        'colorerscaleRange': palette_and_min_max[variable].valueRange,
        'attribution': ncmlMetadata.global_attributes.title,
    };
    console.log('params', params);
    initializeWms(params);
    map.timeDimension.setCurrentTimeIndex(0);
})





// Function to create the base map with OpenStreetMap layer
function createBaseMap() {
    const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    const osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
    const osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib });

    const map = L.map('map', {
        zoom: 5,
        layers: [osm],
        timeDimension: true,
        timeDimensionControl: true,
        timeDimensionControlOptions: {
            position: 'bottomleft',
            autoPlay: true,
            playerOptions: {
                buffer: 10,
                transitionTime: 1000,
                loop: true,
                startOver: false,
            },
        },
        contextmenu: true,
        contextmenuWidth: 140,
        contextmenuItems: [
            {
            text: 'Show coordinates',
            callback: showCoordinates
        },
        {
            text: 'Show data',
            callback: showData
        }],
        center: [51.0, 10.0]
    });

    return map;
};
function showCoordinates (e) {
    alert(`Länge: ${e.latlng.lat}, Breite: ${e.latlng.lng}`);
};

function createChart(data) {
    
    let modalTile = document.getElementById('clim4castChartTitle');
    modalTile.innerHTML = `${data.long_name} at ${data.latitude.toFixed(2)}, ${data.longitude.toFixed(2)}`;

    // Ensure that the modal is shown before attempting to create the chart
    let chartDiv = document.getElementById('clim4castChartDiv');
    console.log(chartDiv);

  

    // Add a small delay before creating the chart to make sure the modal (and canvas) is fully visible
    setTimeout(function() {
        const chart = new Chart(chartDiv, {
            type: "line",
            data: {
                labels: data.dates, // the date labels
                datasets: [{
                    label: `${data.long_name} ${data.units}`,
                    data: data.values,
                    borderColor: 'rgba(75, 192, 192, 1)', // Set color for the line
                    fill: false // Set whether the area under the line should be filled
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right' // Position of the legend
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        labels: data.dates, // the dates as labels on the x-axis
                        title: {
                            display: true,
                            text: 'Dates'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: `${data.units}`
                        }
                    }
                }
            },
        });

        chart.update();
    }, 200);  // Delay of 200ms (adjust if necessary)

};



function showData (e) {
    let nc = datasetSelector.value;
    let variable = netcdfVariableSelector.value;

    // Optionally, add a loading spinner here instead of the text message

    fetch(`/klim4cast/get_data/${nc}/${variable}/${e.latlng.lat}/${e.latlng.lng}`)
    .then(response => response.json())
    .then(data => {
        console.log('data', data);

        // Create the chart
        createChart(data);

        // Hide the loading message and show the modal
        
    })
    .catch(error => {
        console.error("Error fetching data: ", error);
        modalBody.innerHTML = "<p>Error loading data.</p>";
    });
};




// Function to create WMS layer
function createWMSLayer(wmsUrl, layerName,  style) {

    return L.tileLayer.wms(wmsUrl, {
        layers: layerName,
        version: "1.3.0",
        format: 'image/png',
        transparent: true,
        attribution: ncmlMetadata.global_attributes.title,
        tileSize: 1024,
        transparent: true,
        colorscalerange: palette_and_min_max[layerName].valueRange, // the range is set as a constant in palette_and_min_max
        abovemaxcolor: "extend",
        belowmincolor: "extend",
        numcolorbands: 100,
        styles: style,
    });
};


// Function to create legend control. the div gets the image directly from the WMS server
function createLegendControl(legendUrl) {
    const legendControl = L.control({
        position: 'topright',
    });

    legendControl.onAdd = function(map) {
        const src = legendUrl;
        const div = L.DomUtil.create('div', 'info legend leaflet-bar');
        div.innerHTML += '<img src="' + src + '" alt="legend" height="200rem">';
        return div;
    };

    return legendControl;
};

// Main function to initialize the map
const map = createBaseMap();
map.addEventListener('click', function(e) {
    console.log('MAP CLICKED');
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    console.log('You clicked the map at: ' + lat + ', ' + lng);
});
map.timeDimension.on('availabletimeschanged', function() {
    console.log('timeloading', );
        map.timeDimension.setCurrentTimeIndex(0);
    });


// let timeDimension;
let wmsLayer;
let timeDimensionWmsLayer;
let legendControl;


async function initializeWms(params) {
    console.log('InitializeWms params', params);

     try {
        map.removeLayer(timeDimensionWmsLayer);
        console.log('timeDimensionWmsLayer removed');
     } catch (error) {console.log('Deleting old time dimension items failed')  }

    const wmsUrl = `/klim4cast/Timelapse/Thredds/wms/${params.netCdf}`;
    
    const colorscaleRange = palette_and_min_max[params.variable].valueRange;
    const attribution = ncmlMetadata.global_attributes.title;    
    const legendUrl = `${wmsUrl}?request=GetLegendGraphic&PALETTE=default&LAYERS=${params.variable}&transparent=TRUE&&colorscalerange=${colorscaleRange}&numcolorbands=100&styles=${params.style}`;

    legendControl = createLegendControl(legendUrl);
    legendControl.addTo(map);
    // the actual WMS layer is created with the selected parameters
    wmsLayer = createWMSLayer(wmsUrl, params.variable, params.style);
    wmsLayer.addTo(map);
    try {
        timeDimensionWmsLayer =  L.timeDimension.layer.wms(wmsLayer, {
            wmsVersion: "1.3.0",
            updateTimeDimension: true,
            updateTimeDimensionMode: 'replace',
            cache: 24,
            styles: params.style,
        });
        
        timeDimensionWmsLayer.addTo(map);
    } catch (error) {console.log('Creating time dimension layer failed')  }
    
    
};

document.addEventListener('DOMContentLoaded', function() {

    // Get the metadata of the chosen dataset and update the variable selector
    // datasetSelector.addEventListener('change', (event) => {
        $('.input-daterange').datepicker('destroy');
        netcdfVariableSelector.innerHTML = '';
        
        // const dataset = event.target.value;
        const dataset = datasetSelector.value;
        console.log('dataset', dataset);
        fetch(`/klim4cast/get_ncml_metadata/${dataset}`)
            .then(response => response.text())
            .then(data => {
                console.log('data', data);
                var data_json = JSON.parse(data);
                console.log('data_json', data_json);

                // formatting the start and end date of the dataset for the datepicker
                var formattedStartDate = dateFormatter(data_json.global_attributes.time_coverage_start_ymd);
                var formattedEndDate = dateFormatter(data_json.global_attributes.time_coverage_end_ymd);
                // formatDatePicker(formattedStartDate, formattedEndDate)

                Object.keys(data_json.variables).forEach(variable => {
                    console.log(variable);
                    var option = document.createElement("option");
                                    option.text = data_json.variables[variable].attributes.description;
                                    option.value = variable;
                                    netcdfVariableSelector.add(option);
                });
                var selectedVariable = netcdfVariableSelector.value;

                attribution = data_json.variables[selectedVariable].attributes.long_name;
                ncmlMetadata = data_json;


                return data;
            })

    // }); 
});