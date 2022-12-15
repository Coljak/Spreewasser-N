
console.log('map.js loaded!')

// map class initialize 
var map = L.map('map').setView([38.8610, 71.2761], 7);
map.zoomControl.setPosition('topright');

// adding osm tilelayer 
var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var watercolorMap = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}', {
    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    subdomains: 'abcd',
    minZoom: 1,
    maxZoom: 16,
    ext: 'jpg'
});

var st = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}{r}.{ext}', {
    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    subdomains: 'abcd',
    minZoom: 0,
    maxZoom: 20,
    ext: 'png'
});

//Addming marker in the center of map
var singleMarker = L.marker([38.8610, 71.2761])
    .bindPopup('A pretty CSS3 popup.<br> Easily customizable.')
    .openPopup();

//Map coordinate display
map.on('mousemover', function (e) {
    $('.coordinate').html(`Lat: ${e.latlng.lat} Lng: ${e.latlng.lng}`)
})

//add map scale
L.control.scale().addTo(map);



//Geojson load
var marker = L.markerClusterGroup();
var taji = L.geoJSON(data, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup(feature.properties.name)
    }
});
taji.addTo(marker);
marker.addTo(map);


//Leaflet layer control
var baseMaps = {
    'OSM': osm,
    'Water Color Map': watercolorMap,
    'Stamen Toner': st
}

var overlayMaps = {
    'GeoJSON Markers': marker,
    'Single Marker': singleMarker
}

L.control.layers(baseMaps, overlayMaps, { collapsed: false, position: 'topleft' }).addTo(map);







var popup = L.popup();
var marker = L.marker(52.0825, 13.8).addTo(map);

function onMapClickPopup(e){
    marker.setLatLng(e.latlng);
    popup
    .setLatLng(e.latlng)
    .setContent("You clicked at " + e.latlng.toString())
    .openOn(generalMap);
}

generalMap.on('click', onMapClickPopup);