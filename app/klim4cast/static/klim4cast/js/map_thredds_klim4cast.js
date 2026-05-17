import { getOrCreateLegendList, htmlLegendPlugin } from '/static/vendor/chartjs/chartjs-html-legend.js';
import {palettes, palette_min_and_max} from '/static/shared/timelapse_palettes.js';
import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, populateDropdown } from '/static/shared/utils.js';


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
document.getElementById('loadNetCDFButton').addEventListener('click', function() {
    try {
        map.timeDimension.remove();}
    catch (error) {console.log('Deleting old time dimension items failed')  }
        
    $('.info').remove();
    var netCdf = $('#datasetSelector').val();
    // var startDate = $('#startDatePicker').datepicker('getDate');
    // var endDate = $('#endDatePicker').datepicker('getDate');
    var variable = $('#netcdfVariableSelector').val();
    // console.log('startDate', startDate);
    // console.log('endDate', endDate);

    const params = {
        'netCdf': netCdf,
        'variable': variable,

    };
    console.log('params', params);
    initializeWms(params);
    map.timeDimension.setCurrentTimeIndex(0);
})

function showData (e) {
    console.log('Clicked coordinates: ', e.latlng);
    let nc = $('#datasetSelector').val();
    let variable = $('#netcdfVariableSelector').val();

    // Optionally, add a loading spinner here instead of the text message

    fetch('/klim4cast/get_point_data/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() 
        },
        body: JSON.stringify({
            'netcdf': nc,
            'param': variable,
            'lat': e.latlng.lat,
            'lon': e.latlng.lng
        })
    })
    .then(response => response.json())
    .then(data => {
        // Create the chart
        // console.log(data)
        createChart(data);
    })
    .catch(error => {
        console.error("Error fetching data: ", error);
        modalBody.innerHTML = "<p>Error loading data.</p>";
    });
};



// Function to create the base map with OpenStreetMap layer
function createBaseMap() {

    const osmUrl =
        "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

    const osmAttrib =
        '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';

    const osm = L.tileLayer(osmUrl, {
        referrerPolicy: 'strict-origin-when-cross-origin',
        maxZoom: 18,
        attribution: osmAttrib
    });

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

        center: [51.0, 10.0]
    });

    window.addEventListener('resize', () => {
        map.invalidateSize();
    });

    let clickMarker = null;

    map.on('click', function (e) {
        window.currentMapClickEvent = e;
        window.showData = showData; // Make the showData function accessible in the global scope for the button's onclick event

        // Remove old marker
        if (clickMarker) {
            map.removeLayer(clickMarker);
        }

        // Create new marker
        clickMarker = L.marker(e.latlng).addTo(map);

        // Popup HTML
        
        const popupContent = `
            <div>
                <b>Coordinates</b><br>
                Lat: ${e.latlng.lat.toFixed(4)}<br>
                Lon: ${e.latlng.lng.toFixed(4)}<br><br>

                <button
                    class="btn btn-sm btn-secondary show-data-btn"
                    onclick="showData(window.currentMapClickEvent)">
                    Show Data
                </button>
            </div>
        `;

        clickMarker.bindPopup(popupContent).openPopup();
    });

    map.addEventListener

    return map;
}



function createChart(data) {
    
    let modalTile = document.getElementById('clim4castChartTitle');
    modalTile.innerHTML = `${data.long_name} at ${data.latitude.toFixed(2)}, ${data.longitude.toFixed(2)}`;

    // Ensure that the modal is shown before attempting to create the chart
    let chartDiv = document.getElementById('clim4castChartBody');
    chartDiv.innerHTML = '<canvas id="clim4castChartCanvas"></canvas><div id="clim4castChartLegend"></div>'; // Clear previous content and add canvas for the chart
    let chartCanvas = document.getElementById('clim4castChartCanvas');
    console.log('Chartdata', data);
    // Add a small delay before creating the chart to make sure the modal (and canvas) is fully visible
    setTimeout(function() {
        const chart = new Chart(chartCanvas, {
            type: "line",
            data: {
                labels: data.dates, // the date labels
                datasets: [{
                    label: `${data.long_name} ${data.unit}`,
                    data: data.point_data,
                    borderColor: 'rgba(75, 192, 192, 1)', // Set color for the line
                    fill: false // Set whether the area under the line should be filled
                }]
            },

            plugins: [htmlLegendPlugin],
            options: {
                responsive: true,
                plugins: {
                    htmlLegend: {
                        containerID: 'clim4castChartLegend',
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
                    },
            
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
                            text: `${data.long_name} ${data.unit}`
                        }
                    }
                }
            },
        });

        chart.update();
    }, 200);  // Delay of 200ms (adjust if necessary)

};








