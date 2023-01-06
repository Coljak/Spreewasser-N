
console.log('map.js loaded!')

const map = document.getElementById('map')
const SWNOverlay = L.geoJson();

function main_map_init (map, options) {

    
    // Download GeoJSON via Ajax
    $.getJSON(dataurl, function (data) {
        // Add GeoJSON layer
        L.geoJson(data).addTo(map);
    });

}

pilotRegion.addTo(map)
$.getJSON("{% url 'data' %}", function (data) {
    layer.addData(data);
    });

var sidebar = L.control.sidebar('sidebar', {
    closeButton: true,
    position: 'left'
}).addTo(map);