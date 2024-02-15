/*
This script belongs to the timelapse page. It is using leaflet.timeDimension
https://github.com/socib/Leaflet.TimeDimension/blob/master/README.md#lcontroltimedimension
and the bootstrap datepicker https://bootstrap-datepicker.readthedocs.io/en/latest/
*/
const palettes = [ "default", "default-inv", "div-BrBG", "div-BrBG-inv", "div-BuRd", "div-BuRd-inv", "div-BuRd2", "div-BuRd2-inv", "div-PRGn", "div-PRGn-inv", "div-PiYG", "div-PiYG-inv", "div-PuOr", "div-PuOr-inv", "div-RdBu", "div-RdBu-inv", "div-RdGy", "div-RdGy-inv", "div-RdYlBu", "div-RdYlBu-inv", "div-RdYlGn", "div-RdYlGn-inv", "div-Spectral", "div-Spectral-inv", "psu-inferno", "psu-inferno-inv", "psu-magma", "psu-magma-inv", "psu-plasma", "psu-plasma-inv", "psu-viridis", "psu-viridis-inv", "seq-BkBu", "seq-BkBu-inv", "seq-BkGn", "seq-BkGn-inv", "seq-BkRd", "seq-BkRd-inv", "seq-BkYl", "seq-BkYl-inv", "seq-BlueHeat", "seq-BlueHeat-inv", "seq-Blues", "seq-Blues-inv", "seq-BuGn", "seq-BuGn-inv", "seq-BuPu", "seq-BuPu-inv", "seq-BuYl", "seq-BuYl-inv", "seq-GnBu", "seq-GnBu-inv", "seq-Greens", "seq-Greens-inv", "seq-Greys", "seq-Greys-inv", "seq-GreysRev", "seq-GreysRev-inv", "seq-Heat", "seq-Heat-inv", "seq-OrRd", "seq-OrRd-inv", "seq-Oranges", "seq-Oranges-inv", "seq-PuBu", "seq-PuBu-inv", "seq-PuBuGn", "seq-PuBuGn-inv", "seq-PuRd", "seq-PuRd-inv", "seq-Purples", "seq-Purples-inv", "seq-RdPu", "seq-RdPu-inv", "seq-Reds", "seq-Reds-inv", "seq-YlGn", "seq-YlGn-inv", "seq-YlGnBu", "seq-YlGnBu-inv", "seq-YlOrBr", "seq-YlOrBr-inv", "seq-YlOrRd", "seq-YlOrRd-inv", "seq-cubeYF", "seq-cubeYF-inv", "x-Ncview", "x-Ncview-inv", "x-Occam", "x-Occam-inv", "x-Rainbow", "x-Rainbow-inv", "x-Sst", "x-Sst-inv",]

const palette_and_min_max = {
    //  hurs is %
    'hurs': {
        'style': 'default-scalar/seq-Heat',
        'valueRange': '0, 100',
    },
    'pr': {
        'style': 'default-scalar/seq-Heat',
        'valueRange': '0, 200',
    },
    'rsds': {
        'style': 'default-scalar/seq-Heat',
        'valueRange': '0, 10000',
    },
    'sfcWind': {
        'style': 'default-scalar/seq-Heat',
        'valueRange': '0, 30',
    },
    'tas': {
        'style': 'default-scalar/seq-Heat',
        'valueRange': '-25, 40',
    },
    'tasmax': {
        'style': 'default-scalar/seq-Heat',
        'valueRange': '-25, 42',
    },
    'tasmin': {
        'style': 'default-scalar/seq-Heat',
        'valueRange': '-30, 40',
    },
};

const styles = ['default-scalar/seq-Heat', 'colored_contours/default', 'contours', 'raster/default'];
var style = 'raster/psu-inferno-inv';

var lowerRangeinput = document.getElementById('lowerRange');
var upperRangeinput = document.getElementById('upperRange');
var styleSelector = document.getElementById('styleSelector');

palettes.forEach(palette => {
    var option = document.createElement("option");
    option.text = palette;
    styleSelector.add(option);
});

styleSelector.addEventListener('change', (event) => {
    console.log('event', event.target.value);
    style = 'raster/' + event.target.value;
    console.log('style', style);
});
// let timeDimensionLayer;

// Format the yyyy-mm-dd date to dd/mm/yyyy
const dateFormatter = function(date) {
    var components = date.split('-');
    var formattedDate = components[2] + '/' + components[1] + '/' + components[0];
    console.log('Formatted Date: ', date, formattedDate)
    return formattedDate;
};

