//Full screen map view
var mapId = document.getElementById('map');
console.log('typeof(mapId)')
console.log(typeof(mapId))
function fullScreenView() {
    if (document.fullscreenElement) {
        document.exitFullscreen()
    } else {
        mapId.requestFullscreen();
    }
}

//Leaflet browser print function
L.control.browserPrint({ position: 'topright' }).addTo(map);

//Leaflet search
L.Control.geocoder().addTo(map);

// L.control.sidebar('sidebar',{
//     closeButton: true,
//     position: 'left'
//   } ).addTo(map);

var drawnItems = L.featureGroup().addTo(map)
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    draw: {
        position: 'topright',
        circle: false,
        polyline: false,
        polygon: {
            title: 'Draw some polygon!',
            allowIntersection: false,
            drawError: {
                color: '#b00b09',
                timeout: 1000
            },
            shapeOptions: {
                color: '#bada55'
            }
        },
        
    },
    edit: {
      featureGroup: drawnItems
    }
    
}).addTo(map);




//zoom to layer
$('.zoom-to-layer').click(function () {
    map.setView([38.8610, 71.2761], 7)
})