// Function to create WMS layer
function createWMSLayer(wmsUrl, layerName) {
    const ncmlMetadata = JSON.parse(localStorage.getItem('ncmlMetadata')); 
    return L.tileLayer.wms(wmsUrl, {
        layers: layerName,
        version: "1.3.0",
        format: 'image/png',
        transparent: true,
        attribution: ncmlMetadata.title,
        tileSize: 1024,
        transparent: true,
        colorscalerange: palette_min_and_max[layerName].valueRange, // the range is set as a constant in palette_and_min_max
        abovemaxcolor: "extend",
        belowmincolor: "extend",
        numcolorbands: 100,
        styles: palette_min_and_max[layerName].style,
    });
};


// Main function to initialize the map
const map = createBaseMap();

map.timeDimension.on('availabletimeschanged', function() {
    console.log('timeloading', );
        map.timeDimension.setCurrentTimeIndex(0);
    });


// let timeDimension;
let wmsLayer;
let timeDimensionWmsLayer;



async function initializeWms(params) {
    const style = palette_min_and_max[params.variable].style;

     try {
        map.removeLayer(timeDimensionWmsLayer);
        console.log('timeDimensionWmsLayer removed');
     } catch (error) {console.log('Deleting old time dimension items failed')  }

    const wmsUrl = `/klim4cast/Timelapse/Thredds/wms/${params.netCdf}`;
    
    const colorscaleRange = palette_min_and_max[params.variable].valueRange; 
    const legendUrl = `${wmsUrl}?request=GetLegendGraphic&PALETTE=default&LAYERS=${params.variable}&transparent=TRUE&&colorscalerange=${colorscaleRange}&numcolorbands=100&styles=${style}`;

    // legendControl = createLegendControl(legendUrl);
    const legendControl = L.control({
        position: 'topright',
    });

    legendControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'info legend leaflet-bar');
        div.innerHTML += '<img src="' + legendUrl + '" alt="legend" height="200rem">';
        return div;
    };
    legendControl.addTo(map);
    // the actual WMS layer is created with the selected parameters
    wmsLayer = createWMSLayer(wmsUrl, params.variable);
    wmsLayer.addTo(map);
    try {
        timeDimensionWmsLayer =  L.timeDimension.layer.wms(wmsLayer, {
            wmsVersion: "1.3.0",
            updateTimeDimension: true,
            updateTimeDimensionMode: 'replace',
            cache: 24,
            styles:style,
        });
        
        timeDimensionWmsLayer.addTo(map);
    } catch (error) {console.log('Creating time dimension layer failed')  }
    
    
};

document.addEventListener('DOMContentLoaded', function() {

    // Get the metadata of the chosen dataset and update the variable selector
    // datasetSelector.addEventListener('change', (event) => {
        $('.input-daterange').datepicker('destroy');
        $('#netcdfVariableSelector').empty();
        
        // const dataset = event.target.value;
        const dataset = $('#datasetSelector').val();
        console.log('dataset', dataset);
        fetch(`/klim4cast/get_ncml_metadata/${dataset}`)
            .then(response => response.json())
            .then(data => {
                console.log('data', data);
                // var data_json = JSON.parse(data);
                // console.log('data_json', data_json);

                // formatting the start and end date of the dataset for the datepicker
                var formattedStartDate = dateFormatter(data.time_coverage_start_ymd);
                var formattedEndDate = dateFormatter(data.time_coverage_end_ymd);
                // formatDatePicker(formattedStartDate, formattedEndDate)

                Object.keys(data.variables).forEach(variable => {
                    console.log(variable);
                    var option = document.createElement("option");
                    option.text = data.variables[variable].attributes.description;
                    option.value = variable;
                    netcdfVariableSelector.add(option);
                });

                localStorage.setItem('ncmlMetadata', JSON.stringify(data));

            })

    // }); 
});