// The Animated layer with TimeDimension and WMS layer is assigned at click of the load button

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
        // defaultViewDate: { year: 2015, month: 0, day: 22 }
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
    params = {
        'netCdf': netCdf,
        'variable': variable,
        'startDate': startDate,
        'endDate': endDate,
        'style': 'raster/default',
    };
    console.log('params', params);
    initializeWms(params);
    
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
                var formattedStartDate = dateFormatter(data_json.time_coverage_start);
                var formattedEndDate = dateFormatter(data_json.time_coverage_end);
                // formatDatePicker(data_json.time_coverage_start, data_json.time_coverage_end)
                formatDatePicker(formattedStartDate, formattedEndDate)

                data_json.variable.forEach(variable => {
                    var option = document.createElement("option");
                    option.text = variable;
                    netcdfVariableSelector.add(option);
                });

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
        colorscalerange: colorscaleRange,
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
function createTimeDimensionLayer(wmsLayer, wmsUrl, style) {
    const timeDimensionUrl = `${wmsUrl}?service=WMS&request=GetCapabilities&version=1.3.0`;
    return L.timeDimension.layer.wms(wmsLayer, {
        wmsVersion: "1.3.0",
        updateTimeDimension: true,
        updateTimeDimensionMode: 'replace',
        cache: 24,
        styles: style,
        // timeDimensionUrl: timeDimensionUrl,
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
// const dataset = 'zalf_pr_amber_2009_v1-0_cf_v4.nc';
const styles = ['default-scalar/seq-Heat', 'colored_contours/default', 'contours', 'raster/default'];
const style = styles[3];

let timeDimensionControl;
let timeDimension;
let wmsLayer;
let timeDimensionWmsLayer;
let legendControl;


function initializeWms(params) {
    console.log('InitializeWms params', params);
    try {
        map.timeDimension.unregisterSyncedLayer(timeDimensionWmsLayer);
        console.log('timeDimensionWmsLayer unregistered');
    } catch (error) {console.log('Deleting old time dimension items failed')  }
     try {
        map.removeLayer(timeDimensionWmsLayer);
        console.log('timeDimensionWmsLayer removed');
     } catch (error) {console.log('Deleting old time dimension items failed')  }

    var dataset = params.netCdf;
    var style = params.style;
    var selectedStartDate = params.startDate;
    var selectedEndDate = params.endDate;
    var layerName = params.variable;

    const wmsUrl = `/Thredds/wms/${dataset}`;
    const capabilitiesurl = `/Thredds/get_wms_capabilities/${dataset}`;
    
    const colorLower = 0;
    const colorUpper = 15;
    const colorscaleRange = `${colorLower},${colorUpper}`;
    const attribution = 'DWD hindcast | precipitation_flux';

    
    const legendUrl = `${wmsUrl}?request=GetLegendGraphic&PALETTE=default&LAYERS=${layerName}&transparent=TRUE&&colorscalerange=${colorscaleRange}&numcolorbands=100&styles=${style}`;

    legendControl = createLegendControl(legendUrl);
    legendControl.addTo(map);

    wmsLayer = createWMSLayer(wmsUrl, layerName, colorscaleRange, style, attribution);
    wmsLayer.addTo(map);

    timeDimensionWmsLayer = L.timeDimension.layer.wms(wmsLayer, {
        wmsVersion: "1.3.0",
        updateTimeDimension: true,
        updateTimeDimensionMode: 'replace',
        cache: 24,
        styles: style,
    });
    
    timeDimensionWmsLayer.addTo(map);
    map.timeDimension.setCurrentTimeIndex(0);
    
};