// initialize the datepickers with the start and end date of the dataset
const formatDatePicker = function(startDate, endDate) {
    $('.input-daterange').datepicker({
        language: 'de-DE',
        format: "dd/mm/yyyy",
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
var attribution;
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
    params = {
        'netCdf': netCdf,
        'variable': variable,
        'startDate': startDate,
        'endDate': endDate,
        'style': style,
        'attribution': attribution,
    };
    console.log('params', params);
    initializeWms(params);
    map.timeDimension.setCurrentTimeIndex(0);
})



document.addEventListener('DOMContentLoaded', function() {

    // Get the meatdata of the chosen dataset and update the variable selector
    datasetSelector.addEventListener('change', (event) => {
        $('.input-daterange').datepicker('destroy');
        netcdfVariableSelector.innerHTML = '';
        
        const dataset = event.target.value;
        console.log('dataset', dataset);
        fetch(`/Thredds/get_ncml_metadata/${dataset}`)
            .then(response => response.text())
            .then(data => {
                console.log('data', data);
                var data_json = JSON.parse(data);
                console.log('data_json', data_json);
                // const text = data_json.global_attributes['title'] + data_json.global_attributes.creator_name + data_json.time_coverage_start + data_json.time_coverage_end;
                // var formattedStartDate = dateFormatter(data_json.time_coverage_start);
                // var formattedEndDate = dateFormatter(data_json.time_coverage_end);
                var formattedStartDate = dateFormatter(data_json.global_attributes.time_coverage_start_ymd);
                var formattedEndDate = dateFormatter(data_json.global_attributes.time_coverage_end_ymd);
                // formatDatePicker(data_json.time_coverage_start, data_json.time_coverage_end)
                formatDatePicker(formattedStartDate, formattedEndDate)

                Object.keys(data_json.variables).forEach(variable => {
                    console.log(variable);
                    var option = document.createElement("option");
                                    option.text = variable;
                                    netcdfVariableSelector.add(option);
                });
                var selectedVariable = netcdfVariableSelector.value;
                lowerRangeinput.value = data_json.variables[selectedVariable].attributes.minimum_value;
                upperRangeinput.value = data_json.variables[selectedVariable].attributes.maximum_value;
                // console.log('lowerRangeinput', data_json.variables[selectedVariable].attributes.minimum_value);

                attribution = data_json.variables[selectedVariable].attributes.long_name;

                // data_json.variable.forEach(variable => {
                //     var option = document.createElement("option");
                //     option.text = variable;
                //     netcdfVariableSelector.add(option);
                // });

                return data;
            })
        // initializeWms(dataset, style);
    }); 
});

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
        center: [51.0, 10.0]
    });

    return map;
};

// Function to create WMS layer
function createWMSLayer(wmsUrl, layerName, colorscaleRange, style, attribution) {

    return L.tileLayer.wms(wmsUrl, {
        layers: layerName,
        version: "1.3.0",
        format: 'image/png',
        transparent: true,
        attribution: attribution,
        tileSize: 1024,
        transparent: true,
        colorscalerange: palette_and_min_max[layerName].valueRange,
        abovemaxcolor: "extend",
        belowmincolor: "extend",
        numcolorbands: 100,
        styles: style,
    });
};
function createTimeDimension(params) {
    return new L.timeDimension({
    availableTimes: params.availableTimes,
    currentTimeIndex: 0,});
};


// Function to create TimeDimension layer
function createTimeDimensionLayer(wmsLayer,style) {
    // const timeDimensionUrl = `${wmsUrl}?service=WMS&request=GetCapabilities&version=1.3.0`;
    const layer = L.timeDimension.layer.wms(wmsLayer, {
        wmsVersion: "1.3.0",
        updateTimeDimension: true,
        updateTimeDimensionMode: 'replace',
        cache: 24,
        styles: style,
    });
    
    // Return a promise that resolves when the layer is added to the map
    return new Promise(resolve => {
        layer.on('added', () => resolve(layer));
    });
};
// L.control.timeDimension({}).addTo(map);

// Function to create legend control
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
map.timeDimension.on('availabletimeschanged', function() {
    console.log('timeloading', );
        map.timeDimension.setCurrentTimeIndex(0);});


let timeDimensionControl;
let timeDimension;
let wmsLayer;
let timeDimensionWmsLayer;
let legendControl;


async function initializeWms(params) {
    console.log('InitializeWms params', params);
    try {
        // map.timeDimension.unregisterSyncedLayer(timeDimensionWmsLayer);
        console.log('timeDimensionWmsLayer unregistered');
    } catch (error) {console.log('Deleting old time dimension items failed')  }
     try {
        map.removeLayer(timeDimensionWmsLayer);
        console.log('timeDimensionWmsLayer removed');
     } catch (error) {console.log('Deleting old time dimension items failed')  }

    const wmsUrl = `/Thredds/wms/${params.netCdf}`;
    const capabilitiesurl = `/Thredds/get_wms_capabilities/${params.netCdf}`;
    
    const layerName = params.variable;
    const colorscaleRange = palette_and_min_max[layerName].valueRange;
    const attribution = 'DWD hindcast | precipitation_flux';

    
    const legendUrl = `${wmsUrl}?request=GetLegendGraphic&PALETTE=default&LAYERS=${params.variable}&transparent=TRUE&&colorscalerange=${colorscaleRange}&numcolorbands=100&styles=${style}`;

    legendControl = createLegendControl(legendUrl);
    legendControl.addTo(map);
    // the actual WMS layer is created with the selected parameters
    wmsLayer = createWMSLayer(wmsUrl, params.variable, colorscaleRange, params.style, attribution);
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
