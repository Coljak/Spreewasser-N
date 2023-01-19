console.log('user_dashboard.js is loaded!')

const osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const osm = L.tileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib})


const map = new L.Map('map', {
  layers: [osm],
  center: new L.LatLng(-37.7772, 175.2756), 
  zoom: 15,
});



// Leaflet Control top-right
// https://github.com/brunob/leaflet.fullscreen
const fullScreenControl = new L.Control.FullScreen({
  position: 'topright'
})
map.addControl(fullScreenControl)

// Leaflet Control bottom-right
//https://github.com/Leaflet/Leaflet.draw/tree/develop/docs
var drawnItems = L.featureGroup();
map.addLayer(drawnItems);

const GeocoderControl = new L.Control.geocoder({
  position: 'topright'
})
map.addControl(GeocoderControl)

var drawControl = new L.Control.Draw({
  position: 'topright',
  draw: {
        circle: false,
        polyline: false,
        
        
    },
    edit: {
      featureGroup: drawnItems
    }
  
});

map.addControl(drawControl)

// Leaflet Control bottom-right
// Leaflet Control top-left
const sidebarLeft = L.control.sidebar('sidebar',{
  closeButton: true,
  position: 'left'
}).addTo(map);

//add map scale
const mapScale = new L.control.scale({
  position: 'bottomright'
}).addTo(map);