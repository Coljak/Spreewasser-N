const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib =
  '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib });
// example.js


var map = L.map('map', {
    zoom: 5,
    center: [38.705, 1.15],
    layers: [osm],
    timeDimension: true,
    timeDimensionOptions: {
        timeInterval: "2009-12-01/2009-12-31",
        period: "P1D",
        
    },
    timeDimensionControl: true,
    center: [51.0, 10.0]
});
// var wmsUrl = "http://localhost:8088/thredds/wms/testAll/data/netcdf4_test_v3.nc";
var wmsUrl = "/Timelapse_test_django/passthrough/wms/zalf_pr_amber_2009_v1-0_cf_v4.nc";

// Extracted information from GetCapabilities response
const layerName = 'pr';
const styles = ['default-scalar/seq-Heat', 'colored_contours/default', 'contours', 'raster/default'];
const timeDimensionUrl = `${wmsUrl}?service=WMS&request=GetCapabilities&version=1.3.0`;
console.log('timeDimensionUrl', timeDimensionUrl)
const legendUrl = `${wmsUrl}?REQUEST=GetLegendGraphic&PALETTE=default&LAYERS=${layerName}`;


// WMS layer
var wmsLayer = L.tileLayer.wms(wmsUrl, {
    layers: layerName,
    version: "1.3.0",
    format: 'image/png',
    transparent: true,
    attribution: 'DWD hindcast | precipitation_flux',
    tileSize: 1024,
    transparent: true,
    colorscalerange: '0,15',
    abovemaxcolor: "extend",
    belowmincolor: "extend",
    numcolorbands: 100,
    styles: styles[3],
});

// TimeDimension layer
var tdWmsLayer = L.timeDimension.layer.wms(wmsLayer, {
    wmsVersion: "1.3.0",
    updateTimeDimension: true,
    // availableTimes: availableTimes,
    cache: 24,
    styles: styles,
    timeDimensionUrl: timeDimensionUrl,
    legendUrl: legendUrl,   
});

// Add TimeDimension Layer to the map
tdWmsLayer.addTo(map);

tdWmsLayer.addTo(map);