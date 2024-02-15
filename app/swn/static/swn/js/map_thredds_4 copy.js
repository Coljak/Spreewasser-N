const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib });



const dataset = 'zalf_pr_amber_2009_v1-0_cf_v4.nc'

var map = L.map('map', {
    zoom: 5,
    center: [38.705, 1.15],
    layers: [osm],
    timeDimension: true,
    // timeDimensionOptions: {
    //     timeInterval: "2009-12-01/2009-12-31",
    //     period: "P1D",
        
    // },
    timeDimensionControl: true,
    center: [51.0, 10.0]
});


var wmsUrl = `/Timelapse_test_django/passthrough/wms/${dataset}`;

// Extracted information from GetCapabilities response
const layerName = 'pr';
const styles = ['default-scalar/seq-Heat', 'colored_contours/default', 'contours', 'raster/default', ];
var style = styles[3];

console.log('timeDimensionUrl', timeDimensionUrl)


//  TODO: the colorscalerange needs to be set from min and max values of the netCDF's variable
var colorLower = 0;
var colorUpper = 15;
var colorscaleRange = `${colorLower},${colorUpper}`

// TODO: the attribution needs to be set by the standard_name or description of the netCDF
var attribution = 'DWD hindcast | precipitation_flux'

// WMS layer
var wmsLayer = L.tileLayer.wms(wmsUrl, {
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

const timeDimensionUrl = `${wmsUrl}?service=WMS&request=GetCapabilities&version=1.3.0`;
// TimeDimension layer
var tdWmsLayer = L.timeDimension.layer.wms(wmsLayer, {
    wmsVersion: "1.3.0",
    updateTimeDimension: true,
    // availableTimes: availableTimes,
    cache: 24,
    styles: style,
    timeDimensionUrl: timeDimensionUrl,
    // legendUrl: legendUrl,   
});

var availableTimes = tdWmsLayer._availableTimes 
console.log('availableTimes', availableTimes)
var timeDimension = map.timeDimension;
timeDimension.setLowerLimitIndex(2);
timeDimension.setCurrentTimeIndex(0);

const legendUrl = `${wmsUrl}?request=GetLegendGraphic&PALETTE=default&LAYERS=${layerName}&transparent=TRUE&&colorscalerange=${colorscaleRange}&numcolorbands=100&styles=${style}`;
    
console.log('legendUrl', legendUrl)

var tdWmsLegend = L.control({
    position: 'topright',
   
});
tdWmsLegend.onAdd = function(map) {
    var src = legendUrl;
    var div = L.DomUtil.create('div', 'info legend leaflet-bar');
    div.innerHTML +='<img src="' + src + '" alt="legend" height="200rem">';
    return div;
   
};

tdWmsLegend.addTo(map);
tdWmsLayer.addTo(map);

// Get the TimeDimension object from the map

// 1230768000000 
// 1260835200000

// // Set the time interval
// timeDimension.setAvailableTimes("2009-12-01T00:00:00Z", "2009-12-31T00:00:00Z");
// console.log('timeDimension.getAvailableTimes()', timeDimension.getAvailableTimes())
// timeDimension.setPeriod("P1D");
// // timeDimension.setCurrentTime("2009-12-01");


// // // Set the period
// // timeDimension.setCurrentTime(new Date("2009-12-01T00:00:00Z"));

// // Set the current time
// timeDimension.setCurrentTime("2009-12-01T00:00:00Z");

// Add TimeDimension Layer to the map

// map.on('overlayadd', function(eventLayer) {
//     if (eventLayer.name == 'AVISO - Sea surface height above geoid') {
//         heigthLegend.addTo(this);
//     } else if (eventLayer.name == 'AVISO - Surface geostrophic sea water velocity') {
//         velocityLegend.addTo(this);
//     }
// });

// map.on('overlayremove', function(eventLayer) {
//     if (eventLayer.name == 'AVISO - Sea surface height above geoid') {
//         map.removeControl(heigthLegend);
//     } else if (eventLayer.name == 'AVISO - Surface geostrophic sea water velocity') {
//         map.removeControl(velocityLegend);
//     }
// });


// NOTES
//  map.timeDimensionControl.remove()  <--> map.timeDimensionControl.addTo(map)
//  currentTime: Date.parse("2020-09-25T12:00:00Z")

// AI generated notes
// 1. The timeDimensionUrl is the url of the WMS service with the GetCapabilities request
// 2. The timeDimensionUrl is used to get the available times and the legendUrl
// 3. The availableTimes is an array of the available times in the netCDF file
// 4. The timeDimension.setAvailableTimes() is used to set the time interval
// 5. The timeDimension.setPeriod() is used to set the period
// 6. The timeDimension.setCurrentTime() is used to set the current time
// 7. The timeDimension.setLowerLimitIndex() is used to set the lower limit index
// 8. The timeDimension.setCurrentTimeIndex() is used to set the current time index
// 9. The timeDimension._currentTimeIndex is used to get the current time index
// 10. The timeDimension._availableTimes is used to get the available times
// 11. The timeDimension._currentTime is used to get the current time
// 12. The timeDimension._currentTimeIndex is used to get the current time index