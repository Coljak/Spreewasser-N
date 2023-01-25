console.log('user_dashboard.js is loaded!')

const osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const osm = L.tileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib})

const satelliteUrl = 'http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
const satelliteAttrib = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
const satellite = L.tileLayer(satelliteUrl, {maxZoom: 18, attribution: satelliteAttrib})

const topoUrl = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png'
const topoAttrib = 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
const topo = L.tileLayer(topoUrl, {maxZoom: 18, attribution: topoAttrib})

const baseMaps = {
  'Open Street Maps': osm,
  'Satellit': satellite,
  'Topomap': topo
}



const map = new L.Map('map', {
  layers: [osm],
  center: new L.LatLng(52.338145830363914, 13.85877631507592 ), 
  zoom: 8
 
});



// Leaflet Control bottom-right
//https://github.com/Leaflet/Leaflet.draw/tree/develop/docs
var drawnItems = L.featureGroup();
map.addLayer(drawnItems);



// Leaflet Control top-right
// https://github.com/brunob/leaflet.fullscreen
const fullScreenControl = new L.Control.FullScreen({
  position: 'topright'
})
map.addControl(fullScreenControl)



const GeocoderControl = new L.Control.geocoder({
  position: 'topright'
})
map.addControl(GeocoderControl)

var drawControl = new L.Control.Draw({
  position: 'topright',
  draw: {
        circlemarker: false,
        polyline: false,
        polygon: {
          allowIntersection: false,
          showArea: true
      }
        
    },
    edit: {
      featureGroup: drawnItems
    }
  
});

map.addControl(drawControl)



map.on(L.Draw.Event.CREATED, function (event) {
  
  let layer = event.layer;
  drawnItems.addLayer(layer);

  let type = event.layerType;
  let shape = layer.toGeoJSON()
  let shape_for_db = JSON.stringify(shape)
  console.log(typeof shape_for_db)
  
});



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


L.control.layers({
  'osm': osm.addTo(map),
  "Satellit": satellite,
  'Topografische Karte': topo
}, { 'Acker': drawnItems }, { position: 'topright', collapsed: false }).addTo(map);

const layerSwitcher = L.control.layers(baseMaps).addTo(map);

const layerSwitcherObject = layerSwitcher.getContainer();
const sidebarLayerDiv = document.getElementById('baselayer-01')

console.log(layerSwitcherObject)
// const appendLayerControl = (child) => {
//   appendLayerControl
// }
// function setParent(el, newParent) {
  
//     console.log(el.children)
  
  
// }

// setParent(layerSwitcherObject, sidebarLayerDiv)
// Sidebar
// // load a shape from DB/´
const pilotGeojson = L.geoJSON(pilotRegion).addTo(map);




// SIDEBAR 
// const projectRegionSwitch = document.getElementById('projectRegionSwitch')


  var checkbox = document.getElementById('projectRegionSwitch');
  // const switchToggle = () => {
  //   if (checkbox.checked) {
  //     // do this
      
  //     console.log('Checked');
  //   } else {
  //     // do that
  //     // pilotGeojson.remove()
  //     console.log('Not checked');
  //   }
  // }

  checkbox.addEventListener('change', function (){
    if (checkbox.checked) {
      // do this
      pilotGeojson.addTo(map)
      console.log('Checked');
    } else {
      // do that
      pilotGeojson.remove()
      console.log('Not checked');
    }
  });

  