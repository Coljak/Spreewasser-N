console.log('map.js loaded!')

var popup = L.popup();
var marker = L.marker(52.0825, 13.8).addTo(generalMap);

function onMapClickPopup(e){
    marker.setLatLng(e.latlng);
    popup
    .setLatLng(e.latlng)
    .setContent("You clicked at " + e.latlng.toString())
    .openOn(generalMap);
}

generalMap.on('click', onMapClickPopup);